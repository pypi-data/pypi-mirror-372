import pytest

from promium.support.settings import SettingsOpera


@pytest.mark.unit
def test_binary_path():
    assert SettingsOpera.binary_path
    assert "opera" in SettingsOpera.binary_path
