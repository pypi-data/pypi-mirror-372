from dataclasses import dataclass
import asyncio
from .reducers import get_reducer_manager
import inspect
from collections import defaultdict
from typing import Callable, Iterable, Optional, Dict, List, Set, Any, Tuple
import math
import itertools
import bisect


ninf:float = -math.inf

class Behavior:
    """Named constants describing how a hook behaves.

    Attributes:
        DEFAULT: Run only when emitted.
        ONESHOT: Run once, then remove itself after a successful call.
        LOOP: Run on a fixed interval once loops are started.
    """
    DEFAULT = "default"
    ONESHOT = "oneshot"
    LOOP = "loop"

@dataclass()
class Entry:
    """Registered hook entry.

    - `hook_name`: Primary category this entry listens to, for example "on_msg".
    - `tags`: Secondary labels used for filtering, stored as a lowercase frozenset.
    - `priority`: Lower values run earlier within the same hook_name.
    - `seq`: Tiebreaker for identical priorities, assigned in increasing order.
    - `behavior`: One of Behavior.DEFAULT, Behavior.ONESHOT, Behavior.LOOP.
    - `interval`: Seconds between runs for LOOP behavior, otherwise None.
    - `enabled`: Whether this entry is active. Disabled entries are skipped.
    - `callback`: The callable to invoke. May be sync or async.
    - `on_fail`: Optional error handler called with the raised exception.
"""
    
    # EMIT/CALLER HELPERS
    hook_name:str # Required, primary bucket (ex: "on_msg")
    tags:frozenset[str] # Optional, secondary bucket(s) (ex: "on_connect" for on_msg name)

    #SORTING HELPERS
    priority:float #lower number runs first
    seq:int # auto increment priority tie breaker

    #BEHAVIOR
    behavior:str #Behavior.DEFAULT | ONESHOT | LOOP
    interval:float|None # Used only when behavior == loop
    enabled:bool # toggle without removal

    #CALLBACKS
    callback:Callable # Users function
    on_fail:Callable|None #error handler for entry

    #HANDLERS:
    token:object # handler for removing and inspecting

@dataclass
class HookResult:
    """Per-callback execution result returned by gather().

    - `entry`: The Entry that was invoked.
    - `value`: The return value from the callback, if any.
    - `ok`: True if the callback completed without raising.
    - `error`: The exception instance if the callback raised, else None.
    - `elapsed_ms`: Execution time in milliseconds for this callback only.
"""
    entry:Entry
    value:Any
    ok:bool
    error:Optional[BaseException]
    elapsed_ms:float

@dataclass
class HookMetrics:
    """Timing signal for metrics sinks.

    - `hook_name`: Name emitted by the caller, for example "on_msg".
    - `entry`: The Entry that was invoked.
    - `elapsed_ms`: Execution time in milliseconds.
    - `ok`: True if the callback completed without raising.
"""

    hook_name:str
    entry: Entry
    elapsed_ms:float
    ok:bool

class Storage:
    """Internal indexes for registered hooks.

    Holds the ordered buckets per hook_name, a token→Entry map, a tag index,
    and loop task references. All mutation happens through Hookedin methods.
    """
    def __init__(self) -> None:
        """Initialize empty indexes for names, tokens, tags, and loop tasks."""
        # Ordered view per name. Each list is always sorted by (priority, seq).
        self.hooks_by_name: Dict[str, List[Entry]] = defaultdict(list)

        # Lifecycle control. O(1) lookup by token.
        self.entry_by_token: Dict[object, Entry] = {}

        # Optional speed-up for tagged emits: tags_index[name][tag] -> set(tokens)
        self.tags_index: Dict[str, Dict[str, Set[object]]] = defaultdict(lambda: defaultdict(set))

        # Loop tasks map (token -> task handle). Populated only for behavior=LOOP when started.
        self.loop_tasks: Dict[object, Any] = {}

