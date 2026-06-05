# PR: Setup Python App on Railway

## Summary
PR ini menambahkan konfigurasi dan setup yang diperlukan untuk melakukan deployment aplikasi Python ke Railway, termasuk konfigurasi production, dependency management, dan proses deployment otomatis dari GitHub.

---

## Changes

### 1. Deployment Setup
- Menambahkan konfigurasi untuk deployment di Railway
- Menghubungkan repository dengan GitHub untuk auto deploy

### 2. Dependency Management
- Menambahkan `requirements.txt` untuk dependency Python

### 3. Production Configuration
- Menambahkan `Procfile` untuk menjalankan aplikasi di production

### 4. Menambahkan Setup environment variables
- Menambahkan parameter environment pada aplikasi

### 5. Testing deployment
- Melakukan testing deployment local untuk melakukan pengetesan

### 6. Monitoring deployment
- Monitoring debug aplikasi

```bash
web: gunicorn app:app