"""Takviye Bilimi MCP sunucusu (Streamable HTTP, /mcp)."""

from __future__ import annotations

import hmac
import os
from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import CallToolResult, ToolAnnotations
from pydantic import Field
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, Response

from . import araclar, arayuz, ozet, veri
from . import sayac as sayac_mod

# v0.3 Bölüm 2: sunucu yönergesi (initialize yanıtındaki instructions). Tahlil satırı v0.3 listesinde olmayan
# tahlil_goster aracı içindir.
TALIMATLAR = """Takviye Bilimi — takviye edici gıdalar, vitaminler ve mineraller için kaynaklı, Türkçe kanıt rehberi. Orzax tarafından geliştirildi; ürün kataloğu şu an yalnızca Orzax ürünlerini içerir.
Yönlendirme:
- Yakınma (yorgunluk, dökülme, kramp, uykusuzluk…) → sikayet_yolu
- Hedef, mevsim, yaşam evresi ya da genel "ne almalıyım" → takviye_rehberi
- Tek madde ("D vitamini işe yarar mı / kullanmalı mıyım") → önce takviye_rehberi(etken_madde=…); kullanıcı kartı ya da ayrıntıyı isterse etken_madde_rehberi
- Tek ürünün etiketi, kullanımı, yaş sınırı → urun_rehberi
- Ürün / marka / form kıyası → karsilastir
- Birden fazla takviye birlikte, toplam miktar, ilaç etkileşimi → kisisel_rutin
- Yaşam tarzı değerlendirmesi, sağlık hedefi → yasam_karnesi
- Karekod ya da parti numarası → parti_analizi
- Tahlil sonucunu anlama (B12, ferritin, D vitamini) → tahlil_goster
Kurallar: Doz önerme; etiketteki kullanımı ve "hekiminize danışın" notunu aktar. Ürün listesini öneri gibi sunma. Yaş aralığı, gebelik/emzirme ve ilaç grubu eksikse seçenekli sor. Kapı araçlarının köprü sorusunu kullanıcıya ilet; kullanıcı isterse kartlı aracı çağır. Elektronik tablo veya dosya üretme; cevabı sohbette ver."""
# Görsel kartın kendi çağırdığı, modelden gizlenen araçlar (MCP Apps).
YALNIZCA_KART = {"ui": {"visibility": ["app"]}}
KARNE_ARAYUZU = "ui://takviye-bilimi/karne"
KANIT_ARAYUZU = "ui://takviye-bilimi/kanit"
URUN_ARAYUZU = "ui://takviye-bilimi/urun"
RUTIN_ARAYUZU = "ui://takviye-bilimi/rutin"
KIYAS_ARAYUZU = "ui://takviye-bilimi/kiyas"
PARTI_ARAYUZU = "ui://takviye-bilimi/parti"
TAHLIL_ARAYUZU = "ui://takviye-bilimi/tahlil"
MCP_APP_MIME = "text/html;profile=mcp-app"
SURUM = "0.3.0"
WEB_ADRESI = os.environ.get("TB_WEB_ADRESI", "https://www.orzax.com.tr/")


def _salt_okuma(baslik: str) -> ToolAnnotations:
    """v0.3 Bölüm 6: tüm araçlar salt okunur, yıkıcı değil, aynı girdiye aynı yanıt, dış dünyaya kapalı."""
    return ToolAnnotations(title=baslik, readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)


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
    # serverInfo.name: SDK 1.30 serverInfo.title göndermediği için istemcide görünen ad burada kalır (v0.3 Bölüm 7.3
    # "takviye-bilimi" adı, title alanı desteklenince geçilecek).
    name="Takviye Bilimi",
    instructions=TALIMATLAR,
    website_url=WEB_ADRESI,
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
# serverInfo.version (v0.3 Bölüm 7.3).
mcp._mcp_server.version = SURUM


