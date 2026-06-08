# Pull Request: Menambahkan Pengujian Program Hello World Python

## Ringkasan

Pull Request ini menambahkan pengujian dasar untuk program Python sederhana yang menampilkan teks **"Hello World"** ke terminal. Pengujian dilakukan untuk memastikan lingkungan Python telah terinstal dengan benar dan program dapat dijalankan tanpa error.

## Perubahan yang Dilakukan

* Menambahkan program Python sederhana:

  ```python
  print("Hello World")
  ```
* Melakukan verifikasi bahwa program dapat dieksekusi menggunakan Python 3.x.
* Memastikan output yang dihasilkan sesuai dengan yang diharapkan.

## Langkah Pengujian

1. Simpan kode ke dalam file `main.py`.

2. Jalankan perintah:

   ```bash
   python main.py
   ```

3. Periksa output pada terminal.

## Hasil Pengujian

| No | Skenario Pengujian               | Status   |
| -- | -------------------------------- | -------- |
| 1  | Program berjalan tanpa error     | ✅ Passed |
| 2  | Output menampilkan "Hello World" | ✅ Passed |

### Output Aktual

```text
Hello World
```

## Environment

* Python Version: 3.x
* Operating System: Windows / Linux / macOS

## Impact

Perubahan ini tidak memengaruhi fitur lain dalam aplikasi dan hanya digunakan sebagai validasi dasar bahwa lingkungan Python berfungsi dengan baik.

## Related Issue

Closes #<issue-number>
