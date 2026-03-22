# Billing-Software-API: Vighnaharta Fataka

A clean, modular Django REST Framework backend for firecracker wholesale billing.

## Tech Stack
- **Framework**: Django & Django REST Framework
- **Authentication**: JWT (Simple JWT)
- **Database**: SQLite (Local), PostgreSQL (Production)
- **CORS**: django-cors-headers
- **Environment Management**: django-environ
- **Reports**: reportlab, pillow

## Project Structure
- `accounts`: User management & roles (OWNER, STAFF)
- `products`: Product & inventory management
- `billing`: Bills & cart management
- `customers`: Customer records
- `reports`: Sales reports & dashboards
- `core`: Shared utilities

## Setup Instructions

### 1. Clone the repository
```bash
git clone <repository-url>
cd Billing-Software-API
```

### 2. Environment Setup
Copy the example environment file and update your values:
```bash
cp .env.example .env
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Start the Server
```bash
python manage.py runserver
```

## API Endpoints
- **JWT Login**: `/api/token/`
- **JWT Refresh**: `/api/token/refresh/`
- **Accounts**: `/api/accounts/`
- **Products**: `/api/products/`
- **Billing**: `/api/billing/`
- **Customers**: `/api/customers/`
- **Reports**: `/api/reports/`
- **Core**: `/api/core/`
