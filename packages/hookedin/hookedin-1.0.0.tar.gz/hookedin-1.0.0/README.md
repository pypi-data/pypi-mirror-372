# Hookedin

Lightweight, async‑friendly hook and plug‑in manager with tags, priorities, and reducer‑based result merging. Designed for clean composition of middleware, event pipelines, and extension points.

> Batteries included: decorators and programmatic registration, tag filtering, stable priority ordering, async concurrency, looped handlers, reducer‑based dict merges, metrics sink, and easy introspection.

---

## Installation

```bash
pip install hookedin
```

For development:

```bash
pip install -e .[dev]
pytest -v
```

Python 3.9 or newer.

---

## Quick start

```python
from hookedin import get_hook_manager, Behavior, get_reducer_manager

h = get_hook_manager()  # get a manager instance

# Register with a decorator
@h.on("message", tags=["audit"], priority=10)
def audit(ctx=None):
    # ctx is the dict payload for dict inputs
    return {"seen": True, "shared": 1}

# Register async handler
@h.on("message", priority=0)
async def do_work(ctx=None):
    # this one runs before audit due to priority=0
    return {"ok": True, "shared": 2}

# Trigger in parallel and merge dicts using a reducer
result = await h.trigger(
    "message",
    payload={"start": True, "shared": 0},
    parallel=True,
    reducer="last_wins",   # or "first_wins", "sum_numbers", or a custom reducer
)
print(result)  # {'start': True, 'seen': True, 'ok': True, 'shared': 2}
```

> Prefer `trigger()` when you want a final dict. Use `gather()` to get a list of detailed results. Use `fire()` for fire‑and‑forget semantics.

---

## Core concepts

### Hooks and handlers

* A **hook** is a named event channel like `"on_connect"` or `"message"`.
* A **handler** is any sync or async callable you register to a hook.
* Register with a decorator or programmatically.

```python
# decorator
@h.on("reg", tags=["red"], priority=1)
def decorated(payload=None):
    return "ok"

# programmatic
async def async_handler(ctx=None):
    return {"mark": "async"}

tok = h.add(async_handler, "reg", priority=0)
```

Each registration returns a **token** you can use to manage the entry later.

### Priority and order

* Lower numeric priority runs earlier.
* Equal priorities are stable by registration sequence.

```python
order = []

@h.on("prio", priority=0)
def a(payload=None): order.append("a")

@h.on("prio", priority=0)
def b(payload=None): order.append("b")

await h.fire("prio")
assert order == ["a", "b"]

# Raise b to the front
h.change_priority(h.token_of(b), -10)
order.clear(); await h.fire("prio")
assert order == ["b", "a"]
```

### Tags and filtering

* Handlers can have zero or more string **tags**.
* When firing, you can filter by tags and include or exclude untagged handlers.

```python
@h.on("t", tags=["red", "fast"])  
@h.on("t", tags=["red"])  
@h.on("t")  # untagged
async def _(...): ...

# Only tag‑matched
await h.gather("t", tags={"red"}, include_untagged=False)

# Tag‑matched plus untagged
await h.gather("t", tags={"red"}, include_untagged=True)

# Update tags later
tok = h.token_of(_)
h.add_tags(tok, ["red"])   # now matches
h.remove_tags(tok, ["red"]) # no longer matches
```

### Execution modes

* `fire()` – run handlers without collecting values. Errors bubble only if `strict=True`.
* `gather()` – run handlers and collect `HookResult` objects with `.value`, `.ok`, `.error`, `.elapsed_ms`, and `.entry`.
* `trigger()` – run handlers and merge the dict outputs into a single dict using a reducer. This is ideal for middleware‑style edits.

```python
# Strict error propagation
@h.on("boom")
def boom(payload=None):
    raise RuntimeError("boom")

with pytest.raises(RuntimeError):
    await h.fire("boom", strict=True)
```

