# Flask Testing — Catatan Lengkap

## Struktur Folder

```text
tests/
├── unit/           # fungsi terisolasi
├── integration/    # antar komponen + DB
├── functional/     # alur pengguna E2E
├── data/           # JSON/CSV dummy
├── conftest.py     # fixture global
└── pytest.ini      # konfigurasi pytest
```

---

## conftest.py

```python
import pytest, json
from unittest.mock import patch
from app import create_app, db
from app.models import User, Product
from tests.factories import UserFactory, ProductFactory

@pytest.fixture(scope="session")
def app():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
                      "WTF_CSRF_ENABLED": False, "SECRET_KEY": "test-secret"})
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope="function")
def client(app): return app.test_client()

@pytest.fixture(scope="function")
def db_session(app):
    conn = db.engine.connect(); tx = conn.begin(); db.session.bind = conn
    yield db.session
    db.session.remove(); tx.rollback(); conn.close()

@pytest.fixture
def seed_users(db_session):
    users = json.load(open("tests/data/users.json"))
    for u in users:
        user = User(**{k: v for k, v in u.items() if k != "password"})
        user.set_password(u["password"]); db_session.add(user)
    db_session.commit()

@pytest.fixture
def seed_products(db_session):
    [db_session.add(Product(**p)) for p in json.load(open("tests/data/products.json"))]
    db_session.commit()

@pytest.fixture
def auth_client(client, seed_users):
    res = client.post("/auth/login", json={"email": "alice@mail.com", "password": "password123"})
    client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {res.get_json()['token']}"
    return client

@pytest.fixture
def mock_email():
    with patch("app.services.email.send_email") as mock: yield mock

@pytest.fixture
def mock_storage():
    with patch("app.services.storage.upload_file") as mock:
        mock.return_value = "https://cdn.example.com/file.jpg"; yield mock
```

---

## Unit Test

### `test_models.py`

```python
import pytest
from app.models import User, Product

class TestUserModel:
    def test_create(self):
        u = User(username="alice", email="alice@mail.com")
        assert u.username == "alice" and u.email == "alice@mail.com"

    def test_password_hash(self):
        u = User(username="bob"); u.set_password("secret")
        assert u.password_hash != "secret"
        assert u.check_password("secret") is True
        assert u.check_password("wrong") is False

    def test_invalid_email(self):
        with pytest.raises(ValueError): User(email="bukan-email")

    def test_repr(self):
        assert "alice" in repr(User(username="alice"))

class TestProductModel:
    def test_negative_price(self):
        with pytest.raises(ValueError, match="harga tidak valid"):
            Product(name="X", price=-10)

    def test_stock_default(self):
        assert Product(name="Buku", price=25000).stock == 0

    def test_is_available(self):
        p = Product(name="X", price=1000, stock=5)
        assert p.is_available() is True
        p.stock = 0
        assert p.is_available() is False
```

### `test_helpers.py`

```python
import pytest
from app.helpers import format_rupiah, slugify, truncate_text

@pytest.mark.parametrize("val, expected", [
    (50000, "Rp 50.000"), (0, "Rp 0"), (1500000, "Rp 1.500.000"),
])
def test_format_rupiah(val, expected): assert format_rupiah(val) == expected

@pytest.mark.parametrize("val, expected", [
    ("Hello World", "hello-world"), ("  Spasi  ", "spasi"), ("A & B", "a-b"),
])
def test_slugify(val, expected): assert slugify(val) == expected

def test_truncate():
    assert len(truncate_text("a" * 50, 10)) <= 13
    assert truncate_text("Pendek", 20) == "Pendek"
```

### `test_validators.py`

```python
import pytest
from app.validators import validate_email, validate_phone, validate_form

@pytest.mark.parametrize("email, valid", [
    ("user@mail.com", True), ("noatsign", False), ("", False),
])
def test_email(email, valid): assert validate_email(email) is valid

def test_email_none(): 
    with pytest.raises(TypeError): validate_email(None)

@pytest.mark.parametrize("phone, valid", [
    ("08123456789", True), ("+6281234567890", True), ("0812", False),
])
def test_phone(phone, valid): assert validate_phone(phone) is valid

def test_form_valid():
    assert validate_form({"name": "Ali", "email": "a@b.com"}, required=["name","email"]) == []

def test_form_missing_field():
    assert "email" in validate_form({"name": "Ali"}, required=["name","email"])
```

---

## Mocking & Patching

