# WorkBuddy – On-Demand Service Marketplace Platform

WorkBuddy is a full-stack on-demand service marketplace designed to connect **Customers**, **Service Professionals**, and **Administrators**. The system provides end-to-end service discovery, slot scheduling, booking lifecycle management, OTP-verified authentication, and role-specific dashboards through both a React web application and an interactive CLI.

---

## Table of Contents

- [System Architecture](#system-architecture)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Project Directory Structure](#project-directory-structure)
- [Database Schema](#database-schema)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [1. Clone Repository & Setup Virtual Environment](#1-clone-repository--setup-virtual-environment)
  - [2. Configure Environment Variables](#2-configure-environment-variables)
  - [3. Initialize & Seed Database](#3-initialize--seed-database)
  - [4. Run Backend Server](#4-run-backend-server)
  - [5. Run Frontend Client](#5-run-frontend-client)
- [Demo Test Credentials](#demo-test-credentials)
- [REST API Endpoints](#rest-api-endpoints)
- [Testing](#testing)
- [UML Diagrams](#uml-diagrams)

---

## System Architecture

The application is structured following a strict **Layered (N-Tier) Architecture** with separation of concerns:

```
[ React 18 + Tailwind UI (Port 3000) ]  /  [ Terminal CLI (main.py) ]
                          │
                   HTTP REST / JSON
                          ▼
            [ Flask REST API (api.py - Port 5000) ]
                          │
          [ Controller Layer (controllers/) ]
                          │
          [ Service / Business Logic (services/) ]
                          │
          [ Repository / Data Access (repositories/) ]
                          │
           [ Domain Models (models/) ]
                          │
      Parameterized SQL Queries (mysql-connector-python)
                          ▼
             [ MySQL Database (workbuddy) ]
```

1. **Presentation Layer:**
   - **Web UI:** React 18 SPA built with Vite, styled using Tailwind CSS, featuring role-based protected routes and context-driven authentication.
   - **CLI Client:** Terminal-based menu for offline interaction, verification, and testing.
2. **API Layer (`api.py`):** Flask application exposing RESTful JSON endpoints, session management, CORS support, and role-validation middleware.
3. **Controller Layer (`controllers/`):** Orchestrates console I/O and user flows for Admin, Customer, and Professional users.
4. **Service Layer (`services/`):** Contains core domain rules (OTP generation and expiration, scheduling conflict detection, booking state machine transitions, fee and invoice calculations).
5. **Repository Layer (`repositories/`):** Encapsulates all raw SQL queries using parameterized statements to prevent SQL injection.
6. **Persistence Layer:** Relational MySQL schema with foreign keys, cascading rules, and relational integrity.

---

## Key Features

### 1. User & Authentication System
- **Role-Based Access Control (RBAC):** Distinct permissions for `admin`, `customer`, and `professional`.
- **OTP Verification Flow:** Simulates a time-bounded 6-digit OTP verification mechanism upon registration before account activation.
- **Session Authentication:** Secure session-based auth with credential verification and role verification checks.

### 2. Customer Workflow
- **Service Browsing:** Browse catalog of available home services with baseline pricing and descriptions.
- **Provider Filtering:** Discover approved professionals offering specific services, comparing custom hourly rates, ratings, and operating areas.
- **Real-Time Slot Scheduling:** View open calendar slots of professionals to book immediate or scheduled appointments.
- **Booking Management:** Track booking statuses (`pending`, `accepted`, `rejected`, `completed`, `cancelled`) and settle invoices via cash or mock UPI.

### 3. Professional Workflow
- **Profile Onboarding:** Specify operating area, trade experience, and work radius. Profiles undergo administrative review before taking bookings.
- **Custom Service Catalog:** Link multiple skills/services with custom pricing overrides.
- **Availability Management:** Create and publish discrete date/time slots.
- **Request Dispatch:** Review incoming job requests with options to accept or reject, and mark active jobs as completed.

### 4. Admin Workflow
- **Service Catalog Management:** Add and update master platform services with default baseline pricing and estimated duration.
- **Professional Verification:** Review pending professional registrations and grant verification or reject applicants.
- **System Metrics & Monitoring:** View system-wide bookings, registered users, and active service requests.

---

## Tech Stack

| Domain | Technologies |
| :--- | :--- |
| **Frontend** | React 18, Vite, Tailwind CSS, Lucide Icons, React Router DOM |
| **Backend** | Python 3.10+, Flask, Flask-CORS |
| **Database** | MySQL 8.0+, `mysql-connector-python` |
| **Architecture** | Repository Pattern, Layered Architecture, RESTful API |
| **Testing** | Python `unittest` framework |
| **Environment** | `python-dotenv` |

---

## Project Directory Structure

```
work_buddy_code/
├── api.py                     # Flask REST API server (Port 5000)
├── main.py                    # Terminal CLI application entrypoint
├── init_db.py                 # Automated MySQL schema provisioner
├── data.py                    # Mock database seeder (users, services, slots)
├── run_tests.py               # Test runner with clean output logging
├── requirements.txt           # Python backend dependencies
├── .env.example               # Environment variables configuration template
├── .gitignore                 # Exclusion rules for secrets, builds, and venvs
├── README.md                  # System documentation
│
├── controllers/               # CLI Interaction layer
│   ├── admin_controller.py
│   ├── customer_controller.py
│   └── professional_controller.py
│
├── services/                  # Business logic & domain workflows
│   ├── admin_service.py
│   ├── auth_service.py
│   ├── booking_scheduler.py
│   ├── booking_service.py
│   ├── customer_service.py
│   ├── payment_service.py
│   └── professional_service.py
│
├── repositories/              # Data access layer & SQL queries
│   ├── booking_repository.py
│   ├── customer_repository.py
│   ├── invoice_repository.py
│   ├── otp_repository.py
│   ├── professional_repository.py
│   ├── service_repository.py
│   ├── time_slot_repository.py
│   └── user_repository.py
│
├── models/                    # Domain entity definitions
│   ├── admin.py
│   ├── booking.py
│   ├── customer.py
│   ├── professional.py
│   ├── service.py
│   └── user.py
│
├── database/                  # Schema files & migration updates
│   ├── db.py                  # Database connection utility
│   ├── setup_db.sql           # Base database schema DDL
│   └── final_schema_update.py # Schema migrations & foreign key updates
│
├── tests/                     # Unit, service, and integration tests
│   ├── test_admin.py
│   ├── test_auth.py
│   ├── test_booking.py
│   ├── test_customer.py
│   ├── test_integration.py
│   ├── test_invoice.py
│   ├── test_models.py
│   ├── test_payment.py
│   ├── test_professional.py
│   └── test_scheduler.py
│
├── uml diagrams/              # Architectural PNG visual diagrams
│   ├── Class Diagram.png
│   ├── sequence Diagram.png
│   ├── activity diagram.png
│   ├── component diagram.png
│   ├── Deployment Diagram.png
│   └── final use case.png
│
└── workbuddy-frontend/        # React + Vite frontend application
    ├── src/
    │   ├── components/        # Reusable UI cards, modals, buttons
    │   ├── context/           # AuthContext & ThemeContext
    │   ├── layouts/           # Dashboard & Auth wrapper layouts
    │   ├── pages/             # Admin, Customer, and Pro views
    │   └── services/          # Frontend Axios/Fetch API clients
    ├── package.json
    ├── tailwind.config.js
    └── vite.config.js
```

---

## Database Schema

The database consists of relational tables with strict foreign key constraints:

- **`users`**: User identity, role (`admin`, `customer`, `professional`), phone credentials, verification flag.
- **`otp_verification`**: Transient OTP tokens linked to `user_id` with expiration timestamp.
- **`services`**: Master service directory (name, baseline price, estimated execution time).
- **`professionals`**: Professional profiles (experience, service area, operating radius, approval status).
- **`professional_services`**: Many-to-many bridge mapping professionals to services with custom price quotes.
- **`time_slots`**: Date and time window availability per professional (`is_booked` state).
- **`bookings`**: Booking records tracking state (`pending`, `accepted`, `rejected`, `completed`, `cancelled`), chosen time slot, and payment metadata.
- **`invoices`**: Invoiced charge linked to a booking with payment status (`pending`, `paid`) and method (`cash`, `upi`).

---

## Getting Started

### Prerequisites

- **Python 3.10+**
- **Node.js 18+ & npm**
- **MySQL Server 8.0+** running locally

---

### 1. Clone Repository & Setup Virtual Environment

```bash
git clone https://github.com/Rhydham-966/Work_Buddy_Software_Engineering_Project.git
cd Work_Buddy_Software_Engineering_Project/work_buddy_code

# Create virtual environment
python -m venv .venv

# Activate environment
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# On Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### 2. Configure Environment Variables

Create a `.env` file in the `work_buddy_code` root directory:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=workbuddy
```

---

### 3. Initialize & Seed Database

Ensure your MySQL server is running, then execute:

```bash
# 1. Provision database tables and baseline schema
python init_db.py

# 2. Apply final schema updates & foreign keys
python database/final_schema_update.py

# 3. Seed demonstration accounts, services, and bookings
python data.py
```

---

### 4. Run Backend Server

#### Option A: Web REST API Server (Required for Frontend)
```bash
python api.py
```
*API will listen on `http://localhost:5000` with endpoints available under `http://localhost:5000/api`.*

#### Option B: Terminal CLI Interface
```bash
python main.py
```

---

### 5. Run Frontend Client

In a separate terminal window:

```bash
cd workbuddy-frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

*Open your browser at `http://localhost:3000` (Vite dev server proxies API calls to backend port 5000).*

---

## Demo Test Credentials

The database seeder (`data.py`) pre-populates verified accounts for immediate testing:

| Role | Name | Phone / Login | Password | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Admin** | Admin Master | `admin1` | `pass` | Manage services & approve professionals |
| **Professional** | Pro John (Plumber) | `pro1` | `pass` | Service pricing, manage slots, accept jobs |
| **Professional** | Pro Mike (Electrician) | `pro2` | `pass` | Manage electrical bookings |
| **Professional** | Pro Sarah (Cleaner) | `pro3` | `pass` | Manage cleaning bookings |
| **Customer** | Cust Alice | `cust1` | `pass` | Browse, book, and review services |
| **Customer** | Cust Bob | `cust2` | `pass` | General customer booking flow |

---

## REST API Endpoints

### Authentication
- `POST /api/auth/register` - Create an account and receive verification OTP.
- `POST /api/auth/verify-otp` - Confirm registration with 6-digit token.
- `POST /api/auth/login` - Authenticate user credentials and establish session.
- `POST /api/auth/logout` - Invalidate active session.
- `GET  /api/auth/me` - Retrieve current authenticated profile.

### Customer
- `GET  /api/customer/services` - List all master services.
- `GET  /api/customer/services/<id>/professionals` - List verified professionals offering a service.
- `GET  /api/customer/professionals/<id>/slots` - Fetch open time slots for a professional.
- `POST /api/customer/bookings` - Submit a new appointment booking.
- `GET  /api/customer/bookings` - Retrieve active bookings for the customer.
- `POST /api/customer/bookings/<id>/cancel` - Cancel a scheduled appointment.
- `POST /api/customer/bookings/<id>/pay` - Process booking invoice payment.

### Professional
- `GET  /api/professional/profile` - View professional profile and approval status.
- `POST /api/professional/profile` - Setup or update operating area and radius.
- `GET  /api/professional/services` - View assigned services with custom pricing.
- `POST /api/professional/services` - Link a service with custom price quote.
- `GET  /api/professional/slots` - View configured availability time slots.
- `POST /api/professional/slots` - Create a new availability window.
- `POST /api/professional/bookings/<id>/accept` - Accept incoming customer request.
- `POST /api/professional/bookings/<id>/reject` - Decline booking request.
- `POST /api/professional/bookings/<id>/complete` - Mark booking as finished.

### Admin
- `GET  /api/admin/services` - View platform service catalog.
- `POST /api/admin/services` - Register a new service category.
- `GET  /api/admin/pending-professionals` - List professionals awaiting review.
- `POST /api/admin/approve/<id>` - Approve a professional.
- `POST /api/admin/reject/<id>` - Reject a professional application.

---

## Testing

The project includes unit, service, and integration tests covering authentication, scheduling conflicts, booking lifecycle, and admin controls.

Run the automated test suite:

```bash
python run_tests.py
```

All 30+ tests will execute against mocked and isolated scenarios, logging output to `clean_test_output.txt`.

---

## UML Diagrams

Visual architecture specifications are available under the [`uml diagrams/`](uml%20diagrams/) directory:

- **Class Diagram** (`uml diagrams/Class Diagram.png`): Entity models, relationships, and attributes.
- **Sequence Diagram** (`uml diagrams/sequence Diagram.png`): End-to-end booking and OTP verification workflow.
- **Activity Diagram** (`uml diagrams/activity diagram.png`): State transitions across user interactions.
- **Component Diagram** (`uml diagrams/component diagram.png`): Modularity between React, Flask, and MySQL layers.
- **Deployment Diagram** (`uml diagrams/Deployment Diagram.png`): Host, proxy, and database topology.
- **Use Case Diagram** (`uml diagrams/final use case.png`): Actor functional boundaries.
