from typing import Any, Callable

def _unwrap(fn):
    """
    If fn is a bound method, returns fn.__func__.
    If fn has been wrapped by functools.wraps or a decorator, returns fn.__wrapped__.
    Otherwise returns fn itself.
    """
    return (
        getattr(fn, "__wrapped__", None)
        or getattr(fn, "__func__", None)
        or fn
    )

def merge_task_metadata(
    func: Callable[..., Any],
    **extra_meta: Any
) -> bool:
    """
    Merge extra_meta into an existing _task_metadata dict on both
    the unwrapped function and its wrapper.

    Returns True if metadata was present and updated, False otherwise.
    """
    real_fn = _unwrap(func)
    current = getattr(real_fn, "_task_metadata", None)
    if not isinstance(current, dict):
        return False

    # shallow copy + merge
    updated = {**current, **extra_meta}

    # write back to both places
    setattr(real_fn, "_task_metadata", updated)
    setattr(func,      "_task_metadata", updated)
    return True
