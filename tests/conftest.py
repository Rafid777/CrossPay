"""Pytest fixtures and configuration for CrossPay test suite."""
import os
import pytest
from src.db import get_db
from src.mock_data import seed_mock_data


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Ensure data/crosspay.db exists and is fully seeded before any tests run."""
    db_path = "data/crosspay.db"
    conn = get_db(db_path)
    seed_mock_data(conn)
    conn.close()
