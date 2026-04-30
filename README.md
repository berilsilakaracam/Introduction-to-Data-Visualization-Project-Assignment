# 🌐 NetViz — Otonom Ağ Topolojisi ve Anomali Görselleştirici

> **"Ağınızın röntgenini çeken, sorunları önceden gören gerçek zamanlı izleme platformu."**

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-5.22-green)](https://plotly.com)
[![NetworkX](https://img.shields.io/badge/NetworkX-3.3-orange)](https://networkx.org)

---

## 📌 Proje Özeti

NetViz, ağ mühendislerinin **yüzlerce cihazı tek ekrandan izleyebildiği**, trafik anomalilerini anlık tespit edebildiği ve makine öğrenmesi ile gelecekteki gecikmeleri tahmin edebildiği bir **veri görselleştirme uygulamasıdır**.

---

## 🔍 Neden Bu Proje? — Gerçek Hayat Problemi

Ağ mühendisleri her gün şu soruyla karşılaşır:

> *"Sistem neden yavaşladı? Hangi cihaz sorun çıkarıyor?"*

**Mevcut çözümlerin sorunları:**

| Yöntem | Sorun |
|---|---|
| Log dosyası okuma | Yüzlerce satır arasında sorun bulmak saatler alır |
| SolarWinds, PRTG | Lisans başına binlerce dolar — küçük şirketler için erişilemez |
| Manuel ping testi | Tek tek kontrol — gerçek zamanlı değil |

**NetViz'in çözümü:** Tüm ağı **tek ekranda, anlık, görsel olarak** göstermek. Sorun neredeyse orası kırmızıya döner.

---

## 📊 Veri Görselleştirme Neden Önemli?

Veri görselleştirme, ham verinin insan beyninin anlayabileceği görsel formata dönüştürülmesidir. Araştırmalar gösteriyor ki:

- 🧠 İnsan beyni görsel bilgiyi metinden **60.000 kat daha hızlı** işler
- 📉 Görselleştirme kullanan şirketlerde karar alma süresi **%28 azalır**
- 🔍 Anomali tespiti görsel sistemlerde **%73 daha hızlı** gerçekleşir

Ağ yönetiminde bu fark hayati önem taşır: **bir saniye bile kritik olabilir.**

---

## 🏗 Sistem Mimarisi ve Akış Diyagramı

```
┌─────────────────────────────────────────────────────────────┐
│                        KULLANICI                            │
│                    (Ağ Mühendisi)                           │
└──────────────────────────┬──────────────────────────────────┘
                           │ Tarayıcı (localhost:8501)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT ARAYÜZÜ                        │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │  Sidebar    │  │  Ana Panel   │  │   Detay Paneli    │  │
│  │  - Mod seç  │  │  - Topoloji  │  │   - Cihaz bilgi   │  │
│  │  - Eşik     │  │  - Isı harit │  │   - Gecikme graf  │  │
│  │  - CSV indr │  │  - Anomali   │  │   - Port listesi  │  │
│  └─────────────┘  └──────────────┘  └───────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
│   KEŞİF      │  │  GÖRSELLEŞ  │  │    TAHMİN        │
│  MOTORU      │  │  TİRME       │  │    MOTORİ        │
│              │  │              │  │                  │
│ Scapy (ARP)  │  │ NetworkX     │  │ Scikit-learn     │
│ ICMP Ping    │  │ (Graf yapısı)│  │ (LinReg modeli)  │
│ SNMP         │  │ Plotly       │  │ NumPy            │
│              │  │ (Görsel)     │  │                  │
└──────┬───────┘  └──────┬───────┘  └──────┬───────────┘
       │                 │                  │
       └─────────────────▼──────────────────┘
                         │
                ┌────────▼────────┐
                │   VERİ KATMANI  │
                │    Pandas       │
                │  (İşleme/Filtre)│
                └─────────────────┘
```

---

## ⚙️ Kullanılan Kütüphaneler ve Neden Seçildiler

### 🎯 Streamlit — Arayüz Katmanı
**Neden Streamlit?**
- `pip install streamlit` + `streamlit run app.py` — **2 komutla çalışır**
- Flask/Django gibi frontend kodu yazmayı gerektirmez
- Otomatik yenileme (rerun) mekanizması canlı veri için idealdir
- Slider, toggle, download butonu gibi bileşenler hazır gelir
- **Alternatif neden seçilmedi:** Dash (daha karmaşık), Gradio (ML odaklı, ağ için uygun değil)

### 🕸 NetworkX — Graf Teorisi
**Neden NetworkX?**
- Ağ cihazları doğası gereği **düğüm (node) ve kenar (edge)** yapısındadır
- NetworkX bu yapıyı matematiksel olarak temsil eder
- `spring_layout()` algoritması cihazları otomatik olarak mantıklı konumlara yerleştirir
- Bağlantı analizi, en kısa yol, merkezi düğüm tespiti kolayca yapılabilir
- **Alternatif neden seçilmedi:** PyVis (daha az kontrol), igraph (Python entegrasyonu zayıf)

### 📈 Plotly — İnteraktif Görselleştirme
**Neden Plotly?**
- **İnteraktif**: Hover, zoom, pan — kullanıcı grafikle etkileşime girebilir
- Streamlit ile yerel entegrasyon (`st.plotly_chart`)
- Renk, boyut, opaklık gibi parametreler veri bazlı değiştirilebilir
- **Alternatif neden seçilmedi:** Matplotlib (statik, interaktif değil), D3.js (JavaScript bilgisi gerekir)

### 🤖 Scikit-learn — Tahmin Motoru
**Neden Scikit-learn?**
- Gecikme verisi zaman serisi — **LinearRegression** trend tahmini için yeterlidir
- Basit, açıklanabilir model: hocanıza "şu formülü kullandım" diyebilirsiniz
- Kurumsal ortamda "explainable AI" önemlidir — karmaşık modeller şeffaf değildir
- **Alternatif neden seçilmedi:** TensorFlow/PyTorch (aşırı karmaşık, overkill), ARIMA (kurulum karmaşık)

### 🐍 Scapy — Ağ Keşfi
**Neden Scapy?**
- ARP paketleri göndererek ağdaki **tüm cihazları 3 saniyede** tespit eder
- MAC adresi, IP, cihaz tipi bilgilerini doğrudan ağdan çeker
- Nmap'e göre daha hafif, Python native
- **Alternatif:** Root yetkisi yoksa ICMP ping fallback devreye girer

---

## 🏢 Endüstri Perspektifi

| Özellik | NetViz Pro | SolarWinds | Grafana |
|---|---|---|---|
| Kurulum | 2 komut | Haftalarca | Günlerce |
| Maliyet | Ücretsiz | $10,000+/yıl | Ücretsiz |
| AI Tahmin | ✅ LinReg | ❌ | Eklenti |
| IP Konum | ✅ Otomatik | ❌ | ❌ |
| Çözüm Önerisi | ✅ Komutlu | ❌ | ❌ |
| Özelleştirme | Tam kontrol | Sınırlı | Orta |

## 🔄 Veri Akış Diyagramı

```
Ağ Cihazları
     │
     │ ARP / ICMP
     ▼
┌─────────────┐
│  Scapy ile  │──► IP, MAC, Hostname listesi
│  Tarama     │
└─────────────┘
     │
     ▼
┌─────────────┐
│   Pandas    │──► Veriyi DataFrame'e al, filtrele, normalize et
│  İşleme     │
└─────────────┘
     │
     ├──────────────────────┐
     ▼                      ▼
┌─────────────┐      ┌─────────────┐
│  NetworkX   │      │ Scikit-learn│
│  Graf oluşt │      │ Regresyon   │
└──────┬──────┘      └──────┬──────┘
       │                    │
       ▼                    ▼
┌─────────────┐      ┌─────────────┐
│   Plotly    │      │  Forecast   │
│  Topoloji   │      │  Grafiği    │
└──────┬──────┘      └──────┬──────┘
       │                    │
       └──────────┬──────────┘
                  ▼
           Streamlit UI
           (localhost:8501)
```
## 🗺 Sistem Akış Diyagramı

```mermaid
flowchart TD
    A[👤 Ağ Mühendisi] -->|Tarayıcı localhost:8501| B[⚡ NetViz Pro Arayüzü]

    B --> C[🔍 Keşif Motoru]
    B --> D[📊 Görselleştirme]
    B --> E[🤖 Tahmin Motoru]
    B --> F[🌍 Konum Servisi]

    C -->|ARP / ICMP Ping| C1[Scapy]
    C1 -->|IP, MAC, Hostname| G[🐼 Pandas\nVeri İşleme]

    G --> D
    G --> E
    G --> H[🚨 Anomali Dedektörü]

    D -->|Graf yapısı| D1[NetworkX]
    D1 -->|İnteraktif görsel| D2[Plotly]
    D2 --> D3[🌐 Topoloji Haritası]
    D2 --> D4[🔥 Isı Haritası]

    E -->|Zaman serisi| E1[Scikit-learn\nLinearRegression]
    E1 --> E2[📈 Gecikme Tahmini\n+10 dakika]

    H -->|Eşik aşımı| H1[💡 Çözüm Önerisi\nTerminal komutu ile]

    F -->|Dış IP otomatik| F1[ip-api.com]
    F1 --> F2[🗺 Dünya Haritası\nGateway Konumu]
    F -->|Manuel IP giriş| F3[🔍 IP Sorgulama\nHarita]

    D3 --> B
    D4 --> B
    E2 --> B
    H1 --> B
    F2 --> B
    F3 --> B
---

## 🏢 Endüstri Perspektifi — Gerçek Hayatta Ne Kullanılıyor?

Staj/çalışma deneyimimden edindiğim gözlemler:

**Büyük şirketlerin kullandığı araçlar:**
- **Grafana + Prometheus:** Metrik toplama ve görselleştirme (açık kaynak, yaygın)
- **SolarWinds:** Kurumsal ağ izleme ($10,000+/yıl lisans)
- **Cisco DNA Center:** Cisco altyapısı için (donanıma bağlı)
- **Elastic Stack (ELK):** Log analizi ve görselleştirme

**NetViz'in bu araçlardan farkı:**
| Özellik | NetViz | SolarWinds | Grafana |
|---|---|---|---|
| Kurulum | 2 komut | Haftalarca | Günlerce |
| Maliyet | Ücretsiz | $10,000+ | Ücretsiz |
| Özelleştirme | Tam kontrol | Sınırlı | Orta |
| Öğrenme eğrisi | Düşük | Yüksek | Orta |
| AI Tahmin | ✅ | ❌ | Eklenti |

**Endüstrinin NetViz'den öğrenebileceği:**
> Kurumsal araçların karmaşıklığı ve maliyeti, küçük-orta ölçekli şirketleri dışlamaktadır. Python tabanlı açık kaynak araçlar, bu boşluğu doldurmaya başlamıştır. NetViz bu trendin somut bir örneğidir.

---

## 🚀 Gelecek İyileştirmeler

Proje aktif geliştirilmeye devam etmektedir. Planlanan özellikler:

### 🔧 Teknik İyileştirmeler
- [ ] **SNMP v3 entegrasyonu** — gerçek CPU/RAM/bant kullanımı çekme
- [ ] **WebSocket ile gerçek zamanlı** veri akışı (Streamlit rerun yerine)
- [ ] **InfluxDB entegrasyonu** — zaman serisi veritabanı ile geçmiş saklama
- [ ] **Docker container** — `docker run netviz` ile tek komut kurulum

### 🤖 Yapay Zeka İyileştirmeleri
- [ ] **LSTM modeli** — daha doğru gecikme tahmini
- [ ] **Isolation Forest** — daha gelişmiş anomali tespiti
- [ ] **Graf Sinir Ağları (GNN)** — topoloji tabanlı tahmin

### 🎨 Arayüz İyileştirmeleri
- [ ] **E-posta/SMS bildirimi** — kritik anomalilerde otomatik uyarı
- [ ] **Mobil uyumlu** tasarım
- [ ] **Çoklu ağ** desteği (birden fazla subnet)

---

## 🛠 Kurulum

```bash
# 1. Repoyu klonla
git clone https://github.com/berilsilakaracam/Introduction-to-Data-Visualization-Project-Assignment.git
cd Introduction-to-Data-Visualization-Project-Assignment

# 2. Bağımlılıkları kur
pip install streamlit plotly networkx scikit-learn pandas scapy

# 3. Çalıştır
streamlit run app.py
```

Tarayıcıda `http://localhost:8501` açılır.

---

## 📁 Dosya Yapısı

```
├── app.py              # Ana uygulama (Streamlit + Plotly + NetworkX)
├── requirements.txt    # Python bağımlılıkları
├── README.md           # Bu dosya

```

---

## 👩‍💻 Geliştirici

**Beril Sila Karacam**
OSTECH — Veri Görselleştirme Dersi
2025-2026 Akademik Yılı

---

*Bu proje, veri görselleştirmenin ağ yönetimindeki kritik rolünü ve Python ekosisteminin bu alanda sunduğu imkânları göstermek amacıyla geliştirilmiştir.*
