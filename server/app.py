"""Takviye Bilimi MCP sunucusu (Streamable HTTP, /mcp)."""

from __future__ import annotations

import os
from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import CallToolResult, ToolAnnotations
from pydantic import Field

from . import araclar, arayuz, ozet, veri

TALIMATLAR = (
    "Takviye Bilimi, takviye edici gıdalar hakkında Türkçe, markadan bağımsız etiket ve kanıt bilgisi sunar. "
    "Orzax tarafından geliştirilmiştir. Araçları yalnızca takviye ürünleri, takviye rutini, parti analizi "
    "veya yaşam tarzı karnesiyle ilgili sorularda çağır. Tanı koyma, kişiye doz önerme, belirli bir ürünü "
    "alması gerektiğini söyleme. Her yanıtta 'uyari' alanındaki notu kullanıcıya ilet. "
    "Karne sorularını seçenekleriyle iki adımda sor (önce 4, sonra 2 soru); kullanıcı seçenek seçerse kodunu ilet. "
    "Araç yanıtı kısa bir özettir; ayrıntı görsel karttadır, eksik bilgi için web araması yapma. "
    + veri.VERI_NOTU
)
# Görsel kartın kendi çağırdığı, modelden gizlenen araçlar (MCP Apps).
YALNIZCA_KART = {"ui": {"visibility": ["app"]}}
KARNE_ARAYUZU = "ui://takviye-bilimi/karne"
MCP_APP_MIME = "text/html;profile=mcp-app"

# Sadece okuma yapan, dış dünyaya dokunmayan araçlar.
SALT_OKUMA = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)


def _guvenlik() -> TransportSecuritySettings:
    """DNS rebinding korumasını açık tutar; ngrok gibi ek adresler TB_ALLOWED_HOSTS ile eklenir.

    Render'da çalışırken Render'ın verdiği adres (RENDER_EXTERNAL_HOSTNAME) kendiliğinden eklenir.
    """
    ham = [os.environ.get("TB_ALLOWED_HOSTS", ""), os.environ.get("RENDER_EXTERNAL_HOSTNAME", "")]
    ekler = [h.strip() for parca in ham for h in parca.split(",") if h.strip()]
    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=["127.0.0.1:*", "localhost:*", "[::1]:*", *ekler],
        allowed_origins=["http://127.0.0.1:*", "http://localhost:*", "http://[::1]:*", *(f"https://{h}" for h in ekler)],
    )


mcp = FastMCP(
    name="Takviye Bilimi",
    instructions=TALIMATLAR,
    host=os.environ.get("TB_HOST", "127.0.0.1"),
    # Barındırma servisleri (ör. Render) portu PORT değişkeniyle verir.
    port=int(os.environ.get("TB_PORT") or os.environ.get("PORT") or "8000"),
    streamable_http_path="/mcp",
    stateless_http=True,
    json_response=True,
    # Kişisel veri loglanmasın diye ayrıntılı log kapalı.
    log_level="WARNING",
    transport_security=_guvenlik(),
)


@mcp.tool(
    title="Ürün rehberi",
    description=(
        "Katalogdaki bir takviye ürününün etiket bilgisini verir: etken madde miktarları, beslenme referans değeri, "
        "bileşim, etiketteki kullanım, yaş sınırı ve ürün sayfasındaki sağlık beyanları. Katalog şu an yalnızca Orzax "
        "ürünlerini içerir. Kullanıcı belirli bir ürünü sorduğunda kullan."
    ),
    annotations=SALT_OKUMA,
)
def urun_rehberi(
    urun: Annotated[str, Field(description="Ürün adı, ör. 'Ocean D3K2 Damla'")],
    yas: Annotated[int | None, Field(ge=0, le=120, description="İsteğe bağlı: ürünü kullanacak kişinin yaşı")] = None,
) -> CallToolResult:
    return ozet.sonuc("urun_rehberi", araclar.urun_rehberi(urun, yas))


@mcp.tool(
    title="Parti analizi",
    description=(
        "Kutudaki karekod içeriğinden ya da parti numarasından yayımlanmış parti analizini arar. Katalogda şu an "
        "yayımlanmış analiz yoktur; araç bunu bildirir. Kullanıcı karekod okuttuğunda veya bir partinin analizini sorduğunda kullan."
    ),
    annotations=SALT_OKUMA,
)
def parti_analizi(
    karekod_veya_parti_no: Annotated[str, Field(description="Karekod içeriği (URL veya GS1 metni) ya da parti numarası")],
) -> CallToolResult:
    return ozet.sonuc("parti_analizi", araclar.parti_analizi(karekod_veya_parti_no))


@mcp.tool(
    title="Kişisel rutin kontrolü",
    description=(
        "Kullanıcının kullandığı takviyeleri birlikte kontrol eder: tekrar eden etken madde, EFSA üst sınırı aşımı, "
        "etiket uyarıları, ilaç grubu etkileşimleri ve hekime sorulacak sorular. Doz önermez. "
        "Kullanıcı birden fazla takviyeyi birlikte kullanmayı sorduğunda kullan."
    ),
    annotations=SALT_OKUMA,
)
def kisisel_rutin(
    yas: Annotated[int, Field(ge=0, le=120, description="Yaş (yıl)")],
    cinsiyet: araclar.Cinsiyet,
    evre: Annotated[araclar.Evre, Field(description="Gebelik veya emzirme durumu")] = "yok",
    ilac_grubu: Annotated[list[araclar.IlacGrubu] | None, Field(description="Kullanılan ilaç grupları; ilaç adı gerekmez")] = None,
    mevcut_urunler: Annotated[list[str] | None, Field(description="Katalogdaki ürün adları")] = None,
    diger_urun_icerikleri: Annotated[
        list[araclar.DigerUrun] | None,
        Field(description="Katalogda olmayan ürünlerin etiketteki içerikleri"),
    ] = None,
) -> CallToolResult:
    return ozet.sonuc("kisisel_rutin", araclar.kisisel_rutin(yas, cinsiyet, evre, ilac_grubu, mevcut_urunler, diger_urun_icerikleri))


