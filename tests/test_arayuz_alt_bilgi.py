"""TB-06: her görsel kart (MCP Apps ui:// kaynağı) marka alt bilgisini kendi HTML'inde taşır."""

import re

from mcp.shared.memory import create_connected_server_and_client_session

from server.app import MCP_APP_MIME, mcp
from server.arayuz import ALT_BILGI_METNI


async def _arayuzler(oturum) -> dict[str, str]:
    kaynaklar = (await oturum.list_resources()).resources
    sayfalar = {}
    for k in kaynaklar:
        if k.mimeType == MCP_APP_MIME:
            icerik = (await oturum.read_resource(k.uri)).contents[0]
            sayfalar[str(k.uri)] = icerik.text
    return sayfalar


def _gorunur_metin(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html))


async def test_her_arayuzde_marka_alt_bilgisi_var():
    async with create_connected_server_and_client_session(mcp) as oturum:
        sayfalar = await _arayuzler(oturum)
    assert sayfalar, "En az bir ui:// arayüzü kayıtlı olmalı."
    for uri, html in sayfalar.items():
        alt = re.search(r'<footer class="alt-bilgi"[^>]*>(.*?)</footer>', html, re.S)
        assert alt, uri
        assert _gorunur_metin(alt.group(1)).strip() == ALT_BILGI_METNI, uri
        # Alt bilgi ana içeriğin dışında ve sabit HTML'dedir; betik çalışmasa da görünür.
        assert html.index("</main>") < alt.start() < html.index("<script>"), uri
        assert ".alt-bilgi" in html, uri


async def test_arayuze_bagli_her_aracin_kaynagi_kayitli():
    async with create_connected_server_and_client_session(mcp) as oturum:
        sayfalar = await _arayuzler(oturum)
        araclar = (await oturum.list_tools()).tools
    bagli = [(t.name, (t.meta or {}).get("ui", {}).get("resourceUri")) for t in araclar]
    bagli = [(ad, uri) for ad, uri in bagli if uri]
    assert bagli
    for ad, uri in bagli:
        assert uri in sayfalar, ad


async def test_istemcide_gorunen_ad_teknik_ad_degil():
    async with create_connected_server_and_client_session(mcp) as oturum:
        bilgi = oturum.get_server_capabilities()
        araclar = (await oturum.list_tools()).tools
    assert bilgi is not None
    assert mcp.name == "Takviye Bilimi"
    assert all(t.title and "_" not in t.title for t in araclar)