#### Common keyword arguments for execution methods

* `payload` – The data passed to handlers. If it’s a `dict`, handlers receive it as `ctx`. Otherwise it is passed as `payload`.
* `tags` – A set of tags to filter which handlers run.
* `include_untagged` – Whether to include untagged handlers when filtering by tags (default `True`).
* `parallel` – If `True`, handlers run concurrently instead of sequentially.
* `strict` – If `True`, exceptions in handlers are re‑raised immediately; otherwise errors are captured in the result objects.
* `unique_inputs` – If `True` (only valid with `parallel=True`), each handler receives its own copy of the payload, preventing shared mutation.
* `reducer` – Only for `trigger()`. Chooses how multiple dict results are merged (`last_wins`, `first_wins`, `sum_numbers`, or custom).
* `**extra` – Any additional keyword arguments are forwarded to handlers as named arguments, making it easy to inject context like `user_id=123`.

This flexibility makes `fire`, `gather`, and `trigger` suitable for a wide range of use cases, from simple event dispatch to complex middleware pipelines.


### Parallelism and reducers

* Set `parallel=True` to run handlers concurrently.
* Choose how dict outputs merge:

  * `"last_wins"` – later handlers override earlier ones
  * `"first_wins"` – first value wins
  * `"sum_numbers"` – numeric values are summed, others use last wins
* Provide a custom reducer as a name you registered or as a callable.

```python
mgr = get_reducer_manager()

def my_merge(base: dict, edits: list[dict]) -> dict:
    out = base.copy()
    out["sum_b"] = sum(d.get("b", 0) for d in edits)
    return out

mgr.register_reducer("my_merge", my_merge, overwrite=True)

merged = await h.trigger("red", payload={"b": 0}, parallel=True, reducer="my_merge")
```

### Payload passing

* If the payload is a dict, it is given to handlers as `ctx` to encourage structured edits.
* If the payload is not a dict, it is passed as `payload`.
* Set `unique_inputs=True` with `parallel=True` to give each handler its own deep copy so the caller’s input is not mutated by handlers.

```python
def uses_ctx(ctx=None):  # receives dict
    ctx["mutated"] = True

# sequential allows mutation of the original dict
original = {"k": 1}
await h.trigger("u", payload=original, parallel=False)
assert "mutated" in original

# parallel unique inputs preserve the caller’s dict
original2 = {"k": 2}
await h.trigger("u2", payload=original2, parallel=True, unique_inputs=True)
assert "mutated" not in original2
```

### Looped handlers

* Handlers can run in a loop with `behavior=Behavior.LOOP` and an `interval` in seconds.
* Start and stop loops across the manager. You can toggle or reschedule a loop by token.

```python
@h.on("heartbeat", behavior=Behavior.LOOP, interval=0.50)
def tick(payload=None):
    print("tick")

await h.start_loops()
...
# pause then resume a specific loop entry
h.toggle(h.token_of(tick), toggle_amounts=1); h.toggle(h.token_of(tick), toggle_amounts=1)
# change its interval
h.reschedule(h.token_of(tick), 0.25)
...
await h.stop_loops()
```

### Introspection and management

* `token_of(fn)` – get the token of a decorated handler.
* `has(token)` – check presence.
* `remove(token)` or `remove_by_callback(fn)` – remove handlers.
* `list_entries(name)` – get entries registered to a hook.
* `find_tokens(name)` – get tokens under a hook.
* `count(name, tags={...})` – count entries by hook and optional tags.
* `info(token, debug=False)` – view a dict of entry properties.

---

## Metrics

Provide a sink to observe each handler’s timings and outcome. Great for logging and dashboards.

```python
stats = []

def sink(m):
    stats.append({
        "hook_name": m.hook_name,
        "ok": m.ok,
        "elapsed_ms": m.elapsed_ms,
        "callback": getattr(m.entry.callback, "__name__", "anon"),
        "error": type(m.error).__name__ if m.error else None,
    })

h.set_metrics_sink(sink)
await h.fire("myhook")
```