```python
from unittest.mock import patch, MagicMock, call
import pytest

class TestMocking:
    def test_mock_external_api(self, client):
        with patch("app.services.payment.charge") as mock_charge:
            mock_charge.return_value = {"status": "success", "id": "pay_123"}
            res = client.post("/api/checkout", json={"amount": 50000})
            assert res.status_code == 200
            mock_charge.assert_called_once_with(amount=50000)

    def test_mock_email_service(self, client, mock_email):
        client.post("/auth/register", json={"email": "x@mail.com", "password": "P123!"})
        assert mock_email.called
        assert mock_email.call_args[1]["to"] == "x@mail.com"

    def test_mock_file_upload(self, auth_client, mock_storage):
        data = {"file": (b"img content", "photo.jpg", "image/jpeg")}
        res = auth_client.post("/api/upload", data=data, content_type="multipart/form-data")
        assert res.status_code == 200
        assert res.get_json()["url"] == "https://cdn.example.com/file.jpg"

    def test_mock_chained_calls(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = mock_db.query(User).filter(User.id == 1).first()
        assert result is None
```

---

## Factory Boy & Faker

### `tests/factories.py`

```python
import factory
from faker import Faker
from app import db
from app.models import User, Product

fake = Faker("id_ID")  # locale Indonesia

class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User; sqlalchemy_session = db.session

    username = factory.LazyFunction(fake.user_name)
    email    = factory.LazyFunction(fake.email)
    role     = "user"

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        obj.set_password(extracted or "defaultpass")

class ProductFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Product; sqlalchemy_session = db.session

    name     = factory.LazyFunction(fake.word)
    price    = factory.LazyFunction(lambda: fake.random_int(1000, 500000))
    stock    = factory.LazyFunction(lambda: fake.random_int(0, 100))
    category = factory.LazyFunction(lambda: fake.random_element(["elektronik","buku","pakaian"]))
```

### Penggunaan Factory di Test

```python
def test_dengan_factory(db_session):
    user = UserFactory(username="spesifik", password="pass123")
    produk_list = ProductFactory.create_batch(5, category="buku")

    assert user.username == "spesifik"
    assert len(produk_list) == 5
    assert all(p.category == "buku" for p in produk_list)
```

---

## Freeze Time (Mock Datetime)

```python
from freezegun import freeze_time
from datetime import datetime

@freeze_time("2025-01-01 12:00:00")
def test_token_expiry(client, seed_users):
    res = client.post("/auth/login", json={"email": "alice@mail.com", "password": "password123"})
    token_data = res.get_json()
    assert token_data["expires_at"] == "2025-01-01T13:00:00"  # expire 1 jam

@freeze_time("2025-06-01")
def test_promo_aktif(client):
    res = client.get("/api/promo/ramadan")
    assert res.get_json()["aktif"] is False  # promo sudah lewat

class TestFreezeContext:
    def test_order_timestamp(self, auth_client):
        with freeze_time("2025-03-15 09:30:00"):
            res = auth_client.post("/api/orders", json={"product_id": 1})
            assert res.get_json()["created_at"] == "2025-03-15T09:30:00"
```

---

## Integration Test

### `test_routes.py`

```python
class TestUserRoutes:
    def test_get_all(self, client, seed_users):
        res = client.get("/api/users")
        assert res.status_code == 200 and isinstance(res.get_json(), list)

    def test_get_by_id(self, client, seed_users):
        res = client.get("/api/users/1")
        assert res.status_code == 200 and "username" in res.get_json()

    def test_not_found(self, client):
        assert client.get("/api/users/9999").status_code == 404

    def test_create(self, client):
        res = client.post("/api/users", json={"username":"dewi","email":"dewi@mail.com","password":"P123!"})
        assert res.status_code == 201 and res.get_json()["username"] == "dewi"

    def test_duplicate_email(self, client, seed_users):
        assert client.post("/api/users", json={"username":"x","email":"alice@mail.com"}).status_code == 409

    def test_update(self, client, seed_users):
        res = client.put("/api/users/1", json={"email": "baru@mail.com"})
        assert res.status_code == 200 and res.get_json()["email"] == "baru@mail.com"

    def test_delete(self, client, seed_users):
        assert client.delete("/api/users/1").status_code == 200
        assert client.get("/api/users/1").status_code == 404
```

### `test_auth.py`

