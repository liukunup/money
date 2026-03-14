import pytest
from app.core.config import settings

def test_settings_app_name():
    assert settings.APP_NAME == "Money"

def test_settings_debug_mode():
    assert settings.DEBUG == True

def test_settings_database_type():
    assert settings.DATABASE_TYPE == "sqlite"