The metrics object includes at least: `hook_name`, `entry`, `ok`, `error`, `elapsed_ms`.

---

## API summary

> Signatures are shown in a friendly form. Types may be more specific in code.

**Registration**

* `on(hook_name, *, tags=None, priority=0, behavior=Behavior.DEFAULT, interval=None, on_fail=None)` – decorator
* `add(callback, hook_name, *, tags=None, priority=0, behavior=Behavior.DEFAULT, interval=None, on_fail=None) -> token`

**Execution**

* `fire(name, *, payload=None, tags=None, include_untagged=True, parallel=False, strict=False, **extra)`
* `gather(name, *, payload=None, tags=None, include_untagged=True, parallel=False, strict=False, unique_inputs=None, **extra) -> list[HookResult]`
* `trigger(name, *, payload: dict, tags=None, include_untagged=True, parallel=False, reducer="last_wins", unique_inputs=None, **extra) -> dict`

**Reducers**

* Built‑ins: `"last_wins"`, `"first_wins"`, `"sum_numbers"`
* `get_reducer_manager().register_reducer(name, func, overwrite=False)`

**Looping**

* `start_loops()` – start all loop entries
* `stop_loops()` – stop them
* `toggle(token, toggle_amounts=1)` – enable or disable a specific entry
* `reschedule(token, interval)` – change loop interval

**Introspection and edit**

* `token_of(callback) -> token | None`
* `has(token) -> bool`
* `remove(token) -> bool`
* `remove_by_callback(callback) -> bool`
* `change_priority(token, new_priority) -> bool`
* `add_tags(token, tags: Iterable[str]) -> bool`
* `remove_tags(token, tags: Iterable[str]) -> bool`
* `list_entries(hook_name) -> list[Entry]`
* `find_tokens(hook_name) -> list[token]`
* `count(hook_name, tags=None) -> int`
* `info(token, debug=False) -> dict`

**Metrics**

* `set_metrics_sink(callable)` – receive per‑handler timing and status

**Factory and module exports**

* `get_hook_manager()` – create or return a manager instance
* `Behavior` – behaviors: `DEFAULT`, `ONESHOT`, `LOOP`
* `get_reducer_manager()` – reducer registry for merges

---

## Custom reducers

Reducers take `(base: dict, edits: list[dict]) -> dict` and return a new dict.

```python
from hookedin import get_reducer_manager

mgr = get_reducer_manager()

def only_truthy(base, edits):
    out = base.copy()
    for d in edits:
        for k, v in d.items():
            if v:
                out[k] = v
    return out

mgr.register_reducer("only_truthy", only_truthy, overwrite=True)
```

Use by name in `trigger(..., reducer="only_truthy")` or pass the function.

---

## Error handling

* By default errors are captured in `HookResult.error` and do not stop other handlers.
* Set `strict=True` in `fire()` or `gather()` to re‑raise the first error.
* You can also provide per‑entry `on_fail` callbacks when registering if you prefer local handling.

---

## Patterns

### Middleware style edits

Group ordered steps that progressively transform a dict, then reduce the outputs into a final view.

### Feature flags and tags

Tag handlers with features or environments, then filter at call time.

### Background ticks

Use `Behavior.LOOP` for lightweight heartbeats. Example: emit periodic metrics or refresh caches.

---

## Versioning and stability

* Follows semver. Breaking changes increase the major version.
* No runtime dependencies.

---

## Contributing

Issues and pull requests are welcome. Please include tests where possible.

---

## Contact

Created by [Kevin d'Anunciacao](mailto:kmdjr.dev@gmail.com).  
Feel free to reach out via email or open an issue on [GitHub](https://github.com/Kmdjr/hookedin).

---

## License

MIT License. See `LICENSE` for details.
