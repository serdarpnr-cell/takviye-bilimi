"""Faz 2 kapısı: görsel kartlar gerçek tarayıcıda, MCP Apps host benzetimiyle hatasız çizilir.

Node.js ve Playwright yoksa atlanır. Ayrıntı: scripts/kart_onizleme.py
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parent.parent


def _playwright_var() -> bool:
    if not shutil.which("node"):
        return False
    r = subprocess.run(["node", "-e", "require('playwright')"], capture_output=True, env=_ortam())
    return r.returncode == 0


def _ortam() -> dict:
    ortam = dict(os.environ)
    kok = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip() if shutil.which("npm") else ""
    if kok:
        ortam["NODE_PATH"] = os.pathsep.join(filter(None, [ortam.get("NODE_PATH"), kok]))
    return ortam


@pytest.mark.skipif(not _playwright_var(), reason="Node.js ve Playwright gerekli")
def test_dort_kart_hatasiz_cizilir(monkeypatch):
    sys.path.insert(0, str(KOK / "scripts"))
    for k, v in _ortam().items():
        monkeypatch.setenv(k, v)
    import kart_onizleme

    rapor = kart_onizleme.calistir(None, goruntu=False)
    adlar = {r["ad"] for r in rapor}
    assert {"karne_sonuc", "kanit_d_vitamini", "urun_d3k2_8_yas", "rutin_varfarin"} <= adlar
    for r in rapor:
        assert r["konsol_hatalari"] == [], r
        assert r["eksik_ogeler"] == [], r
        assert r["alt_bilgi_gorunur"], r
        assert r["yukseklik"] > 0, r
    # Kanıt kartı sayfalamayı modelden gizli araçla kendisi yapar.
    assert "katalog_sayfasi" in next(r for r in rapor if r["ad"] == "kanit_d_vitamini")["tools_call"]