class Hookedin:
    """Create a new hook manager.

    Sets up internal storage, a sequence counter for stable ordering,
    and a reducer manager used by parallel trigger() calls.
    """
    def __init__(self) -> None:
        self.storage:Storage = Storage()
        self._seq_counter:int = itertools.count(1)
        self._started:bool = False
        self._metrics_sink: Optional[Callable[[HookMetrics],None]] = None
        self.ReduceManager = get_reducer_manager()
    
    # <<========================================= PUBLIC API ========================================================>>

    # ==> REGISTRATION <==
    def on(self,hook_name:str,*,tags:Optional[Iterable[str]]=None,priority:float=0,
           behavior:str = Behavior.DEFAULT, interval:Optional[float]=None,on_fail:Optional[Callable]=None):
        """Decorator to register a function as a hook.

        Usage:
            hooks = Hookedin()
            @hooks.on("on_msg", tags=["auth"], priority=-10)
            async def my_handler(ctx): ...

        Args:
            hook_name: Primary channel to register under.
            tags: Optional iterable of tag strings for filtering.
            priority: Lower numbers run earlier for the same hook_name.
            behavior: DEFAULT, ONESHOT, or LOOP.
            interval: Interval in seconds for LOOP behavior.
            on_fail: Optional error handler that receives the exception.

        Returns:
            The original function, unchanged. A token is attached to it as
            `__hookedin_token__` for later lookups and removal.
        """
        self._validate_registration(hook_name,tags,behavior,interval)
        tags_fs = self._normalize_tags(tags)

        def decorator(fn:Callable):
            entry, token = self._register(
                callback = fn,
                hook_name = hook_name,
                tags = tags_fs,
                priority = priority,
                behavior = behavior,
                interval = interval,
                on_fail = on_fail,
            )
            try:
                setattr(fn, "__hookedin_token__",token)
            except Exception:
                pass
            return fn
        return decorator
    
    def add(self, callback:Callable, hook_name:str, *,tags:Optional[Iterable[str]]=None,priority:float=0,
           behavior:str = Behavior.DEFAULT, interval:Optional[float]=None,on_fail:Optional[Callable]=None):
        """Register a callback programmatically.

        Args:
            callback: Callable to register. Can be sync or async.
            hook_name: Primary channel to register under.
            tags: Optional iterable of tag strings for filtering.
            priority: Lower numbers run earlier for the same hook_name.
            behavior: DEFAULT, ONESHOT, or LOOP.
            interval: Interval in seconds for LOOP behavior.
            on_fail: Optional error handler that receives the exception.

        Returns:
            An opaque token object that identifies this registration.

        Raises:
            ValueError: If LOOP behavior is selected without a positive interval.
        """
        self._validate_registration(hook_name,tags,behavior,interval)
        tags_fs = self._normalize_tags(tags)
        _entry, token = self._register(
            callback = callback,
            hook_name = hook_name,
            tags = tags_fs,
            priority = priority,
            behavior = behavior,
            interval = interval,
            on_fail = on_fail
        )
        return token
    
    # ==> EMITS <==
    # Trigger: run hooks, ignoring return values | Gather: run hooks, returning return values

    async def fire(self,hook_name:str,*,payload:Any,tags:Optional[Set[str]]=None, parallel:bool=False,strict:bool=False,
                   include_untagged:bool=False,unique_inputs:Optional[bool]=None,**kwargs
                   ) -> None:
        """Emit a hook and ignore returns.

        This runs matching handlers either sequentially or in parallel and does not
        return a value to the caller. Errors are handled by on_fail or raised if
        strict=True.

        Args:
            hook_name: Name to emit.
            payload: Object passed to each handler as the first argument or 'ctx'.
            tags: Optional filter set. Only entries that include all tags will run.
            parallel: If True, run handlers concurrently with isolated inputs.
            strict: If True, re-raise exceptions to the caller.
            include_untagged: If True and tags is provided, include untagged entries.
            unique_inputs: If None, defaults to parallel. When True, each handler
                receives a shallow-copied payload to avoid in-place collisions.
            **kwargs: Extra keyword args forwarded to handlers.

        Returns:
            None.
        """

        _results, _final_payload = await self._run(
            mode = "fire",
            hook_name=hook_name,
            tags=tags,
            parallel=parallel,
            strict=strict,
            include_untagged=include_untagged,
            unique_inputs=unique_inputs,
            payload=payload,
            extra_kwargs=kwargs,
            reducer=None
        )
        return None
        

    async def trigger(self, hook_name:str, *, payload:Any, tags:Optional[Set[str]]=None, include_untagged:bool=False,
                      parallel:bool=False, unique_inputs:Optional[bool]=None, strict:bool=False, 
                      reducer:Optional[Callable[[dict,List[dict]],dict]|str]=None, **kwargs
                      ) -> Any:
        """Emit a hook and fold results into a final payload.

        Sequential:
            Handlers run in order and may mutate the same payload object. For non-dict
            payloads, a non-None return value replaces the working payload.

        Parallel:
            Handlers run concurrently with isolated inputs. Dict returns are merged
            using the selected reducer.

        Args:
            hook_name: Name to emit.
            payload: Initial payload object.
            tags: Optional filter set.
            parallel: If True, run handlers concurrently with isolated inputs.
            strict: If True, re-raise exceptions from handlers.
            include_untagged: If True and tags is provided, include untagged entries.
            unique_inputs: If None, defaults to parallel. See fire() for details.
            reducer: Reducer strategy for merging dict returns in parallel mode.
                May be a callable or a registered reducer name.
            **kwargs: Extra keyword args forwarded to handlers.

        Returns:
            The final payload after chaining (sequential) or merge (parallel).
        """

        results, final_payload = await self._run(
            mode = "trigger",
            hook_name=hook_name,
            tags=tags,
            parallel=parallel,
            strict=strict,
            include_untagged=include_untagged,
            unique_inputs=unique_inputs,
            payload=payload,
            reducer=reducer,
            extra_kwargs=kwargs,
        )
        return final_payload
        
    async def gather(self, hook_name:str, *, payload:Any, tags:Optional[Set[str]]=None, parallel:bool=False, strict:bool=False,
                     include_untagged:bool=False, unique_inputs:Optional[bool]=None, **kwargs
                     ) -> List[HookResult]:
        """Emit a hook and collect per-callback results.

        Runs sequentially or in parallel and returns a list of HookResult records.
        The final payload is discarded in this mode.

        Args:
            hook_name: Name to emit.
            payload: Initial payload object given to each handler.
            tags: Optional filter set.
            parallel: If True, run handlers concurrently with isolated inputs.
            strict: If True, re-raise exceptions from handlers.
            include_untagged: If True and tags is provided, include untagged entries.
            unique_inputs: If None, defaults to parallel.
            **kwargs: Extra keyword args forwarded to handlers.

        Returns:
            A list of HookResult objects in execution order.
        """

        results, _final_payload = await self._run(
            mode = "gather",
            hook_name=hook_name,
            tags=tags,
            parallel=parallel,
            strict=strict,
            include_untagged=include_untagged,
            unique_inputs=unique_inputs,
            payload=payload,
            extra_kwargs=kwargs,
            reducer=None
        )
        return results
    
    # ==> Helpers <==
    def enable(self, token:object, *, _entry:Entry|None=None):
        """Enable a previously registered entry.

        Args:
            token: The token returned from add() or stored on a decorated function.
            _entry: Internal override for performance, do not use directly.

        Returns:
            True if the entry was enabled or already enabled, False if not found.
        """
        entry = _entry
        if not isinstance(_entry,Entry):
            entry = self.storage.entry_by_token.get(token)
            if not entry:
                return False
        entry.enabled = True
        if entry.behavior == Behavior.LOOP and self._started and token not in self.storage.loop_tasks:
            self.storage.loop_tasks[token] = self._create_loop_task(entry)
        return True
    
    def disable(self, token:object, *, _entry:Entry|None=None):
        """Disable a previously registered entry.

        Args:
            token: The token for the entry to disable.
            _entry: Internal override for performance, do not use directly.

        Returns:
            True if the entry was disabled or already disabled, False if not found.
        """

        entry = _entry
        if not isinstance(_entry,Entry):
            entry = self.storage.entry_by_token.get(token)
            if not entry:
                return False
        entry.enabled = False
        if entry.behavior == Behavior.LOOP:
            task = self.storage.loop_tasks.pop(token,None)
            if task:
                task.cancel()
        return True
    
    def toggle(self,token:object,*,toggle_amounts:int=1):
        """Toggle an entry enabled/disabled a number of times.

        Args:
            token: The token identifying the entry.
            toggle_amounts: Number of flips. 1 flips once, 2 restores to original.

        Returns:
            True if the token exists, False otherwise.
        """

        amt = toggle_amounts
        if toggle_amounts <= 0:
            amt = 1
        entry = self.storage.entry_by_token.get(token)
        if not entry:
            return False
        for i in range(amt):
            res = self.disable(token) if entry.enabled else self.enable(token)
        return res

    
    def reschedule(self,token:object,interval:float) -> bool:
        """Change the interval of a running LOOP entry.

        If loops are started and the entry is enabled, the loop task is restarted
        with the new interval.

        Args:
            token: The token identifying the entry.
            interval: New interval in seconds, must be positive.

        Returns:
            True on success, False if the token does not exist or is not LOOP.

        Raises:
            ValueError: If interval is not positive.
        """

        entry = self.storage.entry_by_token.get(token)
        if not entry or entry.behavior != Behavior.LOOP or interval <= 0:
            return False
        entry.interval = interval
        if token in self.storage.loop_tasks:
            self.toggle(token,toggle_amounts=2)
        return True
    
    async def start_loops(self) -> None:
        """Start all enabled LOOP entries by creating asyncio tasks.

        Subsequent registrations with LOOP behavior will auto-start while loops are
        running. Call stop_loops() to cancel all loop tasks.
        """

        self._started = True
        #task creation for all neabled loops
        for token, entry in list(self.storage.entry_by_token.items()):
            if entry.behavior == Behavior.LOOP and entry.enabled and token not in self.storage.loop_tasks:
                self.storage.loop_tasks[token] = self._create_loop_task(entry)
    
    async def stop_loops(self) -> None:
        """Stop all running loop tasks and mark loops as stopped."""
        self._started = False
        tasks = list(self.storage.loop_tasks.values())
        self.storage.loop_tasks.clear()
        for t in tasks:
            t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    def remove(self,token:object):
        """Remove a registered entry and all of its indexes.

        Args:
            token: The token identifying the entry.

        Returns:
            True if an entry was removed, False if the token was unknown.
        """

        entry = self.storage.entry_by_token.pop(token,None)
        if not entry:
            return False
        bucket = self.storage.hooks_by_name.get(entry.hook_name,[])
        try:
            bucket.remove(entry)
        except ValueError:
            pass
        if entry.tags:
            tag_map = self.storage.tags_index.get(entry.hook_name,{})
            for t in entry.tags:
                s = tag_map.get(t)
                if s and token in s:
                    s.remove(token)
        
        task = self.storage.loop_tasks.pop(token,None)
        if task:
            try:
                task.cancel()
            except Exception:
                pass
        return True
    
    
    # ===> Inspect Helpers/Token Getters <===
    def list_entries(self,hook_name:Optional[str]=None,*,tags:Optional[Set[str]]=None,
                     include_enabled:bool=True,include_disabled:bool=False
                     ) -> List[Entry]:
        """List entries, optionally filtered and including disabled ones.

        Args:
            hook_name: If provided, only entries for this name are returned.
            tags: If provided, only entries that include all of these tags are returned.
            include_untagged: If True and tags is provided, include untagged entries too.
            include_enabled: Include enabled entries.
            include_disabled: Include disabled entries.

        Returns:
            A list of Entry objects matching the filters, ordered by (priority, seq).
        """

        if not include_disabled and not include_enabled:
            return []
        out: List[Entry] = []
        names = [hook_name] if hook_name else list(self.storage.hooks_by_name.keys())
        for name in names:
            bucket = self.storage.hooks_by_name.get(name,[])
            for e in bucket:
                if not include_enabled and e.enabled:
                    continue
                if not include_disabled and not e.enabled:
                    continue
                if tags:
                    if not tags <= e.tags:
                        continue
                out.append(e)
        return out
    
    def find_tokens(self,hook_name:Optional[str] = None, tags:Optional[Set[str]]=None,
                    include_enabled:bool=True,include_disabled:bool=False
                    ) -> List[object]:
        """Return tokens for entries matching the provided filters.

        Args:
            hook_name: Optional hook_name filter.
            tags: Optional tag filter set.
            include_untagged: If True and tags is provided, include untagged entries.
            include_enabled: Include enabled entries.
            include_disabled: Include disabled entries.

        Returns:
            A list of tokens in the same order as list_entries().
        """

        if not include_enabled and not include_disabled:
            return []
        return [e.token for e in self.list_entries(hook_name=hook_name,tags=tags,include_enabled=include_enabled,include_disabled=include_disabled)]
    
    def token_of(self,callback:Callable) -> object|None:
        """Return the token previously attached to a decorated function.

        Args:
            callback: The function that was decorated with @on.

        Returns:
            The token object or None if the function has no token.
        """

        return getattr(callback,"__hookedin_token__",None)
    
    def remove_by_callback(self,callback:Callable) -> bool:
        """Remove a decorated function by inspecting its attached token.

        Args:
            callback: The function passed to @on.

        Returns:
            True if the callback had a token and was removed, False otherwise.
        """

        tok = self.token_of(callback=callback)
        return self.remove(tok) if tok is not None else False
    
    def info(self, token:object, debug:bool=False, *only_info_for_keys:str) -> dict:
        """Return a lightweight info dict for a token.

        Args:
            token: Token to inspect.
            debug: If True, include extra fields useful for debugging.
            *only_info_for_keys: Optional field names to limit the output.

        Returns:
            A dict with fields like hook_name, tags, priority, behavior, interval,
            enabled, and token. Returns None if the token is unknown.
        """

        e = self.storage.entry_by_token.get(token)
        if not e:
            return {}
        full = {
            "hook_name": e.hook_name,
            "tags": sorted(e.tags),
            "priority": e.priority,
            "seq": e.seq,
            "behavior": e.behavior,
            "interval": e.interval,
            "enabled": e.enabled,
            "is_loop_task_running": token in self.storage.loop_tasks,
            "has_on_fail": bool(e.on_fail),
            "callback_name": getattr(e.callback, "__name__", str(e.callback)),
            "token": token,
        }
        if only_info_for_keys:
            return {k: full[k] for k in only_info_for_keys if k in full}
        if debug:
            return full
        include_basic = ["hook_name","tags","priority","behavior","interval","enabled","token"]
        return {k: full[k] for k in include_basic}

    
    def has(self,token:object) -> bool:
        """Return True if a token exists in the registry."""

        return token in self.storage.entry_by_token
    
    def count(self,hook_name:str,*,tags:Optional[Set[str]]=None,include_enabled:bool=True,include_disabled:bool=False) -> int:
        """Count entries for a hook_name and optional tag filter.

        Args:
            hook_name: Name bucket to count.
            tags: Optional tag filter set.
            include_untagged: If True and tags is provided, include untagged entries.
            include_enabled: Include enabled entries in the count.
            include_disabled: Include disabled entries in the count.

        Returns:
            Integer count of matching entries.
        """

        return len(self.list_entries(
            hook_name=hook_name,tags=tags,include_enabled=include_enabled,include_disabled=include_disabled
        ))
    
    def change_priority(self,token:object,new_priority:float) -> bool:
        """Update the priority of an entry and reinsert it in order.

        Args:
            token: Token identifying the entry.
            new_priority: New priority value. Lower runs earlier.

        Returns:
            True if the entry was found and updated, False otherwise.
        """

        e = self.storage.entry_by_token.get(token)
        if not e:
            return False
        if not isinstance(new_priority,(int,float)):
            raise ValueError("new_priority must be a number")
        if new_priority == e.priority:
            return True
        
        self._bucket_remove(e.hook_name,e)
        e.priority = float(new_priority)
        self._bucket_insert(e.hook_name,e)
        return True
    
    def add_tags(self, token: object, tags_to_add: Iterable[str]) -> bool:
        """
        Add one or more tags to an entry and update the tag index.

        Args:
            token (object): The token identifying the entry whose tags should be modified.
            tags_to_add (Iterable[str]): An iterable of tag strings to add. 
                Each tag must be a string. Tags are normalized to lowercase
                and leading/trailing whitespace is removed.

        Returns:
            bool: 
                - True if the entry exists and its tags were updated (or no changes were needed).
                - False if the token does not correspond to any entry.

        Raises:
            ValueError: If any provided tag is not a string.
        """
        e = self.storage.entry_by_token.get(token)
        if not e:
            return False

        items = list(tags_to_add or ())
        if not items:
            return True
        if not all(isinstance(t, str) for t in items):
            raise ValueError("tags must be strings")

        add_norm = {t.strip().lower() for t in items if t and t.strip()}
        if not add_norm:
            return True

        old = e.tags
        new = frozenset(old | add_norm)
        if new == old:
            return True

        self._reindex_tags_for_entry(e, old_tags=old, new_tags=new)
        e.tags = new
        return True


    def remove_tags(self, token: object, tags_to_remove: Iterable[str]) -> bool:
        """
        Remove one or more tags from an entry and update the tag index.

        Args:
            token (object): The token identifying the entry whose tags should be modified.
            tags_to_remove (Iterable[str]): An iterable of tag strings to remove. 
                Each tag must be a string. Tags are normalized to lowercase
                and leading/trailing whitespace is removed.

        Returns:
            bool:
                - True if the entry exists and its tags were updated (or no changes were needed).
                - False if the token does not correspond to any entry.

        Raises:
            ValueError: If any provided tag is not a string.
        """
        e = self.storage.entry_by_token.get(token)
        if not e:
            return False

        items = list(tags_to_remove or ())
        if not items:
            return True
        if not all(isinstance(t, str) for t in items):
            raise ValueError("tags must be strings")

        rem_norm = {t.strip().lower() for t in items if t and t.strip()}
        if not rem_norm:
            return True

        old = e.tags
        new = frozenset(t for t in old if t not in rem_norm)
        if new == old:
            return True

        self._reindex_tags_for_entry(e, old_tags=old, new_tags=new)
        e.tags = new
        return True

    def register_reducer_func(self,reducer_name:str,func:Callable,*,overwrite:bool=False) -> bool:
        """Register or overwrite a reducer function.

        Args:
            reducer_name: Name to register under.
            func: Callable with signature (base: dict, edits: list[dict]) -> dict.
            overwrite: If True, allow replacing an existing non-protected reducer.

        Raises:
            ValueError: If attempting to override a protected built-in.
            NameError: If a reducer exists and override is False.
        
        Returns:
            True on successful register. Else False if Raises.
        """
        try:
            self.ReduceManager.register_reducer(reducer_name=reducer_name,func=func,overwrite=overwrite)
            return True
        except ValueError:
            print(f"can not overwrite built in reducers. | name: {reducer_name}")
        except NameError:
            print(f"can not overwrite reducer: {reducer_name}, set overwrite to `True` to overwrite.")
        finally:
            return False

    def set_metrics_sink(self,sink:Optional[Callable[[HookMetrics],None]]) -> None:
        """Attach or clear a metrics sink.

        The sink is called after every callback with a HookMetrics instance.

        Args:
            sink: Callable that accepts HookMetrics or None to disable metrics.
        """
        self._metrics_sink = sink

    # ====== Internal Helpers ======

    def _validate_registration(self, hook_name:str, tags:Optional[Iterable[str]],behavior:str,interval:Optional[float]) -> None:
        """Validate behavior and interval before registration.

        Args:
            hook_name: Name bucket, only used for error messages.
            tags: Optional iterable of tags, may be None.
            behavior: DEFAULT, ONESHOT, or LOOP.
            interval: Interval seconds for LOOP entries.

        Raises:
            ValueError: If LOOP is selected without a positive interval.
        """

        if not isinstance(hook_name,str) or not hook_name:
            raise ValueError("hook_name must be a non-empty string")
        if behavior == Behavior.LOOP:
            if interval is None or not (isinstance(interval,(int,float)) and interval > 0):
                raise ValueError("loop behavior requires a positive interval")
        elif behavior == Behavior.ONESHOT:
            if interval is not None:
                raise ValueError("oneshot behavior cannot set interval.")
        
        if tags is not None:
            for t in tags:
                if not isinstance(t,str):
                    raise ValueError("tags must be strings")
    
    def _bucket_remove(self, hook_name: str, entry: Entry) -> None:
        """Remove an Entry from the sorted bucket for its hook_name.

        Args:
            hook_name: Bucket key.
            entry: Entry to remove.

        Notes:
            Keeps ordering of remaining entries intact.
        """

        bucket = self.storage.hooks_by_name.get(hook_name, [])
        try:
            bucket.remove(entry)
        except ValueError:
            pass  # already gone

    def _bucket_insert(self, hook_name: str, entry: Entry) -> None:
        """Insert an Entry into the sorted bucket for its hook_name.

        Args:
            hook_name: Bucket key.
            entry: Entry to insert.

        Notes:
            Entries are kept ordered by (priority, seq).
        """

        bucket = self.storage.hooks_by_name[hook_name]
        keys = [(e.priority, e.seq) for e in bucket]
        idx = bisect.bisect_right(keys, (entry.priority, entry.seq))
        bucket.insert(idx, entry)

    def _reindex_tags_for_entry(self, entry: Entry, *, old_tags: frozenset[str], new_tags: frozenset[str]) -> None:
        """Update tag indexes for a single entry after tags change.

        Args:
            entry: Entry being updated.
            old_tags: Previous tag frozenset.
            new_tags: New tag frozenset.
        """

        name = entry.hook_name
        tok = entry.token
        tag_map = self.storage.tags_index[name]  # defaultdict(set)

        # Remove old memberships
        for t in old_tags:
            if t not in new_tags:
                s = tag_map.get(t)
                if s and tok in s:
                    s.remove(tok)
                    if not s:
                        # keep structure lean
                        try:
                            del tag_map[t]
                        except KeyError:
                            pass

        # Add new memberships
        for t in new_tags:
            if t not in old_tags:
                tag_map[t].add(tok)
    
    def _normalize_tags(self,tags:Optional[Iterable[str]]) -> frozenset[str]:
        """Return a lowercase frozenset from a tag iterable or an empty set.

        Args:
            tags: Iterable of tag strings or None.

        Returns:
            frozenset[str]: Normalized tag set.
        """

        if not tags:
            return frozenset()
        return frozenset(str(t).lower() for t in tags)
    
    def next_seq(self) -> int:
        """Return the next sequence integer used to break priority ties."""
        return next(self._seq_counter)
    
    def _make_token(self) -> object:
        """Create a new opaque token object for a registration.

        Returns:
            A unique object usable as a dictionary key.
        """

        return object()
    
    def _make_entry(self, *, hook_name:str, tags:frozenset[str],priority:float,seq:int,behavior:str,interval:Optional[float],
                    callback:Callable,on_fail:Optional[Callable],token:object
                    ) -> Entry:
        """Build an Entry dataclass from normalized parameters.

        Args:
            hook_name: Primary name.
            tags: Normalized tag frozenset.
            priority: Priority value.
            seq: Sequence tiebreaker.
            behavior: Behavior constant.
            interval: Interval seconds for LOOP or None.
            enabled: Whether the entry starts enabled.
            callback: The callable to run.
            on_fail: Optional error handler.
            token: The token representing this entry.

        Returns:
            The constructed Entry.
        """

        return Entry(
            hook_name=hook_name, tags=tags, priority=priority, seq=seq, behavior=behavior, 
            interval=interval, enabled=True, callback=callback, on_fail=on_fail, token=token,
        )
    
    def _register(self,*,callback:Callable, hook_name:str, tags:frozenset[str], priority:float, 
                  behavior:str, interval:Optional[float], on_fail:Optional[Callable]
                  ) -> Tuple[Entry,object]:
        """Insert a new entry into all indexes.

        Args:
            callback: Callable to run.
            hook_name: Primary name.
            tags: Normalized tag frozenset.
            priority: Priority value.
            behavior: Behavior constant.
            interval: Interval seconds for LOOP or None.
            enabled: Whether the entry starts enabled.
            on_fail: Optional error handler.

        Returns:
            (entry, token): The created Entry and its token.
        """

        seq = self.next_seq()
        token = self._make_token()
        entry = self._make_entry(hook_name=hook_name,tags=tags,priority=priority,seq=seq,
                                 behavior=behavior,interval=interval,callback=callback,on_fail=on_fail,token=token)
        self._index_entry(entry)
        return entry, token
    
    def _index_entry(self,entry:Entry) -> None:
        """Add an Entry to name bucket, token map, and tag indexes.

        Args:
            entry: Entry to index.
        """

        #Attribute easy access
        name = entry.hook_name
        priority = entry.priority
        seq = entry.seq
        token = entry.token

        # Insert with order
        bucket = self.storage.hooks_by_name[name]
        keys = [(e.priority, e.seq) for e in bucket]
        idx = bisect.bisect_right(keys,(priority,seq))
        bucket.insert(idx,entry)

        #Token Mapping:
        self.storage.entry_by_token[token] = entry

        # tag index per name
        if entry.tags:
            tag_map = self.storage.tags_index[name]
            for t in entry.tags:
                tag_map[t].add(token)

        if self._started and entry.behavior == Behavior.LOOP and entry.enabled:
            self.storage.loop_tasks[token] = self._create_loop_task(entry)
        
    
    def _create_loop_task(self, entry:Entry) -> Any:
        """Create and register an asyncio Task for a LOOP entry.

        Args:
            entry: LOOP Entry to schedule.

        Returns:
            The created asyncio.Task.
        """

        return asyncio.create_task(self._loop_runner(entry))
    
    async def _loop_runner(self, entry:Entry) -> None:
        """Task body for LOOP entries. Repeats callback at the entry interval.

        Args:
            entry: LOOP Entry to run.
        """

        busy = False
        try:
            while self._started and entry.enabled and entry.token in self.storage.entry_by_token:
                if not busy:
                    busy = True
                    try:
                        kw = self._prepare_kwargs(entry.callback, payload=None,extra={},unique_inputs=True)
                        await self._invoke_with_timing(entry,kw,strict=False)
                    except Exception:
                        pass
                    finally:
                        busy = False
                await asyncio.sleep(entry.interval or 0.0)
        except asyncio.CancelledError:
            return


    def _select_entries(self, hook_name:str, emitter_tags:Optional[Set[str]],
                        include_untagged:bool) -> List[Entry]:
        """Select entries for a name and optional tag filter.

        Args:
            hook_name: Name bucket to search.
            emitter_tags: Tags requested by the emitter or None.
            include_untagged: If True and emitter_tags is provided, include untagged.

        Returns:
            A list of Entry objects in run order.
        """

        emitter_tags = {str(t).lower() for t in emitter_tags} if emitter_tags else set()
        bucket = self.storage.hooks_by_name.get(hook_name,[])
        bucket = [e for e in bucket if e.behavior != Behavior.LOOP]
        if not bucket:
            return []
        if not emitter_tags:
            return list(bucket)
        
        tag_map:Dict[str, Set[object]] = self.storage.tags_index.get(hook_name)
        if tag_map and all(t in tag_map for t in emitter_tags):
            iter_sets = [tag_map[t] for t in emitter_tags]
            candidate_tokens = set.intersection(*iter_sets) if iter_sets else set()
            if include_untagged:
                return [e for e in bucket if (not e.tags) or (e.token in candidate_tokens)]
            return [e for e in bucket if e.token in candidate_tokens]
        
        e_tags = set(emitter_tags)
        if include_untagged:
            return [e for e in bucket if (not e.tags) or (e_tags <= e.tags)]
        return [e for e in bucket if e_tags <= e.tags]
    
    def _prepare_kwargs(self, fn:callable, payload:Any, extra:dict[str,Any], unique_inputs:bool,
                        ) -> Dict[str,Any]:
        """Prepare **kwargs for invoking a callback.

        Ensures the payload is passed correctly based on the function signature and
        adds any extra kwargs from the emitter.

        Args:
            fn: The callback to be invoked.
            payload: The payload object from the emitter.
            extra_kwargs: Extra keyword arguments from the emitter.
            unique_inputs: If True, shallow copy dict-like payloads.

        Returns:
            A dict of keyword arguments to use when calling the callback.
        """

        cand: Dict[str,Any] = dict(extra) if extra else {}
        if payload is not None:
            if isinstance(payload,dict):
                cand["ctx"] = payload.copy() if unique_inputs else payload
            else:
                cand["payload"] = payload
        sig = inspect.signature(fn)
        allowed = sig.parameters.keys()
        return {k:v for k,v in cand.items() if k in allowed}
    
    async def _invoke_with_timing(self, entry:Entry, kwargs:Dict[str,Any],strict:bool
                                  ) -> Tuple[bool,Any,Optional[BaseException],float]:
        """Call a callback and measure elapsed time.

        Args:
            entry: Entry to invoke.
            kwargs: Keyword arguments to pass to the callback.
            strict: If True, raise exceptions instead of swallowing them.

        Returns:
            (ok, value, error, elapsed_ms)
        """

        loop = asyncio.get_running_loop()
        t0 = loop.time()

        ok_flag = False
        val = None
        err_obj: Optional[BaseException] = None

        try:
            res = entry.callback(**kwargs)
            if inspect.iscoroutine(res):
                res = await res
            ok_flag, val, err_obj = True, res, None
        except BaseException as exc:
            # run on_fail if present
            try:
                if entry.on_fail:
                    maybe = entry.on_fail(exc)
                    if inspect.iscoroutine(maybe):
                        await maybe
            finally:
                if strict:
                    raise
            ok_flag, val, err_obj = False, None, exc

        elapsed = (loop.time() - t0) * 1000.0

        if self._metrics_sink:
            try:
                self._metrics_sink(HookMetrics(hook_name=entry.hook_name, entry=entry,
                                            elapsed_ms=elapsed, ok=ok_flag))
            except Exception:
                pass

        return ok_flag, val, err_obj, elapsed
    
    def _maybe_chain_payload(self, current:Any, returned:Any, ok:bool) -> Any:
        """Compute the next payload value in sequential mode.

        Args:
            current: Current working payload value.
            returned: Value returned by the callback.
            ok: True if the callback completed without raising.

        Returns:
            The payload to use for the next callback.
        """

        if not ok:
            return current
        if isinstance(current,dict):
            return current
        if returned is not None:
            return returned
        return current
    
    def _mk_result(self, entry:Entry, value:Any, ok:bool, error:Optional[BaseException], elapsed_ms:float
                         ) -> HookResult:
        """Create a HookResult record from a callback outcome.

        Args:
            entry: The Entry that was invoked.
            value: The return value from the callback.
            ok: True if the callback succeeded.
            error: Exception instance if raised, else None.
            elapsed_ms: Execution time in milliseconds.

        Returns:
            A HookResult instance.
        """

        hr = HookResult.__new__(HookResult)
        hr.entry = entry
        hr.value = value
        hr.ok = ok
        hr.error = error
        hr.elapsed_ms = elapsed_ms
        return hr


    async def _run(self, *, mode:str, hook_name:str, tags:Optional[Set[str]],parallel:bool,strict:bool,include_untagged:bool,
                   unique_inputs:Optional[bool],payload:Any,
                   reducer:Optional[Callable[[dict,List[dict]],dict]|str],**extra_kwargs
                   ) -> Tuple[List[HookResult],Any]:
        """Core execution engine used by fire, trigger, and gather.

        Args:
            mode: "fire", "trigger", or "gather".
            hook_name: Name to emit.
            tags: Optional tag filter set.
            parallel: If True, run handlers concurrently.
            strict: If True, re-raise exceptions.
            include_untagged: If True and tags is provided, include untagged entries.
            unique_inputs: If None, defaults to parallel. See fire().
            payload: Initial payload object.
            reducer: Callable or registered name for merging dict results in parallel.
            extra_kwargs: Additional keyword args forwarded to callbacks.

        Returns:
            (results, final_payload) where results is a list[HookResult] and
            final_payload is the chained or merged value.
        """

        entries = self._select_entries(hook_name,tags,include_untagged)
        if not entries:
            return [],payload
        
        if unique_inputs is None:
            unique_inputs = parallel
        
        # SEQUENTIAL ORDER
        if not parallel:
            current_payload = payload
            out: List[HookResult] = []
            for e in entries:
                if not e.enabled:
                    continue
                call_kwargs = self._prepare_kwargs(fn=e.callback, payload=current_payload, extra=extra_kwargs, unique_inputs=unique_inputs)
                ok, val, err, elapsed = await self._invoke_with_timing(e, call_kwargs, strict)

                if ok and e.behavior == Behavior.ONESHOT:
                    self.remove(e.token)
                
                if mode == "gather":
                    out.append(self._mk_result(entry=e, value=val, ok=ok, error=err, elapsed_ms=elapsed))

                if mode == "trigger":
                    current_payload = self._maybe_chain_payload(current=current_payload,returned=val,ok=ok)

            return out, current_payload
        
        # PARALLEL ORDER
        # build per entry kwargs
        per_entry_kwargs:List[Optional[Dict[str,Any]]] = []
        for e in entries:
            if not e.enabled:
                per_entry_kwargs.append(None)
            else:
                per_entry_kwargs.append(self._prepare_kwargs(fn=e.callback,payload=payload,extra=extra_kwargs,unique_inputs=unique_inputs))
        
        # START
        corouts = []
        for e, kw in zip(entries, per_entry_kwargs):
            if not e.enabled:
                async def _noop():
                    return False, None, None, 0.0   # ok=False so oneshot is NOT removed
                corouts.append(_noop())
            else:
                corouts.append(self._invoke_with_timing(e, kw, strict))

        raw = await asyncio.gather(*corouts, return_exceptions=False)

        # Build Result for Output
        out: List[HookResult] = []
        for e, tup in zip(entries, raw):
            ok, val, err, elapsed = tup
            if ok and e.behavior == Behavior.ONESHOT:
                self.remove(e.token)               # only removes if the hook truly ran and ok=True
            if mode == "gather":
                out.append(self._mk_result(e, val, ok, err, elapsed))
        
        # Final Payload Logic
        final_payload = payload
        if mode == "trigger":
            if isinstance(payload,dict):
                #collect dict returns from only successfully triggered hooks
                dicts:List[dict] = []
                for ok_i, val_i, _err_i, _elapsed_i in raw:
                    if ok_i and isinstance(val_i,dict):
                        dicts.append(val_i)
                reducer_func = self.ReduceManager._resolve_reducer(reducer)
                try:
                    final_payload = reducer_func(payload,dicts)
                except Exception:
                    final_payload = payload
            else:
                for ok_i, val_i, _err_i, _elapsed_i in raw:
                    if ok_i and val_i is not None:
                        final_payload = val_i
                        break
        
        return out, final_payload
                



_GLOBAL_HOOKS:Optional[Hookedin] = None

def get_hook_manager() -> Hookedin:
    """Return a process-wide singleton Hookedin instance.

    Creates the instance on first call, then returns the same object on later calls.

    Returns:
        Hookedin: The global hook manager.
    """

    global _GLOBAL_HOOKS
    if _GLOBAL_HOOKS is None:
        _GLOBAL_HOOKS = Hookedin()
    return _GLOBAL_HOOKS

        