def _yanit(arac: str, v: dict, **sayac) -> CallToolResult:
    """Modele kısa özet, karta tam veri; toplu sayaç (kişisel veri yok)."""
    sayac_mod.kaydet(arac, v, **sayac)
    return ozet.sonuc(arac, v)


# v0.3 Bölüm 3: araç açıklamaları birebir (Ne yapar → Kullan → Örnek kullanıcı cümleleri → Kullanma).
ACIKLAMALAR = {
    "takviye_rehberi": "Kullanıcı bir hedef, mevsim ya da yaşam evresiyle, ya da \"hangi takviyeyi almalıyım / X kullanmalı mıyım\" gibi genel bir soruyla geldiğinde ilk bunu kullan. İlgili etken maddeleri, her birinin kısa kanıt özetini ve kanıt kartı durumunu, güvenlik notlarını, besinle karşılama notunu ve eksik profil sorularını tek yanıtta verir; ürün önermez. Sonuç bir köprü sorusuyla biter.\nÖrnek kullanıcı cümleleri: «Kış geldi, hangi vitaminleri almam gerek?» «Bağışıklığımı güçlendirmek için ne kullanmalıyım?» «Hamilelik planlıyoruz, hangi takviyeler önemli?» «50 yaşını geçtim, nelere dikkat etmeliyim?» «Veganım, eksik kalabileceğim bir şey var mı?» «Spor yapıyorum, takviye gerekli mi?» «D vitamini kullanmalı mıyım?» «Omega-3 işe yarıyor mu?»\nKullanma: yakınma varsa → sikayet_yolu; belirli ürün → urun_rehberi; ürün kıyası → karsilastir.",
    "sikayet_yolu": "Kullanıcı bir yakınmadan yola çıkıp ne kullanması gerektiğini sorduğunda önce bunu kullan. Dikkat edilecek işaretleri, hekimin isteyebileceği tahlilleri, yaşam karnesi bağlantısını ve ilgili maddelerin kısa kanıt özetini verir; ürün önermez. Sonuç bir köprü sorusuyla biter.\nÖrnek kullanıcı cümleleri: «Hep yorgunum, ne kullanayım?» «Saçlarım çok dökülüyor, hangi vitamin iyi gelir?» «Gece bacaklarıma kramp giriyor.» «Halsizim, takviye işe yarar mı?» «Uykularım düzensiz, ne alabilirim?»\nKullanma: yakınma yoksa, hedef ya da mevsim sorusu → takviye_rehberi.",
    "etken_madde_rehberi": "Bir etken maddenin kanıt kartını gösterir: kanıt düzeyi, 100 kişide mutlak fark, kimde kanıt olduğu, güvenlik uyarıları, yaş grubuna göre EFSA üst sınırı, etkileşimler ve kaynaklar. Kullan: kullanıcı bir maddenin kanıtını ya da ayrıntısını istediğinde veya takviye_rehberi / sikayet_yolu köprüsüne \"evet\" dediğinde.\nÖrnek kullanıcı cümleleri: «D vitamini gerçekten işe yarıyor mu, araştırmalar ne diyor?» «Omega-3 kimde işe yarıyor?» «Magnezyumun uykuya etkisi kanıtlı mı?» «Kan sulandırıcı kullanıyorum, K2 içeren ürün kullanabilir miyim?» «Gebeyim, folik asit neden önemli?»\nKullanma: ürün sorusu → urun_rehberi; genel ya da hedef sorusu → takviye_rehberi.",
    "urun_rehberi": "Katalogdaki tek bir ürünün etiket bilgisini verir: etken madde miktarları, BRD, bileşim, etiketteki kullanım, yaş sınırı, ürün sayfası beyanları ve parti analizi durumu. Katalog şu an yalnızca Orzax ürünlerini içerir.\nÖrnek kullanıcı cümleleri: «Ocean D3K2 Damla nasıl kullanılır?» «8 yaşındaki kızıma Ocean Vitamin D3 sprey verebilir miyim?» «Ocean Vitamin D3 1000 IU damlada ne kadar D vitamini var?» «Bu ürün kaç yaşından itibaren kullanılır?» «Kutudaki ürünün içeriğini açıklar mısın?»\nKullanma: birden fazla ürün → karsilastir; katalog dışı marka → karsilastir (kapsam mesajı) ya da etiket içeriği girilerek kisisel_rutin.",
    "karsilastir": "Bir etken maddeyi içeren katalog ürünlerini etikete göre tek tabloda kıyaslar: form, porsiyondaki miktar, BRD, yaş grubuna göre EFSA sınırına oran, ek etken maddeler, yaş sınırı ve etkileşim bayrakları. Sıralama öneri değildir; fiyat ya da sponsorluk yoktur. Katalog şu an yalnızca Orzax ürünlerini içerir.\nÖrnek kullanıcı cümleleri: «D vitamini markalarını içeriklerine göre kıyaslar mısın?» «Sprey mi damla mı, D vitamini ürünleri arasındaki fark ne?» «Çocuğum için hangi D vitamini ürünleri var?» «K2'li ve K2'siz D vitamini farkı ne?» «Magnezyum ürünlerini içeriğe göre sırala.»\nKullanma: tek ürün → urun_rehberi; maddenin işe yarayıp yaramadığı → takviye_rehberi.",
    "kisisel_rutin": "Kullanıcının birlikte kullandığı takviyeleri kontrol eder: tekrar eden etken madde, toplam miktarın EFSA üst sınırına oranı, etiket uyarıları, ilaç grubu etkileşimleri ve hekime sorulacaklar. Doz önermez. Katalog dışı ürünler etiketteki içerikleriyle girilebilir.\nÖrnek kullanıcı cümleleri: «D vitamini, multivitamin ve kalsiyumu birlikte kullanıyorum, fazla mı?» «Annem varfarin kullanıyor, takviyelerine bakar mısın?» «Omega-3 ile magnezyumu birlikte alabilir miyim?» «Çocuğumun vitaminlerini toplasak sınırı aşıyor mu?» «Sabah içtiğim takviyeleri kontrol et.»\nKullanma: tek maddenin kanıtı → etken_madde_rehberi.",
    "yasam_karnesi": "Hareket, uyku, sebze-meyve, balık, tütün ve stres üzerine 6 soruluk yaşam karnesini çıkarır; en fazla 3 hedef ve her biri için ilk adımı verir. Cevaplar eksikse soruları seçenekleriyle döndürür; soruları iki adımda, seçenekli sor.\nÖrnek kullanıcı cümleleri: «Sağlıklı yaşıyor muyum?» «Yaşam tarzımı puanlar mısın?» «Takviyeden önce neyi değiştirmeliyim?» «Uyku ve beslenme alışkanlıklarımı değerlendir.» «Kendime küçük sağlık hedefleri koymak istiyorum.»\nKullanma: belirli bir yakınma → sikayet_yolu.",
    "parti_analizi": "Kutudaki karekod içeriğinden ya da parti numarasından yayımlanmış parti analizini arar. Şu an yayımlanmış analiz yoktur; araç bunu bildirir.\nÖrnek kullanıcı cümleleri: «Karekodu okuttum: https://…» «Bu ürünün parti analizi var mı? Parti no: …» «Aldığım kutunun analiz sonuçlarını görebilir miyim?»"
}