@mcp.tool(
    title="Yaşam karnesi",
    # MCP Apps: destekleyen istemcide karne seçenekli form olarak açılır; desteklemeyende metin seçeneklerine düşülür.
    meta={"ui": {"resourceUri": KARNE_ARAYUZU}},
    description=(
        "Hareket, uyku, sebze-meyve, balık, tütün ve dinlenme üzerine 6 soruluk testin karnesini çıkarır "
        "ve en fazla 3 hedef seçer. Cevaplar eksikse soruları döndürür. "
        "Kullanıcı yaşam tarzı testini yapmak istediğinde kullan."
    ),
    annotations=SALT_OKUMA,
)
def yasam_karnesi(
    cevaplar: Annotated[
        araclar.KarneCevaplari | None,
        Field(description="6 sorunun cevapları; sayısal sorularda sayı ya da seçenek kodu (ör. '1_2_gun')"),
    ] = None,
    yas: Annotated[int | None, Field(ge=0, le=120, description="İsteğe bağlı yaş")] = None,
) -> CallToolResult:
    return ozet.sonuc("yasam_karnesi", araclar.yasam_karnesi(cevaplar, yas))


@mcp.tool(
    title="Etken madde rehberi",
    description=(
        "Bir etken maddenin kanıt düzeyini, kimde kanıt olduğunu, güvenlik uyarılarını, EFSA üst sınırını ve "
        "etkileşimlerini kaynaklarıyla verir; kanıt kartı yoksa ürün listelemez. Kullan: bir maddenin işe yarayıp yaramadığı ya da kimlere uygun olduğu "
        "sorulduğunda. Kullanma: belirli bir ürün sorulduğunda."
    ),
    annotations=SALT_OKUMA,
)
def etken_madde_rehberi(
    etken_madde: Annotated[str, Field(description="Etken madde adı, ör. 'D vitamini', 'omega-3', 'magnezyum', 'multivitamin'")],
    yas: Annotated[int | None, Field(ge=0, le=120, description="İsteğe bağlı yaş (yıl)")] = None,
    cinsiyet: araclar.Cinsiyet | None = None,
    evre: Annotated[araclar.Evre | None, Field(description="İsteğe bağlı gebelik veya emzirme durumu")] = None,
    sigara: Annotated[araclar.Sigara | None, Field(description="İsteğe bağlı tütün kullanımı")] = None,
    ilac_grubu: Annotated[list[araclar.IlacGrubu] | None, Field(description="İsteğe bağlı ilaç grupları; ilaç adı gerekmez")] = None,
) -> CallToolResult:
    return ozet.sonuc("etken_madde_rehberi", araclar.etken_madde_rehberi(etken_madde, yas, cinsiyet, evre, sigara, ilac_grubu))


@mcp.tool(
    title="Şikâyet yolu",
    description=(
        "Kullanıcı bir yakınmadan (ör. yorgunluk, halsizlik) yola çıkıp ne kullanması gerektiğini sorduğunda önce "
        "bunu kullan. Dikkat edilecek işaretleri, hekimin isteyebileceği tahlilleri, yaşam karnesini ve ilgili kanıt "
        "kartlarını tek yanıtta verir; ürün önermez."
    ),
    annotations=SALT_OKUMA,
)
def sikayet_yolu(
    sikayet: Annotated[str, Field(description="Kullanıcının yakınması, ör. 'yorgunluk', 'hep yorgunum'")],
    yas: Annotated[int | None, Field(ge=0, le=120, description="İsteğe bağlı yaş (yıl)")] = None,
    cinsiyet: araclar.Cinsiyet | None = None,
) -> CallToolResult:
    return ozet.sonuc("sikayet_yolu", araclar.sikayet_yolu(sikayet, yas, cinsiyet))


@mcp.tool(
    title="Katalog sayfası (görsel kart)",
    description="Görsel kartın sayfalama için çağırdığı araçtır; modelden gizlidir. Kanıt kartı olmayan maddede ürün döndürmez.",
    annotations=SALT_OKUMA,
    meta=YALNIZCA_KART,
)
def katalog_sayfasi(
    etken_madde: Annotated[str, Field(description="Etken madde adı")],
    sayfa: Annotated[int, Field(ge=1, le=50, description="Sayfa numarası (her sayfada 5 ürün)")] = 1,
    yas: Annotated[int | None, Field(ge=0, le=120, description="İsteğe bağlı yaş; yaş sınırı dışındaki ürünler elenir")] = None,
) -> dict[str, Any]:
    return araclar.katalog_sayfasi(etken_madde, sayfa, yas)


@mcp.resource(
    KARNE_ARAYUZU,
    name="karne",
    title="Yaşam karnesi formu",
    description="Yaşam karnesi sorularını seçenekli form olarak gösterir ve sonucu kart olarak çizer.",
    mime_type=MCP_APP_MIME,
)
def karne_arayuzu() -> str:
    return arayuz.karne_html()


def main() -> None:
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
