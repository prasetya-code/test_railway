# minimal policy web headers yang layak dipasang di production

| Level       | Persentase | Keterangan                                              |
| ----------- | ---------- | ------------------------------------------------------- |
| Basic       | 60-70%     | Sudah aman untuk aplikasi internal                      |
| Recommended | 80-90%     | Cocok untuk mayoritas website dan API production        |
| Hardened    | 95-100%    | Cocok untuk fintech, healthcare, government, enterprise |


# headers

- header param tidak pernah terpanggil, dan harus di panggil lewat regis_utils
- skema yang di inginkan saya mau semua param header di satukan ke dalam satu file dulu yakni headers.py lalu pada regis_utils tingal memanggil init_headers yang menjalankan semua header param yang sudah di set

# Note

- ** itu untuk unpack (membongkar) isi dictionary dan menggabungkannya ke dalam dictionary baru.