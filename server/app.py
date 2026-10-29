"""Takviye Bilimi MCP sunucusu (Streamable HTTP, /mcp)."""

from __future__ import annotations

import os
from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations
from pydantic import Field

from . import araclar

TALIMATLAR = (
    "Takviye Bilimi, takviye edici gıdalar hakkında Türkçe, markadan bağımsız etiket ve kanıt bilgisi sunar. "
    "Orzax tarafından geliştirilmiştir. Araçları yalnızca takviye ürünleri, takviye rutini, parti analizi "
    "veya yaşam tarzı karnesiyle ilgili sorularda çağır. Tanı koyma, kişiye doz önerme, belirli bir ürünü "
    "alması gerektiğini söyleme. Her yanıtta 'uyari' alanındaki notu kullanıcıya ilet."
)

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
) -> dict[str, Any]:
    return araclar.urun_rehberi(urun)


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
) -> dict[str, Any]:
    return araclar.parti_analizi(karekod_veya_parti_no)


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
) -> dict[str, Any]:
    return araclar.kisisel_rutin(yas, cinsiyet, evre, ilac_grubu, mevcut_urunler, diger_urun_icerikleri)


@mcp.tool(
    title="Yaşam karnesi",
    description=(
        "Hareket, uyku, sebze-meyve, balık, tütün ve dinlenme üzerine 6 soruluk testin karnesini çıkarır "
        "ve en fazla 3 hedef seçer. Cevaplar eksikse soruları döndürür. "
        "Kullanıcı yaşam tarzı testini yapmak istediğinde kullan."
    ),
    annotations=SALT_OKUMA,
)
def yasam_karnesi(
    cevaplar: Annotated[araclar.KarneCevaplari | None, Field(description="6 sorunun cevapları")] = None,
    yas: Annotated[int | None, Field(ge=0, le=120, description="İsteğe bağlı yaş")] = None,
) -> dict[str, Any]:
    return araclar.yasam_karnesi(cevaplar, yas)


def main() -> None:
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