@mcp.tool(
    title="Takviye Rehberi",
    description=ACIKLAMALAR["takviye_rehberi"],
    annotations=_salt_okuma("Takviye Rehberi"),
)
def takviye_rehberi(
    konu: Annotated[str, Field(description="Kullanıcının cümlesi ya da özeti, ör. 'kış', 'bağışıklık', 'D vitamini kullanmalı mıyım'")],
    hedef: Annotated[araclar.Hedef | None, Field(description="İsteğe bağlı hedef kodu; verilmezse konudan bulunur")] = None,
    etken_madde: Annotated[str | None, Field(description="Tek madde sorusu için madde adı, ör. 'D vitamini'")] = None,
    yas: Annotated[int | None, Field(ge=0, le=120, description="İsteğe bağlı yaş (yıl)")] = None,
    cinsiyet: araclar.Cinsiyet | None = None,
    evre: Annotated[araclar.Evre | None, Field(description="İsteğe bağlı gebelik veya emzirme durumu")] = None,
    ilac_grubu: Annotated[list[araclar.IlacGrubu] | None, Field(description="İsteğe bağlı ilaç grupları; ilaç adı gerekmez")] = None,
) -> CallToolResult:
    v = araclar.takviye_rehberi(konu, hedef, etken_madde, yas, cinsiyet, evre, ilac_grubu)
    return _yanit("takviye_rehberi", v, etken_madde=etken_madde, yas=yas)


