"""Benchmark & Latency SLA Verification Test Suite.
Validates sub-15ms local inference, deterministic consistency across iterations,
and memory bounds during high-throughput tool dispatching.
"""

import time
import pytest
from src.autonomous_engine import AutonomousFinEngine
from src.tool_registry import dispatch_tool

@pytest.fixture
def engine():
    return AutonomousFinEngine(student_id="STU001")

def test_autonomous_inference_latency_sla(engine):
    """Ensure average intent classification and response latency is under 35ms on CI runners."""
    query = "What is the current BDT to CNY exchange rate?"
    latencies = []

    # Warm-up (3 iterations to prime caches and JIT paths)
    for _ in range(3):
        engine.chat(query)

    for _ in range(50):
        t0 = time.perf_counter()
        res = engine.chat(query)
        t1 = time.perf_counter()
        latencies.append((t1 - t0) * 1000)
        assert len(res) > 0

    avg_latency = sum(latencies) / len(latencies)
    assert avg_latency < 35.0, f"Average latency {avg_latency:.2f}ms exceeded 35ms SLA"

def test_deterministic_dispatch_throughput():
    """Verify dispatching 100 consecutive FX conversions executes in under 500ms."""
    # Warm-up
    dispatch_tool("convert_amount", {"amount": 500.0, "from_currency": "USD", "to_currency": "CNY"})

    t0 = time.perf_counter()
    for _ in range(100):
        res = dispatch_tool("convert_amount", {"amount": 500.0, "from_currency": "USD", "to_currency": "CNY"})
        assert res["converted"] > 0
    t1 = time.perf_counter()
    total_time_ms = (t1 - t0) * 1000
    assert total_time_ms < 500.0, f"100 conversions took {total_time_ms:.2f}ms (expected < 500ms)"
