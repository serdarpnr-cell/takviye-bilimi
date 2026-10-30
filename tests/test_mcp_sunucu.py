"""MCP protokolü üzerinden uçtan uca testler (bellek içi ve gerçek HTTP)."""

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.shared.memory import create_connected_server_and_client_session

from server.app import mcp
from server.ozet import OZET_SINIRI
from server.veri import UYARI

KOK = Path(__file__).resolve().parent.parent

CAGRILAR = {
    "urun_rehberi": {"urun": "Ocean Magnezyum Complex"},
    "parti_analizi": {"karekod_veya_parti_no": "https://ornek.example/k/MG-24D210"},
    "kisisel_rutin": {
        "yas": 41, "cinsiyet": "kadin", "evre": "yok", "ilac_grubu": ["kan_sulandirici_varfarin"],
        "mevcut_urunler": ["Ocean D3K2 Damla"],
        "diger_urun_icerikleri": [{"ad": "Multi", "icerikler": [{"etken_madde": "D vitamini", "miktar": 800, "birim": "IU"}]}],
    },
    "etken_madde_rehberi": {"etken_madde": "D vitamini", "yas": 41},
    "sikayet_yolu": {"sikayet": "Kendimi yorgun hissediyorum", "yas": 41, "cinsiyet": "kadin"},
    "karsilastir": {"etken_madde": "D vitamini", "yas": 8, "ilac_grubu": ["kan_sulandirici_varfarin"]},
    "takviye_rehberi": {"konu": "Kış geldi, hangi vitaminleri almam gerek?"},
    "tahlil_goster": {"tahlil": "B12"},
    "yasam_karnesi": {"cevaplar": {"hareket_gun": 2, "uyku_saat": 7, "sebze_meyve_porsiyon": 3,
                                   "balik_haftalik": 1, "sigara": "hayir", "stres": "bazen"}},
}


async def _arac_testleri(oturum: ClientSession) -> None:
    araclar = (await oturum.list_tools()).tools
    # katalog_sayfasi görsel kartın kendi çağırdığı araçtır (modelden gizli).
    assert {t.name for t in araclar} == set(CAGRILAR) | {"katalog_sayfasi"}
    for t in araclar:
        a = t.annotations
        # v0.3 Bölüm 6: dizin başvurusu için zorunlu ek açıklamalar.
        assert (a.readOnlyHint, a.destructiveHint, a.idempotentHint, a.openWorldHint) == (True, False, True, False), t.name
        assert a.title, t.name
    for ad, arg in CAGRILAR.items():
        sonuc = await oturum.call_tool(ad, arg)
        assert not sonuc.isError, (ad, sonuc.content)
        assert sonuc.structuredContent["uyari"] == UYARI
        assert sonuc.structuredContent["kaynaklar"], ad
        assert "Takviye edici gıdalar ilaç değildir" in sonuc.content[0].text
        # Modele kısa özet, karta tam veri.
        assert len(sonuc.content[0].text) <= OZET_SINIRI, ad
        assert sonuc.structuredContent["kisa_ozet"] in sonuc.content[0].text


async def test_bellek_ici_protokol():
    async with create_connected_server_and_client_session(mcp) as oturum:
        await _arac_testleri(oturum)


async def test_pydantic_dogrulama_hatasi_arac_hatasi_olarak_doner():
    async with create_connected_server_and_client_session(mcp) as oturum:
        sonuc = await oturum.call_tool("kisisel_rutin", {"yas": 30, "cinsiyet": "bilinmiyor"})
        assert sonuc.isError


def _bos_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def http_sunucu():
    port = _bos_port()
    ortam = {k: v for k, v in os.environ.items() if k not in ("TB_PORT", "TB_ALLOWED_HOSTS")}
    # PORT ve RENDER_EXTERNAL_HOSTNAME, Render'daki gibi verilir.
    ortam.update({"PORT": str(port), "TB_ALLOWED_HOSTS": "ornek.ngrok-free.app",
                  "RENDER_EXTERNAL_HOSTNAME": "takviye-bilimi.onrender.com"})
    surec = subprocess.Popen([sys.executable, "-m", "server"], cwd=KOK, env=ortam,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    url = f"http://127.0.0.1:{port}/mcp"
    for _ in range(100):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                break
        except OSError:
            time.sleep(0.1)
    else:
        surec.kill()
        raise RuntimeError(surec.stdout.read().decode())
    yield url
    surec.terminate()
    cikti = surec.communicate(timeout=10)[0].decode()
    # Sunucu çıktısında kişisel girdiler görünmemeli.
    assert "kan_sulandirici_varfarin" not in cikti
    assert "Multi" not in cikti


async def test_streamable_http_mcp(http_sunucu):
    async with httpx.AsyncClient(trust_env=False, timeout=30) as istemci:
        async with streamable_http_client(http_sunucu, http_client=istemci) as (oku, yaz, _):
            async with ClientSession(oku, yaz) as oturum:
                await oturum.initialize()
                await _arac_testleri(oturum)


async def _initialize(url: str, host: str) -> httpx.Response:
    govde = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "t", "version": "0"}}}
    async with httpx.AsyncClient(trust_env=False) as istemci:
        return await istemci.post(url, json=govde, headers={
            "Host": host, "Accept": "application/json, text/event-stream"})


async def test_izinli_ngrok_adresi_kabul_edilir(http_sunucu):
    yanit = await _initialize(http_sunucu, "ornek.ngrok-free.app")
    assert yanit.status_code == 200
    assert json.loads(yanit.text)["result"]["serverInfo"]["name"] == "Takviye Bilimi"


async def test_render_adresi_kabul_edilir(http_sunucu):
    yanit = await _initialize(http_sunucu, "takviye-bilimi.onrender.com")
    assert yanit.status_code == 200


async def test_izinsiz_host_reddedilir(http_sunucu):
    yanit = await _initialize(http_sunucu, "kotu.example.com")
    assert yanit.status_code in (400, 421)