@mcp.tool(
    title="Şikâyet Yolu",
    description=ACIKLAMALAR["sikayet_yolu"],
    annotations=_salt_okuma("Şikâyet Yolu"),
)
def sikayet_yolu(
    sikayet: Annotated[str, Field(description="Kullanıcının yakınması, ör. 'yorgunluk', 'hep yorgunum'")],
    yas: Annotated[int | None, Field(ge=0, le=120, description="İsteğe bağlı yaş (yıl)")] = None,
    cinsiyet: araclar.Cinsiyet | None = None,
) -> CallToolResult:
    return _yanit("sikayet_yolu", araclar.sikayet_yolu(sikayet, yas, cinsiyet), yas=yas)


@mcp.tool(
    title="Parti Analizi",
    # Not (v0.3 Bölüm 1 ile çelişki, raporlandı): kapı aracı olduğu hâlde parti kartı bağlı; v0.4 B2 gereği değiştirilmedi.
    meta={"ui": {"resourceUri": PARTI_ARAYUZU}},
    description=ACIKLAMALAR["parti_analizi"],
    annotations=_salt_okuma("Parti Analizi"),
)
def parti_analizi(
    karekod_veya_parti_no: Annotated[str, Field(description="Karekod içeriği (URL veya GS1 metni) ya da parti numarası")],
) -> CallToolResult:
    return _yanit("parti_analizi", araclar.parti_analizi(karekod_veya_parti_no))


@mcp.tool(
    title="Kanıt Kartı",
    meta={"ui": {"resourceUri": KANIT_ARAYUZU}},
    description=ACIKLAMALAR["etken_madde_rehberi"],
    annotations=_salt_okuma("Kanıt Kartı"),
)
def etken_madde_rehberi(
    etken_madde: Annotated[str, Field(description="Etken madde adı, ör. 'D vitamini', 'omega-3', 'magnezyum', 'multivitamin'")],
    yas: Annotated[int | None, Field(ge=0, le=120, description="İsteğe bağlı yaş (yıl)")] = None,
    cinsiyet: araclar.Cinsiyet | None = None,
    evre: Annotated[araclar.Evre | None, Field(description="İsteğe bağlı gebelik veya emzirme durumu")] = None,
    sigara: Annotated[araclar.Sigara | None, Field(description="İsteğe bağlı tütün kullanımı")] = None,
    ilac_grubu: Annotated[list[araclar.IlacGrubu] | None, Field(description="İsteğe bağlı ilaç grupları; ilaç adı gerekmez")] = None,
) -> CallToolResult:
    v = araclar.etken_madde_rehberi(etken_madde, yas, cinsiyet, evre, sigara, ilac_grubu)
    return _yanit("etken_madde_rehberi", v, etken_madde=etken_madde, yas=yas)


