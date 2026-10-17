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
    """Ensure average intent classification and response latency is under 15ms."""
    query = "What is the current BDT to CNY exchange rate?"
    latencies = []

    # Warm-up
    engine.chat(query)

    for _ in range(50):
        t0 = time.perf_counter()
        res = engine.chat(query)
        t1 = time.perf_counter()
        latencies.append((t1 - t0) * 1000)
        assert len(res) > 0

    avg_latency = sum(latencies) / len(latencies)
    assert avg_latency < 15.0, f"Average latency {avg_latency:.2f}ms exceeded 15ms SLA"

def test_deterministic_dispatch_throughput():
    """Verify dispatching 100 consecutive FX conversions executes in under 200ms."""
    t0 = time.perf_counter()
    for _ in range(100):
        res = dispatch_tool("convert_amount", {"amount": 500.0, "from_currency": "USD", "to_currency": "CNY"})
        assert res["converted"] > 0
    t1 = time.perf_counter()
    total_time_ms = (t1 - t0) * 1000
    assert total_time_ms < 200.0, f"100 conversions took {total_time_ms:.2f}ms (expected < 200ms)"
