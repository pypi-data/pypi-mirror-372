# test_hookedin.py
"""
Pytest port of the Hookedin comprehensive test suite (pro).

Discovery:
    pytest -v

Notes:
- Keeps logic and expectations identical to your original harness.
- Uses pytest.mark.asyncio for async tests.
- Adds a small session fixture to show tracemalloc stats at the end,
  which mirrors your original summary without changing test logic.
"""

import asyncio
import time
import pytest
from hookedin import Behavior, get_reducer_manager, get_hook_manager as get_hook_manager


# ----- optional: session memory stats like your original summary -----
@pytest.fixture(scope="session", autouse=True)
def _tracemalloc_session():
    import tracemalloc
    tracemalloc.start()
    t0 = time.perf_counter()
    yield
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    elapsed = time.perf_counter() - t0
    print(
        f"\n== Session Summary ==\n"
        f"Elapsed time: {elapsed:.3f} s\n"
        f"Tracemalloc current: {current/1024:.1f} KiB  peak: {peak/1024:.1f} KiB"
    )


# ---------- Tests ----------

@pytest.mark.asyncio
async def test_registration_and_tokens():
    h = get_hook_manager()

    @h.on("reg", priority=2)
    def decorated(payload=None):
        return "decorated"

    def sync_plain(payload=None):
        return "sync_plain"

    async def async_dict(ctx=None):
        await asyncio.sleep(0)
        return {"mark": "async_dict"}

    t_sync = h.add(sync_plain, "reg", priority=1)
    t_async = h.add(async_dict, "reg", priority=0)
    assert all(t is not None for t in (t_sync, t_async))

    res = await h.gather("reg", payload={"x": 1}, parallel=False, foo="bar")
    vals = [r.value for r in res]
    assert len(res) == 3 and "sync_plain" in vals

    final = await h.trigger("reg", payload={"start": True}, parallel=False)
    assert isinstance(final, dict)

    tok_decorated = h.token_of(decorated)
    assert tok_decorated is not None and h.has(tok_decorated)

    assert h.token_of(sync_plain) is None

    removed = h.remove_by_callback(decorated)
    assert removed and not h.has(tok_decorated)


@pytest.mark.asyncio
async def test_priority_and_change_priority():
    h = get_hook_manager()
    order = []

    @h.on("prio", priority=0)
    def a(payload=None):
        order.append("a")

    @h.on("prio", priority=0)
    def b(payload=None):
        order.append("b")

    # initial order with same priority is by seq
    await h.fire("prio", payload=None)
    assert order == ["a", "b"]

    btok = h.token_of(b)
    ok1 = h.change_priority(btok, -10)
    order.clear()
    await h.fire("prio", payload=None)
    assert ok1 and order == ["b", "a"]

    ok2 = h.change_priority(btok, -10)
    assert ok2 is True

    with pytest.raises(Exception):
        h.change_priority(btok, "bad")  # type: ignore


@pytest.mark.asyncio
async def test_enable_disable_toggle_reschedule_remove():
    h = get_hook_manager()
    hits = {"hb": 0}

    @h.on("loopA", behavior=Behavior.LOOP, interval=0.03)
    def hb(payload=None):
        hits["hb"] += 1

    def will_remove(payload=None):
        return "ok"

    tok_nonloop = h.add(will_remove, "loopA")

    await h.start_loops()
    await asyncio.sleep(0.12)

    loop_tokens = list(h.storage.loop_tasks.keys())
    assert len(loop_tokens) >= 1
    tok_loop = loop_tokens[0]
    assert h.toggle(tok_loop, toggle_amounts=1)  # disable
    assert h.toggle(tok_loop, toggle_amounts=1)  # enable
    assert h.reschedule(tok_loop, 0.01) is True

    assert h.remove(tok_nonloop) is True

    await h.stop_loops()
    assert h._started is False

    fake = object()
    assert h.disable(fake) is False
    assert h.enable(fake) is False
    assert h.reschedule(fake, 0.5) is False


@pytest.mark.asyncio
async def test_fire_gather_trigger_parallel_and_strict():
    h = get_hook_manager()

    @h.on("work", priority=0)
    def d1(payload=None):
        return {"a": 1, "shared": 1}

    @h.on("work", priority=1)
    async def d2(ctx=None):
        await asyncio.sleep(0)
        return {"b": 2, "shared": 2}

    r1 = await h.trigger("work", payload={"start": True}, parallel=True, reducer="last_wins")
    assert r1.get("shared") == 2

    r2 = await h.trigger("work", payload={"start": True}, parallel=True, reducer="first_wins")
    assert r2.get("shared") == 1

    r3 = await h.trigger("work", payload={"n": 0, "shared": 0}, parallel=True, reducer="sum_numbers")
    assert r3.get("b") == 2

    def boom(payload=None):
        raise RuntimeError("boom")

    h.add(boom, "boom")
    with pytest.raises(RuntimeError):
        await h.fire("boom", payload=None, strict=True)


