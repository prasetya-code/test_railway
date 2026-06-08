# NOTE LINTING & TESTING

- linting with ruff -> `ruff check . --fix && ruff format . && ruff check .`
- testing with pytest -> 
   - buat file pytest.ini
   - `pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=xml`

# Env in railways

| Kebutuhan                                | Gunakan           |
| ---------------------------------------- | ----------------- |
| Token deploy Railway dari GitHub Actions | GitHub Secrets    |
| API key aplikasi production              | Railway Variables |
| DATABASE_URL production                  | Railway Variables |
| Flask/Django secret key                  | Railway Variables |
| Token automation CI/CD                   | GitHub Secrets    |



# Flow yang benar

GitHub Actions
    ↓
menggunakan GitHub Secrets
    ↓
deploy ke Railway
    ↓
Aplikasi berjalan di Railway
    ↓
menggunakan Railway Variables



# Contoh yang umum dipakai

## GitHub Secrets 
Settings ➡️ tab secret and variables ➡️ actions

| Name            | Value         |
| --------------- | ------------- |
| RAILWAY_TOKEN   | token railway |
| RAILWAY_SERVICE | nama service  |


## Railway Variables

Project ➡️ Variables

| Key          | Value          |
| ------------ | -------------- |
| APP_ENV      | production     |
| DATABASE_URL | postgres://... |
| SECRET_KEY   | random-secret  |
| DEBUG        | false          |
