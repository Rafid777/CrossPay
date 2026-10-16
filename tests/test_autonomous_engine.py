"""
Tests for CrossPay Autonomous FinEngine and Offline Agent Capability.
Verifies zero-API-key standalone execution, intent prediction, entity extraction,
and 2-step confirmation gate.
"""
import pytest
from src.db import get_db
from src.mock_data import seed_mock_data
from src.autonomous_engine import AutonomousFinEngine
from src.agent import CrossPayAgent


@pytest.fixture(autouse=True)
def setup_test_db():
    conn = get_db()
    seed_mock_data(conn)
    conn.close()


def test_autonomous_engine_initializes():
    engine = AutonomousFinEngine("STU001")
    assert engine.student_id == "STU001"
    assert engine.pipeline is not None


def test_predict_intent_exchange_rate():
    engine = AutonomousFinEngine("STU001")
    intent = engine.predict_intent("What is the current BDT to CNY exchange rate?")
    assert intent == "get_exchange_rate"


def test_predict_intent_remittance_comparison():
    engine = AutonomousFinEngine("STU001")
    intent = engine.predict_intent("Compare remittance options to send $500 to China")
    assert intent == "compare_remittance_options"


def test_predict_intent_aml_check():
    engine = AutonomousFinEngine("STU001")
    intent = engine.predict_intent("Will sending $12,000 USD trigger AML compliance?")
    assert intent == "check_aml_threshold"


def test_predict_intent_sanctions():
    engine = AutonomousFinEngine("STU001")
    intent = engine.predict_intent("Is Iran on the sanctioned countries list for transfer?")
    assert intent == "check_sanctioned_destination"


def test_predict_intent_worldbank():
    engine = AutonomousFinEngine("STU001")
    intent = engine.predict_intent("World Bank official remittance data for Bangladesh")
    assert intent == "get_worldbank_remittance"


def test_extract_entities_amount_and_currencies():
    engine = AutonomousFinEngine("STU001")
    entities = engine.extract_entities("Convert $500 USD to CNY")
    assert entities.get("amount") == 500.0
    assert entities.get("from_currency") == "USD"
    assert entities.get("to_currency") == "CNY"


def test_autonomous_chat_bilingual_en():
    agent = CrossPayAgent("STU001", api_key="", engine_mode="autonomous")
    response = agent.chat("What is the current BDT to CNY exchange rate?")
    assert "Real-Time Foreign Exchange Rate" in response or "Spot Rate" in response
    assert "BDT" in response and "CNY" in response
    assert agent.pending_action is None


def test_autonomous_chat_bilingual_zh():
    agent = CrossPayAgent("STU001", api_key="", engine_mode="autonomous")
    response = agent.chat("查询最新的 BDT 对人民币汇率。")
    assert "实时外汇汇率" in response or "微众金融" in response
    assert agent.pending_action is None


def test_autonomous_chat_write_triggers_confirmation():
    agent = CrossPayAgent("STU001", api_key="", engine_mode="autonomous")
    response = agent.chat("Record 50 CNY for lunch")
    assert agent.pending_action is not None
    assert agent.pending_action["tool"] == "add_expense"
    assert "Confirmation" in response or "confirmation" in response


def test_autonomous_chat_confirm_action():
    agent = CrossPayAgent("STU001", api_key="", engine_mode="autonomous")
    agent.chat("Record 50 CNY for lunch")
    assert agent.pending_action is not None
    confirm_msg = agent.confirm_action()
    assert agent.pending_action is None
    assert "Done" in confirm_msg or "completed" in confirm_msg


def test_agent_runs_100_percent_offline_without_api_key():
    # Crucial test: No API key passed at all
    agent = CrossPayAgent("STU001", api_key="")
    resp1 = agent.chat("Compare remittance options to send $500")
    assert "Remittance" in resp1 or "WeBank" in resp1
    resp2 = agent.chat("How to build credit in China?")
    assert "Credit" in resp2 or "score" in resp2
