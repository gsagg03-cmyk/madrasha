# মাদরাসা উম্মুলকুরা - Domain Information

## 🌐 Domain Details

**Primary Domain:** `madrasaummulqura.com`

**Alternative Domains:**
- `www.madrasaummulqura.com`

## 📧 Contact Email
`admin@madrasaummulqura.com`

## 🔐 SSL Certificate
Configured with Let's Encrypt for HTTPS

## 🏢 Madrasha Name (Official)
**Bengali:** মাদরাসা উম্মুলকুরা  
**English:** Madrasa Ummul Qura  
**Arabic:** مدرسة أم القرى

## 📍 Location
Mohadevpur Girls School Mor  
Phone: 01712227754  
Email: mshfiqul490@gmail.com

## 🚀 Live URLs
- Production: `https://madrasaummulqura.com`
- With www: `https://www.madrasaummulqura.com`

## 🔧 Server Configuration
- VPS Provider: Contabo
- Server Location: `/var/www/madrasha`
- Nginx Configuration: `/etc/nginx/sites-available/madrasha`
- SSL Certificates: `/etc/letsencrypt/live/madrasaummulqura.com/`

## 📝 DNS Records Required
```
Type    Name    Value                   TTL
A       @       [Your VPS IP]           3600
A       www     [Your VPS IP]           3600
CNAME   www     madrasaummulqura.com    3600
```

## 🔄 SSL Renewal
SSL certificates auto-renew via certbot cron job.  
Manual renewal: `sudo certbot renew`

---

**Last Updated:** November 24, 2025
