# Connecto

A Django-based delivery and parcel logistics platform that connects customers who need to send parcels with vendors (drivers/agents) who are traveling on trips. Customers create delivery requests; vendors create trips. The system matches parcels to trips, manages shipments, KYC (DigiLocker), payments (Razorpay), and live tracking.

---

## Features

- **Customer**
  - Create delivery requests (parcels) with pickup/destination, dimensions, budget, and optional home pickup/drop addresses
  - Search trips by source/destination city
  - View and manage shipments, ratings, support tickets
  - KYC via DigiLocker (Aadhaar, PAN, Driving License) with database-backed document storage
  - OTP-based order verification; SMS on order creation and delivery
  - Razorpay payments; Stream chat with vendors

- **Vendor**
  - Create trips (source, destination, transport type, capacity, schedule)
  - Search parcels, accept/reject customer requests, manage shipments
  - Update shipment status; mark orders delivered (triggers SMS)
  - Live location updates and customer-facing tracking
  - Trip deletion blocked when parcels are assigned

- **Masters**
  - Cities (auto-created when trips or parcels are saved with new source/destination city names)

- **Users & Auth**
  - Custom user model (mobile as username); Firebase (phone/Google) and JWT (REST API)
  - User KYC (Aadhaar required for approval); profile and credits
  - Admin login (`/users/login-admin/`)

- **API**
  - REST API with JWT; Swagger at `/swagger/`, ReDoc at `/redoc/`
  - CORS allowed for localhost (3000, 8081, 5173)

---

## Tech Stack

- **Backend:** Django 5.x, Django REST Framework, Simple JWT, django-filter
- **Auth:** Firebase Admin (phone/Google), JWT
- **Payments:** Razorpay
- **KYC:** Surepass/DigiLocker (optional; can run DB-only)
- **Database:** SQLite (default); configurable for PostgreSQL etc.
- **Env:** python-dotenv (`.env` in `connecto/`)

---

## Project Structure

```
connecto/
├── connecto/           # Project settings, urls, wsgi
│   ├── settings.py
│   ├── urls.py
│   └── .env            # RAZORPAY_*, SMS_*, etc. (create from example)
├── customer/           # Delivery requests, parcels, shipments, KYC, payments, chat
├── vendor/             # Trips, parcel requests, shipments, location
├── users/              # User model, auth, KYC, profile, admin login
├── masters/            # Cities and other master data
├── templates/          # Django templates (e.g. account/login)
├── static/
├── media/
├── db.sqlite3
└── README.md
```

---

## Setup

### 1. Clone and virtual environment

```bash
git clone <repo-url>
cd connecto
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install django djangorestframework djangorestframework-simplejwt django-filter
pip install django-cors-headers drf-yasg python-dotenv
pip install firebase-admin requests Pillow stream-chat
# If using Razorpay: pip install razorpay
```

(Or add these to a `requirements.txt` and run `pip install -r requirements.txt`.)

### 3. Environment variables

Create `connecto/.env` (and optionally set in `settings.py`):

- `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`, `RAZORPAY_WEBHOOK_SECRET` – Razorpay
- `SMS_API_URL`, `SMS_API_KEY`, `SMS_SENDER_ID` – optional; for OTP/delivery SMS and `requests.log`
- Firebase: place service account JSON at `connecto/firebase_key.json` (see `settings.py`)

### 4. Database and run server

```bash
python manage.py migrate
python manage.py createsuperuser   # use mobile number as username if prompted
python manage.py runserver
```

- App: `http://127.0.0.1:8000/`
- Swagger: `http://127.0.0.1:8000/swagger/`
- Admin: `http://127.0.0.1:8000/admin/`
- Admin login (custom): `http://127.0.0.1:8000/users/login-admin/`

---

## Main URL Prefixes

| Prefix        | Description                    |
|---------------|--------------------------------|
| `/`           | Dashboard                      |
| `/admin/`     | Django admin                   |
| `/masters/`   | Masters APIs                   |
| `/vendor/`    | Trip, parcel request, shipments |
| `/users/`     | Auth, profile, KYC, admin login|
| `/customer/`  | Delivery requests, KYC, payments, chat, shipments |
| `/swagger/`   | API docs (Swagger)             |
| `/redoc/`     | API docs (ReDoc)              |

---

## SMS and `requests.log`

SMS is sent when:

1. A new **Customer_Order** is created (OTP generated) – OTP SMS to customer mobile.
2. An order is **marked delivered** (vendor marks delivered or status updated to delivered) – delivery confirmation SMS.

Each attempt is logged to `requests.log` in the project root (including when SMS is skipped because `SMS_API_URL` or `SMS_API_KEY` is not set).

---

## KYC (DigiLocker)

- **Fetch documents:** `GET /customer/kyc/fetch-documents/?client_id=<digilocker_client_id>&refresh=false`
- With `refresh=false`, the API returns already-verified documents from the database when available.
- Approval is based on **Aadhaar verified** only (see `users.models.UserKYC.check_and_update_approval`).
- On restricted environments (e.g. some hosts), external DigiLocker calls may be disabled; the app can still serve cached KYC data from the DB.

---

## License

Proprietary / internal use unless otherwise stated.
