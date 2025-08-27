
from typing import Callable, List, Dict, Optional, Set

class MergeReducerManager:
    """Registry of merge reducers used by parallel trigger() calls.

    Provides a table of named reducers, a set of protected built-ins, and a
    helper to resolve a reducer from a callable or string key.
    """

    def __init__(self):
        """Initialize built-in reducers and the protected-name set."""
        self.protected:Set[str] = set(["first_wins",
                                       "last_wins",
                                       "sum_numbers",
                                       ])
        self.table:dict[str,Callable] = {
            "first_wins":self._reduce_first_wins,
            "last_wins":self._reduce_last_wins,
            "sum_numbers":self._reduce_sum_numbers,                      
            }
        

    def _resolve_reducer(self, merge:Optional[Callable[[dict,List[dict]],dict]|str]
                            ) -> Callable[[dict,List[dict]],dict]:
        """Return a reducer callable from a name or callable.

        Args:
            merge: A callable reducer, a registered name, or None.

        Returns:
            A reducer callable with signature (base: dict, edits: list[dict]) -> dict.

        Raises:
            KeyError: If a string name is given and no reducer is registered under it.
        """

        if callable(merge):
            return merge
        if isinstance(merge,str):
            return self.table.get(merge.lower(),self._reduce_last_wins)
        return self.table.get("last_wins")
    
    def _reduce_last_wins(self,base:dict,edits:List[dict]) -> dict:
        """Merge dict edits, letting later values overwrite earlier ones.

        Args:
            base: Starting dict. Not modified.
            edits: List of dicts produced by handlers.

        Returns:
            A new dict where later edits take precedence on conflicts.
        """

        out = base.copy()
        for d in edits:
            out.update(d)
        return out
    
    def _reduce_first_wins(self,base:dict,edits:List[dict]) -> dict:
        """Merge dict edits, keeping the first value for each key.

        Args:
            base: Starting dict. Not modified.
            edits: List of dicts produced by handlers.

        Returns:
            A new dict. The first non-missing value for each key is kept.
        """

        out = base.copy()
        for d in edits:
            for k, v in d.items():
                if k not in out:
                    out[k] = v
        return out

    def _reduce_sum_numbers(self,base:dict,edits:List[dict]) -> dict:
        """Merge dict edits by summing numeric values.

        Numeric values for the same key are summed. Non-numeric values fall back to
        "last wins" behavior.

        Args:
            base: Starting dict. Not modified.
            edits: List of dicts produced by handlers.

        Returns:
            A new dict with numeric keys summed where applicable.
        """

        out = base.copy()
        for d in edits:
            for k, v in d.items():
                if isinstance(v, (int, float)) and isinstance(out.get(k), (int,float)):
                    out[k] = out[k] + v
                else:
                    out[k] = v
        return out

    def register_reducer(self,reducer_name:str,func:Callable,overwrite:bool=False) -> None:
        """Register or overwrite a reducer function.

        Args:
            reducer_name: Name to register under.
            func: Callable with signature (base: dict, edits: list[dict]) -> dict.
            override: If True, allow replacing an existing non-protected reducer.

        Raises:
            ValueError: If attempting to override a protected built-in.
            NameError: If a reducer exists and override is False.
        """

        name = reducer_name.lower()
        if name in self.protected:
            raise ValueError(f"can not overwrite built in reducers. | name: {reducer_name}")
        if name in self.table.keys() and not overwrite:
            raise NameError(f"can not overwrite reducer: {reducer_name}, set overwrite to `True` to overwrite.")
        self.table[name] = func



_GLOBAL_REDUCE_MANAGER:Optional[MergeReducerManager] = None

def get_reducer_manager() -> MergeReducerManager:
    """Return a process-wide singleton MergeReducerManager.

    Creates the instance on first call, then returns the same object on later calls.

    Returns:
        MergeReducerManager: The global reducer manager.
    """
    global _GLOBAL_REDUCE_MANAGER
    if _GLOBAL_REDUCE_MANAGER is None:
        _GLOBAL_REDUCE_MANAGER = MergeReducerManager()
    return _GLOBAL_REDUCE_MANAGER
