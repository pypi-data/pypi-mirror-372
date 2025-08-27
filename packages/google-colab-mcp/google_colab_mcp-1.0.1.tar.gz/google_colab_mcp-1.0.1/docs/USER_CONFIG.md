# 🔧 User Configuration Guide

MCP Colab Server artık kullanıcı bazlı konfigürasyon sistemi kullanıyor. Bu, her kullanıcının kendi credentials ve ayarlarını ayrı ayrı yönetebilmesi anlamına gelir.

## 📁 Konfigürasyon Dizini

Tüm kullanıcı konfigürasyonları şu dizinde saklanır:
```
Windows: C:\Users\[username]\.mcp-colab\
Linux/Mac: ~/.mcp-colab/
```

## 📂 Dizin Yapısı

```
~/.mcp-colab/
├── server_config.json      # Server konfigürasyonu
├── credentials.json        # Google API credentials
├── token.json             # OAuth2 tokens (otomatik oluşturulur)
├── credentials.json.template # Credentials şablonu
└── logs/
    └── colab_mcp.log      # Log dosyası
```

## 🚀 Hızlı Başlangıç

### 1. Konfigürasyon Dizinini Başlat
```bash
python -m mcp_colab_server.config_manager --init
```

### 2. Credentials Dosyasını Yerleştir
1. Google Cloud Console'dan `credentials.json` dosyasını indirin
2. `~/.mcp-colab/credentials.json` olarak kaydedin

### 3. Kimlik Doğrulama Yap
```bash
python -m mcp_colab_server.setup
```

### 4. Durumu Kontrol Et
```bash
python -m mcp_colab_server.config_manager --status
```

## 🛠️ Konfigürasyon Yönetimi

### Durum Kontrolü
```bash
python -m mcp_colab_server.config_manager --status
```

### Konfigürasyonu Doğrula
```bash
python -m mcp_colab_server.config_manager --validate
```

### Konfigürasyonu Sıfırla
```bash
python -m mcp_colab_server.config_manager --reset
```

### Zorla Yeniden Başlat
```bash
python -m mcp_colab_server.config_manager --init --force
```

## 📋 Konfigürasyon Dosyaları

### server_config.json
Ana server konfigürasyonu. Otomatik olarak kullanıcı dizinindeki dosya yollarını kullanacak şekilde ayarlanır.

### credentials.json
Google Cloud Console'dan indirilen OAuth2 credentials dosyası.

### token.json
İlk kimlik doğrulama sonrası otomatik olarak oluşturulur. Refresh token'ları içerir.

## 🔄 Eski Sistemden Geçiş

Eğer daha önce proje dizininde `config/` klasörü kullanıyorsanız:

1. Eski credentials'ları kopyalayın:
```bash
python -m mcp_colab_server.config_manager --copy-credentials ./config
```

2. Eski token'ı silin (yenisi otomatik oluşturulacak):
```bash
rm config/token.json
```

3. Yeni sistemi test edin:
```bash
python -m mcp_colab_server.config_manager --validate
```

## 🔒 Güvenlik

- `credentials.json` ve `token.json` dosyaları hassas bilgiler içerir
- Bu dosyalar asla version control'e commit edilmemelidir
- Her kullanıcının kendi credentials'ları olmalıdır
- Token'lar otomatik olarak yenilenir

## 🐛 Sorun Giderme

### Credentials Bulunamıyor
```bash
# Durum kontrolü yap
python -m mcp_colab_server.config_manager --status

# Template oluştur
python -m mcp_colab_server.config_manager --init

# Gerçek credentials dosyasını yerleştir
# ~/.mcp-colab/credentials.json
```

### Token Geçersiz
```bash
# Token'ı sil ve yeniden kimlik doğrula
rm ~/.mcp-colab/token.json
python -m mcp_colab_server.setup
```

### Konfigürasyon Bozuk
```bash
# Tümünü sıfırla ve yeniden başlat
python -m mcp_colab_server.config_manager --reset
python -m mcp_colab_server.config_manager --init
```

## 💡 İpuçları

1. **Çoklu Kullanıcı**: Her kullanıcı kendi `~/.mcp-colab/` dizinine sahip olur
2. **Taşınabilirlik**: Konfigürasyon kullanıcı home dizininde olduğu için sistem genelinde erişilebilir
3. **Güvenlik**: Dosya izinleri otomatik olarak kullanıcı bazlı ayarlanır
4. **Backup**: Önemli dosyaları düzenli olarak yedekleyin

## 🌐 Chrome Profil Yönetimi

MCP Colab Server artık Chrome profillerini de `.mcp-colab` dizininde yönetir:

### Chrome Profil Komutları
```bash
# Profil özeti
python -m mcp_colab_server.config_manager --profile-summary

# Eski profilleri temizle
python -m mcp_colab_server.config_manager --clean-profiles

# Tüm profilleri optimize et
python -m mcp_colab_server.config_manager --optimize-profiles
```

### Chrome Profil Yapısı
```
~/.mcp-colab/chrome_profiles/
├── default/                 # Varsayılan profil
├── backup_20241226_143022/  # Otomatik backup
└── profiles_metadata.json  # Profil metadata
```

### Profil Özellikleri
- **Kalıcı Oturum**: Google login bilgileri saklanır
- **Otomatik Backup**: Önemli değişiklikler öncesi backup
- **Optimizasyon**: Cache ve geçici dosyalar temizlenir
- **Metadata Takibi**: Kullanım istatistikleri

## 🔧 Gelişmiş Kullanım

### Özel Konfigürasyon Yolu
```python
from mcp_colab_server import AuthManager

# Özel path ile
auth_manager = AuthManager(
    credentials_file="/custom/path/credentials.json",
    token_file="/custom/path/token.json"
)
```

### Programatik Konfigürasyon
```python
from mcp_colab_server import ConfigManager
from mcp_colab_server import ChromeProfileManager

# Config yönetimi
config_manager = ConfigManager()
config_manager.init_user_config()
config_manager.validate_config()

# Chrome profil yönetimi
profile_manager = ChromeProfileManager()
profiles = profile_manager.list_profiles()
profile_manager.optimize_profile("default")
```

### Selenium Konfigürasyonu
```json
{
  "selenium": {
    "browser": "chrome",
    "headless": false,
    "profile": {
      "use_persistent_profile": true,
      "profile_name": "default"
    },
    "anti_detection": {
      "disable_automation_indicators": true,
      "custom_user_agent": true,
      "disable_images": false
    }
  }
}
```