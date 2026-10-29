import pytest

from server.veri import UYARI


@pytest.fixture
def uyari_var():
    def kontrol(yanit: dict) -> None:
        assert yanit["uyari"] == UYARI
        assert "Takviye edici gıdalar ilaç değildir" in yanit["uyari"]
        assert yanit["gelistirici"] == "Orzax tarafından geliştirilmiştir."

    return kontrol
