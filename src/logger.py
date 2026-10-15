import json
import os
from datetime import datetime
from src.tools.compliance import mask_pii


def log_tool_call(
    tool_name: str,
    inputs: dict,
    output: dict,
    log_dir: str = "logs"
) -> None:
    """Append one JSON line to the execution audit log."""
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "execution_log.jsonl")

    # Mask PII in inputs before logging
    inputs_str = json.dumps(inputs, default=str)
    masked_inputs_str = mask_pii(inputs_str)
    try:
        masked_inputs = json.loads(masked_inputs_str)
    except json.JSONDecodeError:
        masked_inputs = {"raw": masked_inputs_str}

    # Truncate output summary to 200 chars
    output_str = json.dumps(output, default=str)
    output_summary = output_str[:200] + "..." if len(output_str) > 200 else output_str

    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tool_name": tool_name,
        "inputs": masked_inputs,
        "output_summary": output_summary,
    }

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