```python
class TestAuth:
    def test_register(self, client):
        res = client.post("/auth/register", json={"username":"u","email":"u@mail.com","password":"P123!"})
        assert res.status_code == 201

    def test_login_ok(self, client, seed_users):
        res = client.post("/auth/login", json={"email":"alice@mail.com","password":"password123"})
        assert res.status_code == 200 and "token" in res.get_json()

    def test_login_wrong_pass(self, client, seed_users):
        assert client.post("/auth/login", json={"email":"alice@mail.com","password":"salah"}).status_code == 401

    def test_protected_no_token(self, client):
        assert client.get("/api/protected").status_code == 401

    def test_protected_with_token(self, auth_client):
        assert auth_client.get("/api/protected").status_code == 200
```

---

## Error Handling & Exception Test

```python
class TestErrorHandlers:
    def test_404_handler(self, client):
        res = client.get("/route/yang/tidak/ada")
        assert res.status_code == 404
        assert res.get_json()["error"] == "not_found"

    def test_500_handler(self, client):
        with patch("app.routes.user.get_users", side_effect=Exception("DB error")):
            res = client.get("/api/users")
            assert res.status_code == 500
            assert "error" in res.get_json()

    def test_403_forbidden(self, auth_client):
        # user biasa tidak bisa akses endpoint admin
        res = auth_client.get("/api/admin/users")
        assert res.status_code == 403

    def test_422_validation_error(self, client):
        res = client.post("/api/users", json={"username": ""})
        assert res.status_code == 422
        assert "errors" in res.get_json()

    def test_custom_exception(self, client):
        with patch("app.routes.product.get_product", side_effect=OutOfStockError("stok habis")):
            res = client.post("/api/cart", json={"product_id": 1, "qty": 999})
            assert res.status_code == 400
            assert res.get_json()["code"] == "OUT_OF_STOCK"
```

---

## Test File Upload

```python
import io

class TestFileUpload:
    def test_upload_gambar_valid(self, auth_client, mock_storage):
        data = {"file": (io.BytesIO(b"fake image data"), "foto.jpg", "image/jpeg")}
        res = auth_client.post("/api/upload", data=data, content_type="multipart/form-data")
        assert res.status_code == 200
        assert "url" in res.get_json()

    def test_upload_format_tidak_valid(self, auth_client):
        data = {"file": (io.BytesIO(b"data"), "file.exe", "application/octet-stream")}
        res = auth_client.post("/api/upload", data=data, content_type="multipart/form-data")
        assert res.status_code == 400
        assert res.get_json()["error"] == "format_tidak_didukung"

    def test_upload_tanpa_file(self, auth_client):
        res = auth_client.post("/api/upload", data={}, content_type="multipart/form-data")
        assert res.status_code == 400

    def test_upload_file_terlalu_besar(self, auth_client):
        data = {"file": (io.BytesIO(b"x" * 10_000_001), "besar.jpg", "image/jpeg")}
        res = auth_client.post("/api/upload", data=data, content_type="multipart/form-data")
        assert res.status_code == 413
```

---

## Test Blueprint

```python
# Jika app pakai Blueprint, test per blueprint
class TestProductBlueprint:
    def test_blueprint_terdaftar(self, app):
        blueprints = list(app.blueprints.keys())
        assert "product" in blueprints
        assert "auth" in blueprints

    def test_url_prefix_product(self, client):
        # Blueprint product dengan prefix /products
        res = client.get("/products/")
        assert res.status_code in [200, 401]  # ada atau butuh auth

    def test_url_prefix_admin(self, client):
        res = client.get("/admin/dashboard")
        assert res.status_code in [200, 401, 403]
```

---

## Pytest Markers

```python
import pytest

@pytest.mark.skip(reason="fitur belum diimplementasi")
def test_fitur_baru(): ...

@pytest.mark.xfail(reason="bug diketahui, sedang diperbaiki")
def test_edge_case_diketahui_gagal():
    assert 1 == 2  # memang gagal, dianggap expected

@pytest.mark.slow
def test_proses_batch_besar(client, seed_products):
    # test yang butuh waktu lama
    res = client.post("/api/export/csv")
    assert res.status_code == 200

@pytest.mark.smoke
def test_app_berjalan(client):
    assert client.get("/health").status_code == 200

@pytest.mark.auth
def test_endpoint_butuh_auth(auth_client):
    assert auth_client.get("/api/me").status_code == 200

# Jalankan berdasarkan marker:
# pytest -m smoke          → hanya smoke test
# pytest -m "not slow"     → skip test lambat
# pytest -m "auth and not slow"
```