@mcp.tool(
    title="Ürün Etiketi",
    meta={"ui": {"resourceUri": URUN_ARAYUZU}},
    description=ACIKLAMALAR["urun_rehberi"],
    annotations=_salt_okuma("Ürün Etiketi"),
)
def urun_rehberi(
    urun: Annotated[str, Field(description="Ürün adı, ör. 'Ocean D3K2 Damla'")],
    yas: Annotated[int | None, Field(ge=0, le=120, description="İsteğe bağlı: ürünü kullanacak kişinin yaşı")] = None,
) -> CallToolResult:
    return _yanit("urun_rehberi", araclar.urun_rehberi(urun, yas), yas=yas)


@mcp.tool(
    title="Ürün Kıyası",
    meta={"ui": {"resourceUri": KIYAS_ARAYUZU}},
    description=ACIKLAMALAR["karsilastir"],
    annotations=_salt_okuma("Ürün Kıyası"),
)
def karsilastir(
    etken_madde: Annotated[str, Field(description="Kıyaslanacak etken madde, ör. 'D vitamini', 'magnezyum'")],
    form: Annotated[araclar.Form | None, Field(description="İsteğe bağlı form süzgeci")] = None,
    yas: Annotated[int | None, Field(ge=0, le=120, description="İsteğe bağlı yaş; EFSA sınırı o yaş grubuna göre alınır")] = None,
    sadece_tek_bilesen: Annotated[bool, Field(description="Yalnızca bu maddeyi tek başına içeren ürünler")] = False,
    marka: Annotated[str | None, Field(description="İsteğe bağlı marka; katalog dışı markada kapsam mesajı döner")] = None,
    ilac_grubu: Annotated[list[araclar.IlacGrubu] | None, Field(description="İsteğe bağlı ilaç grupları; eşleşen bayrak kırmızı olur")] = None,
    sayfa: Annotated[int, Field(ge=1, le=20, description="40 üründen fazlası için sayfa")] = 1,
) -> CallToolResult:
    v = araclar.karsilastir(etken_madde, form, yas, sadece_tek_bilesen, marka, ilac_grubu, sayfa)
    return _yanit("karsilastir", v, etken_madde=etken_madde, yas=yas)


