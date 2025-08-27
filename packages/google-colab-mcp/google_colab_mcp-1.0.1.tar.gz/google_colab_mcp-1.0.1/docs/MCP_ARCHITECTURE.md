# Google Colab MCP Server - Architecture Documentation

## Model Context Protocol (MCP) Overview

Bu proje, Google Colab ile entegrasyon sağlayan bir MCP (Model Context Protocol) server implementasyonudur. MCP, AI uygulamaları ile harici veri kaynakları ve araçlar arasında standart bir iletişim protokolü sağlar.

### MCP Mimarisi

MCP, JSON-RPC 2.0 tabanlı bir protokol olup iki katmandan oluşur:

1. **Data Layer (Veri Katmanı)**: JSON-RPC mesaj yapısı ve semantiği
2. **Transport Layer (Taşıma Katmanı)**: İletişim kanalları ve kimlik doğrulama

### Temel Bileşenler

#### MCP Host (Ana Bilgisayar)
- AI uygulaması (VS Code, Claude Desktop, vb.)
- Bir veya birden fazla MCP client'ı yönetir

#### MCP Client (İstemci)
- MCP server ile bağlantı kuran bileşen
- Her server için ayrı bir client instance'ı

#### MCP Server (Sunucu)
- Bağlam verisi sağlayan program
- Bu projede: Google Colab entegrasyonu

### MCP Primitives (Temel Öğeler)

1. **Tools**: AI'ın çağırabileceği fonksiyonlar
   - `create_colab_notebook`
   - `run_code_cell`
   - `install_package`
   - `list_notebooks`
   - vb.

2. **Resources**: Bağlamsal bilgi kaynakları
   - Notebook içerikleri
   - Çalışma zamanı bilgileri
   - Oturum durumları

3. **Prompts**: Yeniden kullanılabilir şablonlar (bu projede kullanılmıyor)

### Transport Mechanisms

#### STDIO Transport
- Standart giriş/çıkış akışları kullanır
- Yerel süreçler arası iletişim
- Bu projede kullanılan yöntem

#### Streamable HTTP Transport
- HTTP POST istekleri
- Uzak sunucu iletişimi
- Server-Sent Events desteği

## Proje Yapısı

```
google-colab-mcp/
├── src/
│   ├── mcp_server.py          # Ana MCP server implementasyonu
│   ├── auth_manager.py        # Google API kimlik doğrulama
│   ├── colab_drive.py         # Google Drive API entegrasyonu
│   ├── colab_selenium.py      # Selenium otomasyon
│   ├── session_manager.py     # Oturum yönetimi
│   └── utils.py               # Yardımcı fonksiyonlar
├── config/
│   ├── server_config.json     # Server konfigürasyonu
│   └── credentials.json       # Google API kimlik bilgileri
├── mcp_config_*.json          # MCP client konfigürasyonları
└── run_server.py              # Server başlatma scripti
```

## Konfigürasyon Dosyaları

### 1. mcp_config_example.json
Temel örnek konfigürasyon

### 2. mcp_config_production.json
Üretim ortamı için optimize edilmiş konfigürasyon
- Debug logging aktif
- Selenium headless modu kapalı
- Genişletilmiş timeout değerleri

### 3. mcp_config_advanced.json
Gelişmiş özelliklerle tam konfigürasyon
- Güvenlik ayarları
- Monitoring desteği
- Log rotation
- Performans optimizasyonları

### 4. mcp_config_test.json
Test amaçlı minimal konfigürasyon

## Kullanım

### 1. Konfigürasyon Seçimi
İhtiyacınıza göre uygun config dosyasını seçin:

```bash
# Test için
cp mcp_config_test.json .kiro/settings/mcp.json

# Üretim için
cp mcp_config_production.json .kiro/settings/mcp.json

# Gelişmiş özellikler için
cp mcp_config_advanced.json .kiro/settings/mcp.json
```

### 2. Server Başlatma
```bash
python run_server.py
```

### 3. VS Code/Kiro Entegrasyonu
Config dosyasını `.kiro/settings/mcp.json` konumuna kopyalayın ve Kiro'yu yeniden başlatın.

## Güvenlik Özellikleri

- Google OAuth 2.0 kimlik doğrulama
- Otomatik onay listesi (autoApprove)
- İstek boyutu sınırlaması
- Timeout koruması
- Hata yakalama ve loglama

## Monitoring ve Debugging

- Detaylı loglama sistemi
- Health check endpoint'i
- Metrics toplama
- Session tracking
- Error reporting

## Best Practices

1. **Güvenlik**: Hassas bilgileri environment variable'larda saklayın
2. **Performance**: Headless modu üretimde kullanın
3. **Monitoring**: Log seviyesini ortama göre ayarlayın
4. **Reliability**: Retry mekanizmalarını aktif tutun
5. **Maintenance**: Session cleanup'ı düzenli yapın

## Troubleshooting

### Yaygın Sorunlar

1. **Authentication Error**: `credentials.json` dosyasını kontrol edin
2. **Selenium Timeout**: Browser driver'ları güncelleyin
3. **Connection Failed**: Network bağlantısını kontrol edin
4. **Permission Denied**: Google Drive API izinlerini kontrol edin

### Debug Modu

```json
{
  "env": {
    "COLAB_MCP_LOG_LEVEL": "DEBUG",
    "COLAB_SELENIUM_HEADLESS": "false"
  }
}
```

Bu ayarlarla detaylı loglar ve görsel browser etkileşimi sağlanır.