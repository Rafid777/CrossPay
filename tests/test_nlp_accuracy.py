"""Unit tests for advanced NLP entity parsing (Chinese numbers, shorthand, relative dates) and new accuracy intents."""
import pytest
from src.autonomous_engine import AutonomousFinEngine
from src.agent import CrossPayAgent


def test_extract_shorthand_amounts_en():
    engine = AutonomousFinEngine("STU001")
    e1 = engine.extract_entities("Convert 10k USD to CNY")
    assert e1["amount"] == 10000.0
    
    e2 = engine.extract_entities("Send 50k to China")
    assert e2["amount"] == 50000.0


def test_extract_chinese_numbers():
    engine = AutonomousFinEngine("STU001")
    e1 = engine.extract_entities("转账5万元到深圳大学")
    assert e1["amount"] == 50000.0
    
    e2 = engine.extract_entities("记录消费3千元买电脑")
    assert e2["amount"] == 3000.0


def test_predict_intent_safe_quota():
    engine = AutonomousFinEngine("STU001")
    intent, conf = engine.predict_intent_with_confidence("How much of my SAFE annual quota is remaining?")
    assert intent == "check_safe_quota"
    assert conf >= 0.80
    
    intent_zh, conf_zh = engine.predict_intent_with_confidence("查询我今年的国家外汇管理局便利化结汇额度")
    assert intent_zh == "check_safe_quota"


def test_predict_intent_pboc_parity():
    engine = AutonomousFinEngine("STU001")
    intent, _ = engine.predict_intent_with_confidence("What is today's PBOC central parity rate for USD?")
    assert intent == "get_pboc_central_parity_rate"
    
    intent_zh, _ = engine.predict_intent_with_confidence("查询今日央行人民币中间价")
    assert intent_zh == "get_pboc_central_parity_rate"


def test_predict_intent_anomalies():
    engine = AutonomousFinEngine("STU001")
    intent, _ = engine.predict_intent_with_confidence("Check my transactions for any abnormal spending or anomalies")
    assert intent == "detect_spending_anomalies"
    
    intent_zh, _ = engine.predict_intent_with_confidence("帮我检测最近是否有异常消费支出")
    assert intent_zh == "detect_spending_anomalies"


def test_autonomous_chat_safe_quota_response():
    agent = CrossPayAgent("STU001", api_key="", engine_mode="autonomous")
    resp = agent.chat("Check my SAFE foreign exchange quota for $5,000 USD transfer")
    assert "SAFE" in resp or "外汇" in resp
    assert "50,000" in resp or "50000" in resp


def test_autonomous_chat_pboc_rate_response():
    agent = CrossPayAgent("STU001", api_key="", engine_mode="autonomous")
    resp = agent.chat("What is today's PBOC central parity rate for USD/CNY?")
    assert "PBOC" in resp or "中间价" in resp or "Parity" in resp