@pytest.mark.asyncio
async def test_tag_filtering_and_indexing():
    h = get_hook_manager()

    @h.on("t", tags=["red", "fast"])
    def t1(payload=None):
        return "t1"

    @h.on("t", tags=["red"])
    def t2(payload=None):
        return "t2"

    @h.on("t")
    def t3(payload=None):
        return "t3"

    r = await h.gather("t", payload=None, tags={"red"}, include_untagged=False)
    assert all(rr.entry.tags for rr in r)  # no untagged

    r2 = await h.gather("t", payload=None, tags={"red"}, include_untagged=True)
    assert any(not rr.entry.tags for rr in r2)  # untagged included

    tok3 = h.token_of(t3)
    h.add_tags(tok3, ["red"])
    r3 = await h.gather("t", payload=None, tags={"red"}, include_untagged=False)
    names3 = [rr.entry.callback.__name__ for rr in r3]
    assert "t3" in names3

    h.remove_tags(tok3, ["red"])
    r4 = await h.gather("t", payload=None, tags={"red"}, include_untagged=False)
    names4 = [rr.entry.callback.__name__ for rr in r4]
    assert "t3" not in names4

    c_red = h.count("t", tags={"red"})
    tokens = h.find_tokens("t")
    assert c_red >= 1
    assert len(tokens) >= 2


@pytest.mark.asyncio
async def test_prepare_kwargs_and_unique_inputs():
    h = get_hook_manager()

    def uses_ctx(ctx=None):
        if isinstance(ctx, dict):
            ctx["mutated"] = True
        return ctx

    h.add(uses_ctx, "u", priority=0)

    original = {"k": 1}
    final1 = await h.trigger("u", payload=original, parallel=False)
    assert "mutated" in original  # sequential allows mutation

    h2 = get_hook_manager()
    h2.add(uses_ctx, "u2", priority=0)
    original2 = {"k": 2}
    final2 = await h2.trigger("u2", payload=original2, parallel=True, unique_inputs=True)
    assert "mutated" not in original2  # original preserved

    seen = {"got": None}

    @h.on("non_dict")
    def see_payload(payload=None):
        seen["got"] = payload

    await h.fire("non_dict", payload=123)
    assert seen["got"] == 123


@pytest.mark.asyncio
async def test_reducers_and_custom_registration():
    h = get_hook_manager()
    mgr = get_reducer_manager()

    f = mgr._resolve_reducer("last_wins")
    assert callable(f)

    def custom_sum(base: dict, edits: list[dict]) -> dict:
        out = base.copy()
        out["sum_b"] = sum(e.get("b", 0) for e in edits)
        return out

    registered = True
    try:
        mgr.register_reducer("pro_custom", custom_sum, overwrite=True)
    except Exception:
        registered = False
    assert registered

    @h.on("red", priority=0)
    def r1(payload=None):
        return {"b": 1}

    @h.on("red", priority=1)
    def r2(payload=None):
        return {"b": 2}

    res = await h.trigger("red", payload={"b": 0}, parallel=True, reducer="pro_custom")
    assert res.get("sum_b") == 3

    ok_flag = h.register_reducer_func("pro_custom2", custom_sum, overwrite=True)
    try:
        mgr.register_reducer("pro_custom2", custom_sum, overwrite=True)
    except Exception:
        pass
    res2 = await h.trigger("red", payload={"b": 0}, parallel=True, reducer="pro_custom2")
    assert res2.get("sum_b") == 3


@pytest.mark.asyncio
async def test_metrics_sink_and_result_fields():
    h = get_hook_manager()
    seen = []

    def sink(m):
        seen.append(
            {
                "hook_name": m.hook_name,
                "elapsed_ms": m.elapsed_ms,
                "ok": m.ok,
                "callback": getattr(m.entry.callback, "__name__", "anon"),
            }
        )

    h.set_metrics_sink(sink)

    @h.on("met", priority=0)
    def m1(payload=None):
        return 42

    @h.on("met")
    def m2(payload=None):
        raise ValueError("nope")

    await h.fire("met", payload=None)
    assert len(seen) >= 2
    assert all("callback" in x for x in seen)
    assert any(not x["ok"] for x in seen)

    results = await h.gather("met", payload=None, parallel=False, strict=False)
    assert any((not r.ok and r.error) for r in results)


@pytest.mark.asyncio
async def test_list_find_count_info_and_remove():
    h = get_hook_manager()

    def a(payload=None):
        return 1

    def b(payload=None):
        return 2

    t1 = h.add(a, "L", tags=["alpha"])
    t2 = h.add(b, "L", tags=None)

    lst = h.list_entries("L")
    assert len(lst) == 2

    toks = h.find_tokens("L")
    assert len(toks) == len(lst)

    count_alpha = h.count("L", tags={"alpha"})
    assert count_alpha == 1

    info = h.info(t1, debug=False)
    assert set(["hook_name", "tags", "priority", "behavior", "interval", "enabled", "token"]).issubset(
        set(info.keys())
    )

    rem = h.remove(t1)
    assert rem is True
    assert h.has(t1) is False


@pytest.mark.asyncio
async def test_start_stop_idempotency_and_remove_active_loop():
    h = get_hook_manager()
    ticks = {"n": 0}

    @h.on("loops", behavior=Behavior.LOOP, interval=0.03)
    def lo(payload=None):
        ticks["n"] += 1

    await h.start_loops()
    await h.start_loops()  # idempotent
    await asyncio.sleep(0.08)

    # remove an active loop entry
    tok = next(iter(h.storage.loop_tasks.keys()))
    removed = h.remove(tok)
    assert removed is True

    await asyncio.sleep(0.06)

    await h.stop_loops()
    await h.stop_loops()  # idempotent
    assert not h._started


@pytest.mark.asyncio
async def test_stress_light_parallel():
    h = get_hook_manager()
    N = 300
    counter = {"n": 0}

    def mk(i):
        def cb(payload=None):
            counter["n"] += 1
            return {"i": i}
        return cb

    for i in range(N):
        h.add(mk(i), "S")

    t0 = time.perf_counter()
    res = await h.trigger("S", payload={"ok": True}, parallel=True, reducer="last_wins")
    dt = time.perf_counter() - t0
    assert counter["n"] == N