@mcp.tool(
    title="Rutin Kontrolü",
    meta={"ui": {"resourceUri": RUTIN_ARAYUZU}},
    description=ACIKLAMALAR["kisisel_rutin"],
    annotations=_salt_okuma("Rutin Kontrolü"),
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
    v = araclar.kisisel_rutin(yas, cinsiyet, evre, ilac_grubu, mevcut_urunler, diger_urun_icerikleri)
    return _yanit("kisisel_rutin", v, yas=yas)


@mcp.tool(
    title="Yaşam Karnesi",
    # MCP Apps: destekleyen istemcide karne seçenekli form olarak açılır; desteklemeyende metin seçeneklerine düşülür.
    meta={"ui": {"resourceUri": KARNE_ARAYUZU}},
    description=ACIKLAMALAR["yasam_karnesi"],
    annotations=_salt_okuma("Yaşam Karnesi"),
)
def yasam_karnesi(
    cevaplar: Annotated[
        araclar.KarneCevaplari | None,
        Field(description="6 sorunun cevapları; sayısal sorularda sayı ya da seçenek kodu (ör. '1_2_gun')"),
    ] = None,
    yas: Annotated[int | None, Field(ge=0, le=120, description="İsteğe bağlı yaş")] = None,
) -> CallToolResult:
    return _yanit("yasam_karnesi", araclar.yasam_karnesi(cevaplar, yas), yas=yas)


@mcp.tool(
    title="Tahlil Görünümü",
    meta={"ui": {"resourceUri": TAHLIL_ARAYUZU}},
    description=(
        "Kullanıcı B12, ferritin ya da D vitamini tahlil sonucunu anlamak istediğinde kartı açar. Değer araca gönderilmez; "
        "kullanıcı değerini ve raporundaki referans aralığını kartta, kendi cihazında girer. Tahmin ve doz vermez."
    ),
    annotations=_salt_okuma("Tahlil Görünümü"),
)
def tahlil_goster(
    tahlil: Annotated[str, Field(description="Tahlil adı: 'B12', 'ferritin' ya da 'D vitamini'. Değer yazılmaz.")],
) -> CallToolResult:
    return _yanit("tahlil_goster", araclar.tahlil_goster(tahlil))


@mcp.tool(
    title="Katalog sayfası (görsel kart)",
    description="Görsel kartın sayfalama için çağırdığı araçtır; modelden gizlidir. Kanıt kartı olmayan maddede ürün döndürmez.",
    annotations=_salt_okuma("Katalog Sayfası"),
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


@mcp.resource(
    KANIT_ARAYUZU,
    name="kanit",
    title="Kanıt kartı",
    description="Etken maddenin kanıt düzeyini, 100 kişilik ikon dizisini, güvenlik uyarılarını ve katalogu kart olarak gösterir.",
    mime_type=MCP_APP_MIME,
)
def kanit_arayuzu() -> str:
    return arayuz.kart_html("kanit")


@mcp.resource(
    URUN_ARAYUZU,
    name="urun",
    title="Ürün kartı",
    description="Ürünün etiket bilgisini, EFSA sınır göstergesini ve ürün sayfası beyanlarını kart olarak gösterir.",
    mime_type=MCP_APP_MIME,
)
def urun_arayuzu() -> str:
    return arayuz.kart_html("urun")


@mcp.resource(
    RUTIN_ARAYUZU,
    name="rutin",
    title="Rutin kartı",
    description="Takviyelerden toplam alımı ürün başına yığılmış çubuk ve EFSA çizgisiyle, uyarıları rozetlerle gösterir.",
    mime_type=MCP_APP_MIME,
)
def rutin_arayuzu() -> str:
    return arayuz.kart_html("rutin")


@mcp.resource(
    KIYAS_ARAYUZU,
    name="kiyas",
    title="Kıyas kartı",
    description="Bir maddeyi içeren katalog ürünlerini etiket ölçütleriyle tabloda gösterir; form çipleri, EFSA çubuğu, etkileşim rozetleri.",
    mime_type=MCP_APP_MIME,
)
def kiyas_arayuzu() -> str:
    return arayuz.kart_html("kiyas")


@mcp.resource(
    PARTI_ARAYUZU,
    name="parti",
    title="Parti kartı",
    description="Parti analizinde etiketteki ve ölçülen miktarı, laboratuvarı ve tarihi gösterir; demo kayıtlar etiketlidir.",
    mime_type=MCP_APP_MIME,
)
def parti_arayuzu() -> str:
    return arayuz.kart_html("parti")


@mcp.resource(
    TAHLIL_ARAYUZU,
    name="tahlil",
    title="Tahlil kartı",
    description="Kullanıcının kendi değerini kendi laboratuvarının referans aralığında gösterir; değer cihazda kalır.",
    mime_type=MCP_APP_MIME,
)
def tahlil_arayuzu() -> str:
    return arayuz.kart_html("tahlil")


@mcp.custom_route("/sayaclar", methods=["GET"])
async def sayaclar(istek: Request) -> Response:
    """Toplu sayaçlar (v0.3 Bölüm 11). TB_SAYAC_ANAHTARI tanımlı değilse adres yoktur."""
    anahtar = os.environ.get("TB_SAYAC_ANAHTARI")
    if not anahtar:
        return PlainTextResponse("Not Found", status_code=404)
    if not hmac.compare_digest(istek.headers.get("authorization", ""), f"Bearer {anahtar}"):
        return PlainTextResponse("Unauthorized", status_code=401)
    return JSONResponse(sayac_mod.rapor())


def main() -> None:
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