---

## Functional Test

### `test_user_flow.py`

```python
class TestAlurPengguna:
    def test_register_login_logout(self, client):
        # Register
        assert client.post("/auth/register", json={
            "username": "testuser", "email": "t@mail.com", "password": "T123!"
        }).status_code == 201

        # Login → token
        token = client.post("/auth/login", json={
            "email": "t@mail.com", "password": "T123!"
        }).get_json()["token"]

        h = {"Authorization": f"Bearer {token}"}

        # Akses & verifikasi profil
        res = client.get("/api/profile", headers=h)
        assert res.status_code == 200 and res.get_json()["username"] == "testuser"

        # Logout → token invalid
        client.post("/auth/logout", headers=h)
        assert client.get("/api/profile", headers=h).status_code == 401

    def test_alur_belanja(self, auth_client, seed_products):
        produk_id = auth_client.get("/api/products").get_json()[0]["id"]
        assert auth_client.post("/api/cart", json={"product_id": produk_id, "qty": 2}).status_code == 201
        res = auth_client.post("/api/checkout")
        assert res.status_code == 200 and "order_id" in res.get_json()
```

---

## Test Data

### `tests/data/users.json`

```json
[
  {"username": "alice", "email": "alice@mail.com", "password": "password123", "role": "admin"},
  {"username": "bob",   "email": "bob@mail.com",   "password": "bobpass",     "role": "user"}
]
```

### `tests/data/products.json`

```json
[
  {"name": "Laptop Dev",  "price": 12500000, "stock": 10, "category": "elektronik"},
  {"name": "Buku Python", "price": 150000,   "stock": 50, "category": "buku"}
]
```

---

## pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test
python_functions = test_

addopts =
    --strict-markers -v --tb=short
    --cov=app --cov-report=term-missing --cov-report=html:htmlcov

markers =
    slow:  test yang membutuhkan waktu lama
    smoke: sanity check dasar aplikasi
    auth:  test yang memerlukan autentikasi
```

### Perintah Umum

```bash
pytest                                        # semua test
pytest tests/unit/                            # hanya unit
pytest tests/unit/test_helpers.py::test_slugify  # satu fungsi
pytest -m smoke                               # by marker
pytest -m "not slow"                          # skip lambat
pytest -v -x                                  # verbose, stop pertama gagal
pytest --cov=app --cov-report=html            # dengan coverage
```

### `requirements-test.txt`

```
pytest>=7.0
pytest-flask
pytest-cov
pytest-mock
factory-boy
faker
freezegun
```

---

## Membaca Coverage Report

```
Name                      Stmts   Miss  Cover   Missing
-------------------------------------------------------
app/models.py                40      4    90%   45, 67-69
app/helpers.py               20      0   100%
app/routes/auth.py           35      7    80%   88-94
```

- **Stmts** → total baris kode yang bisa dieksekusi
- **Miss** → baris yang tidak tereksekusi saat test
- **Cover** → persentase coverage
- **Missing** → nomor baris yang belum tercover → tambahkan test untuk baris tersebut
- Target minimal: **80% overall**, fungsi kritis (auth, payment) **≥ 95%**

---

## Anti-Pattern — Jangan Lakukan Ini

```python
# ❌ Test saling bergantung (urutan mempengaruhi hasil)
def test_a(): db.session.add(User(username="x")); db.session.commit()
def test_b(): assert User.query.count() == 1  # gagal jika test_a belum jalan

# ✅ Tiap test mandiri, gunakan fixture
def test_b(seed_users): assert User.query.count() == len(seed_users)

# ❌ Hardcode ID (bisa berbeda tiap run)
def test_get_user(client): client.get("/api/users/1")

# ✅ Ambil ID dari response sebelumnya
def test_get_user(client, seed_users):
    user_id = client.get("/api/users").get_json()[0]["id"]
    client.get(f"/api/users/{user_id}")

# ❌ Assert terlalu umum (selalu lulus meski ada bug)
def test_response(): assert res.status_code == 200

# ✅ Assert spesifik
def test_response():
    assert res.status_code == 200
    assert res.get_json()["username"] == "alice"
    assert "token" in res.get_json()

# ❌ Tidak membersihkan mock
def test_pakai_mock():
    patch("app.service.send").start()  # mock tidak berhenti otomatis

# ✅ Gunakan context manager atau fixture
def test_pakai_mock():
    with patch("app.service.send") as m: m.return_value = True; ...
```