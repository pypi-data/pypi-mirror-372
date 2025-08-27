# Chrome Profil Yönetimi Rehberi

Bu rehber, Google Colab MCP sunucusunda kalıcı Chrome profili özelliğinin nasıl kullanılacağını açıklar.

## Özellik Açıklaması

Kalıcı Chrome profili özelliği, Google oturum açma bilgilerinizi tarayıcıda saklar. Bu sayede:
- Her seferinde Google'a yeniden giriş yapmanıza gerek kalmaz
- Oturum bilgileri güvenli bir şekilde saklanır
- Colab kullanımı daha hızlı ve sorunsuz hale gelir

## Yapılandırma

### Otomatik Yapılandırma (Varsayılan)
Sistem varsayılan olarak kalıcı profil kullanacak şekilde yapılandırılmıştır:
- Profil dizini: `~/.colab_selenium_profile`
- Otomatik oluşturma: Etkin
- Kalıcı profil: Etkin

### Manuel Yapılandırma
`config/server_config.json` dosyasında profil ayarlarını değiştirebilirsiniz:

```json
{
  "selenium": {
    "profile": {
      "use_persistent_profile": true,
      "profile_directory": null,
      "auto_create_profile": true
    }
  }
}
```

#### Yapılandırma Seçenekleri:
- `use_persistent_profile`: Kalıcı profil kullanımını etkinleştirir/devre dışı bırakır
- `profile_directory`: Özel profil dizini (null ise varsayılan kullanılır)
- `auto_create_profile`: Profil dizinini otomatik oluşturur

## MCP Araçları

### 1. Profil Bilgisi Alma
```bash
# Profil durumunu kontrol et
get_chrome_profile_info
```

Bu araç şu bilgileri verir:
- Kalıcı profil etkin mi?
- Profil dizini nerede?
- Profil mevcut mu?
- Profil boyutu (MB)

### 2. Profil Temizleme
```bash
# Profil verilerini temizle
clear_chrome_profile
```

Bu araç:
- Tüm oturum verilerini siler
- Çerezleri ve önbelleği temizler
- Yeniden giriş yapmanızı gerektirir

## İlk Kurulum Süreci

1. **MCP Sunucusunu Başlatın**
   ```bash
   python -m mcp_colab_server.server
   ```

2. **Google Kimlik Doğrulaması Yapın**
   ```bash
   authenticate_google
   ```

3. **İlk Colab Oturumu**
   - Tarayıcı açılacak
   - Google hesabınızla giriş yapın
   - Gerekli izinleri verin
   - Oturum bilgileri otomatik kaydedilecek

4. **Sonraki Kullanımlar**
   - Artık otomatik giriş yapılacak
   - Manuel kimlik doğrulama gerekmeyecek

## Sorun Giderme

### Oturum Açma Sorunları
Eğer sürekli giriş yapmanız isteniyorsa:

1. Profil durumunu kontrol edin:
   ```bash
   get_chrome_profile_info
   ```

2. Profili temizleyip yeniden deneyin:
   ```bash
   clear_chrome_profile
   authenticate_google
   ```

### Profil Boyutu Sorunları
Profil çok büyükse (>100MB):

1. Profili temizleyin:
   ```bash
   clear_chrome_profile
   ```

2. Yeniden giriş yapın:
   ```bash
   authenticate_google
   ```

### Yapılandırma Sorunları
Profil çalışmıyorsa:

1. `config/server_config.json` dosyasını kontrol edin
2. `use_persistent_profile: true` olduğundan emin olun
3. Profil dizininin yazılabilir olduğunu kontrol edin

## Güvenlik Notları

- Profil verileri yerel olarak saklanır
- Paylaşılan bilgisayarlarda dikkatli olun
- Düzenli olarak profil temizliği yapın
- Şüpheli aktivite durumunda profili temizleyin

## Avantajlar

✅ **Hızlı Erişim**: Tekrar giriş yapmaya gerek yok
✅ **Otomatik Oturum**: Seamless Colab deneyimi
✅ **Güvenli Saklama**: Yerel profil koruması
✅ **Kolay Yönetim**: MCP araçlarıyla kontrol

## Dezavantajlar

⚠️ **Disk Kullanımı**: Profil verileri yer kaplar
⚠️ **Güvenlik Riski**: Paylaşılan sistemlerde dikkat
⚠️ **Bağımlılık**: Chrome'a özgü çözüm

## Sık Sorulan Sorular

**S: Profil nerede saklanıyor?**
C: Varsayılan olarak `~/.colab_selenium_profile` dizininde.

**S: Profili nasıl yedeklerim?**
C: Profil dizinini kopyalayın. Ancak güvenlik nedeniyle önerilmez.

**S: Birden fazla Google hesabı kullanabilir miyim?**
C: Hayır, profil tek hesap için tasarlanmıştır.

**S: Profil bozulursa ne yapmalıyım?**
C: `clear_chrome_profile` aracını kullanarak temizleyin ve yeniden giriş yapın.