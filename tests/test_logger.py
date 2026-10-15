import json
import pytest
from pathlib import Path
from src.logger import log_tool_call
from src.tool_registry import dispatch_tool, TOOL_DECLARATIONS


def test_log_creates_jsonl_file(tmp_path):
    log_tool_call(
        "test_tool",
        {"key": "val"},
        {"result": "ok"},
        log_dir=str(tmp_path)
    )
    files = list(tmp_path.glob("execution_log.jsonl"))
    assert len(files) == 1


def test_log_appends_multiple_entries(tmp_path):
    log_tool_call("tool_a", {}, {"x": 1}, log_dir=str(tmp_path))
    log_tool_call("tool_b", {}, {"x": 2}, log_dir=str(tmp_path))
    lines = (tmp_path / "execution_log.jsonl").read_text().strip().splitlines()
    assert len(lines) == 2


def test_log_entry_has_required_fields(tmp_path):
    log_tool_call(
        "get_exchange_rate",
        {"from_currency": "BDT", "to_currency": "CNY"},
        {"rate": 0.065},
        log_dir=str(tmp_path)
    )
    with open(tmp_path / "execution_log.jsonl") as f:
        entry = json.loads(f.readline())
    assert "timestamp" in entry
    assert "tool_name" in entry
    assert "inputs" in entry
    assert "output_summary" in entry
    assert entry["tool_name"] == "get_exchange_rate"


def test_log_masks_pii_in_inputs(tmp_path):
    log_tool_call(
        "add_expense",
        {"student_id": "STU001", "account": "12345678"},
        {"recorded": True},
        log_dir=str(tmp_path)
    )
    with open(tmp_path / "execution_log.jsonl") as f:
        entry = json.loads(f.readline())
    # The raw 8-digit account number must not appear in the log
    assert "12345678" not in json.dumps(entry)


def test_log_output_summary_truncated(tmp_path):
    big_output = {"data": "x" * 1000}
    log_tool_call("big_tool", {}, big_output, log_dir=str(tmp_path))
    with open(tmp_path / "execution_log.jsonl") as f:
        entry = json.loads(f.readline())
    assert len(entry["output_summary"]) <= 220  # 200 chars + some json overhead


def test_dispatch_tool_get_exchange_rate():
    result = dispatch_tool("get_exchange_rate", {"from_currency": "USD", "to_currency": "CNY"})
    assert "rate" in result
    assert result["rate"] > 6.0


def test_dispatch_tool_convert_amount():
    result = dispatch_tool("convert_amount", {"amount": 100.0, "from_currency": "USD", "to_currency": "CNY"})
    assert "converted" in result
    assert result["converted"] > 0


def test_dispatch_tool_compare_remittance():
    result = dispatch_tool("compare_remittance_options", {"amount_usd": 500.0, "destination_country": "CN"})
    assert isinstance(result, list)
    assert len(result) >= 3


def test_dispatch_tool_check_aml():
    result = dispatch_tool("check_aml_threshold", {"amount_usd": 15000.0})
    assert result["flagged"] is True


def test_dispatch_tool_check_sanctions():
    result = dispatch_tool("check_sanctioned_destination", {"country_code": "IR"})
    assert result["blocked"] is True


def test_dispatch_tool_unknown_raises():
    with pytest.raises(ValueError, match="Unknown tool"):
        dispatch_tool("nonexistent_tool", {})


def test_tool_declarations_is_list():
    assert isinstance(TOOL_DECLARATIONS, list)
    assert len(TOOL_DECLARATIONS) >= 8


def test_tool_declarations_have_required_fields():
    for decl in TOOL_DECLARATIONS:
        assert "name" in decl
        assert "description" in decl
        assert "parameters" in decl
        assert "properties" in decl["parameters"]
