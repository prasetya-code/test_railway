# Alur Lengkap Git: Issue → Branch → Commit → Push → PR → Merge

## 1. Buat Issue dari File Markdown

Untuk issue dengan file markdown, buat file markdown khusus issue lalu lakukan create issue dengan file tersebut:

```bash
# Format lengkap
gh issue create --title "judul issue" --body-file path_issue.md --label "nama label"

# Format singkat
gh issue create -t "judul issue" -F path_issue.md -l "nama label"

# Jika ingin edit title
gh issue edit no_ID -t "new title"  | 

# Jika ingin add or remove label
gh issue --add-label no_ID "new label" | gh issue --remove-label no_ID "nama label"

# Menampilkan semua issue yang terbuka
gh issue ls

# Filter issue berdasarkan label
gh issue ls -l "nama label"

# Melihat detail issue berdasarkan ID
gh issue view no_ID
```

Catat nomor issue yang dibuat (misalnya `#42`) untuk direferensikan di branch dan commit.

> **Keuntungan pendekatan ini:**
> - Konten issue tersimpan di repository sebagai dokumentasi
> - Bisa di-review dan di-edit sebelum dibuat
> - Konsisten karena tidak bergantung pada editor di browser GitHub

---

## 2. Buat dan Pindah ke Branch Baru

```bash
# Buat branch baru sekaligus pindah ke branch tersebut
# Sertakan nomor issue agar mudah dilacak
git checkout -b 'nama branch'

# Atau dengan perintah terpisah
git branch 'nama branch'
git checkout 'nama branch'

# Verifikasi branch aktif
git branch
```

---

## 3. Kerjakan Perubahan: Add, Commit, & Push

```bash
# Lihat status perubahan
git status

# Tambahkan semua file yang berubah
git add .

# Atau tambahkan file tertentu saja
git add src/login.ts

# Commit dengan pesan yang deskriptif, sertakan nomor issue
git commit -m "pesan deskriptif, no_ID issue"

# Push branch baru ke remote (origin)
git push -u origin nama branch
```

---

## 5. Buat Pull Request dari File Markdown

Untuk PR dengan file markdown, buat file markdown khusus PR lalu lakukan create PR dengan file tersebut:

```bash
# Format lengkap
gh pr create --title "judul PR" --body-file path_pr.md --base "tujuan branch" --head "sumber branch"

# Format singkat
gh issue create -t "judul PR" -F path_issue.md -B "tujuan branch" -H "sumber branch"
```

> **Keuntungan pendekatan ini:**
> - Konten PR tersimpan di repository sebagai dokumentasi
> - Bisa di-review dan di-edit sebelum dibuat
> - Konsisten karena tidak bergantung pada editor di browser GitHub

---

## 6. Review & Merge PR ke Main

```bash
# Lihat daftar PR yang terbuka
gh pr list

# Lihat detail PR (opsional)
gh pr view

# Merge PR ke main setelah di-review
gh pr merge --merge   # merge commit biasa
gh pr merge --squash  # gabungkan semua commit jadi satu
gh pr merge --rebase  # rebase ke main
```

---

## 7. Sinkronisasi Main Lokal & Hapus Branch

```bash
# Kembali ke branch main
git checkout main

# Tarik perubahan terbaru dari remote
git pull origin main

# Hapus branch lokal yang sudah di-merge
git branch -d feat/42-login-oauth

# Hapus branch remote (opsional)
git push origin --delete feat/42-login-oauth
```

---

> **Ringkasan alur:**
> `issue` → `branch` → `add` → `commit` → `push` → `pr` → `review` → `merge` → `cleanup`