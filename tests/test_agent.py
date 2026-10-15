import pytest
from unittest.mock import patch, MagicMock
from src.agent import CrossPayAgent


def test_agent_initializes_with_student_id():
    agent = CrossPayAgent("STU001", "fake-key")
    assert agent.student_id == "STU001"

def test_agent_starts_with_no_pending_action():
    agent = CrossPayAgent("STU001", "fake-key")
    assert agent.pending_action is None

def test_agent_starts_with_no_previous_interaction():
    agent = CrossPayAgent("STU001", "fake-key")
    assert agent.previous_interaction_id is None

def test_confirm_without_pending_returns_message():
    agent = CrossPayAgent("STU001", "fake-key")
    result = agent.confirm_action()
    assert "no pending" in result.lower()

def test_cancel_clears_pending_action():
    agent = CrossPayAgent("STU001", "fake-key")
    agent.pending_action = {"tool": "add_expense", "args": {}, "preview": {}}
    result = agent.cancel_action()
    assert agent.pending_action is None
    assert "cancel" in result.lower()

def test_cancel_without_pending_returns_message():
    agent = CrossPayAgent("STU001", "fake-key")
    result = agent.cancel_action()
    assert agent.pending_action is None

def test_get_system_prompt_contains_rules():
    agent = CrossPayAgent("STU001", "fake-key")
    prompt = agent._system_prompt()
    assert "CrossPay" in prompt
    assert "confirmation" in prompt.lower()

@patch("src.agent.genai")
def test_chat_stores_previous_interaction_id(mock_genai):
    mock_client = MagicMock()
    mock_genai.Client.return_value = mock_client
    mock_interaction = MagicMock()
    mock_interaction.id = "interaction-abc-123"
    mock_interaction.steps = []
    mock_interaction.output_text = "Hello! How can I help?"
    mock_client.interactions.create.return_value = mock_interaction
    agent = CrossPayAgent("STU001", "fake-key")
    response = agent.chat("Hello")
    assert agent.previous_interaction_id == "interaction-abc-123"
    assert response == "Hello! How can I help?"

@patch("src.agent.genai")
def test_chat_passes_previous_interaction_id_on_second_turn(mock_genai):
    mock_client = MagicMock()
    mock_genai.Client.return_value = mock_client
    def make_interaction(iid, text):
        m = MagicMock()
        m.id = iid
        m.steps = []
        m.output_text = text
        return m
    mock_client.interactions.create.side_effect = [
        make_interaction("id-1", "First response"),
        make_interaction("id-2", "Second response"),
    ]
    agent = CrossPayAgent("STU001", "fake-key")
    agent.chat("First")
    agent.chat("Second")
    second_call_kwargs = mock_client.interactions.create.call_args_list[1][1]
    assert second_call_kwargs.get("previous_interaction_id") == "id-1"

@patch("src.agent.genai")
@patch("src.agent.dispatch_tool")
def test_chat_detects_confirmation_required(mock_dispatch, mock_genai):
    mock_client = MagicMock()
    mock_genai.Client.return_value = mock_client
    func_call_step = MagicMock()
    func_call_step.type = "function_call"
    func_call_step.name = "add_expense"
    func_call_step.arguments = {"student_id": "STU001", "amount_cny": 80.0, "category": "food", "note": "dinner"}
    mock_interaction = MagicMock()
    mock_interaction.id = "id-conf"
    mock_interaction.steps = [func_call_step]
    mock_interaction.output_text = "Please confirm"
    mock_client.interactions.create.return_value = mock_interaction
    mock_dispatch.return_value = {"recorded": False, "confirmation_required": True, "new_balance_cny": 3420.0}
    agent = CrossPayAgent("STU001", "fake-key")
    response = agent.chat("Record 80 CNY dinner")
    assert agent.pending_action is not None
    assert agent.pending_action["tool"] == "add_expense"
    assert len(response) > 0
