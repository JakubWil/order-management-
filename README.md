# 🛒 Order Management API

A production-ready REST API for managing an e-commerce store — built with **FastAPI**, **PostgreSQL (Supabase)**, and **JWT authentication**.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Running Tests](#running-tests)
- [Database Schema](#database-schema)

---

## Overview

This project is a backend API for an order management system. It handles:

- 🔐 User registration and login with JWT tokens
- 📦 Full product management (CRUD)
- 🧾 Order creation with automatic stock management
- ✅ Automated test suite with pytest

---

## Tech Stack

| Technology            | Purpose                     |
| --------------------- | --------------------------- |
| **Python 3.12**       | Core language               |
| **FastAPI**           | Web framework               |
| **Supabase**          | PostgreSQL database (cloud) |
| **JWT (python-jose)** | Authentication tokens       |
| **bcrypt**            | Password hashing            |
| **Poetry**            | Dependency management       |
| **pytest**            | Automated testing           |
| **Uvicorn**           | ASGI server                 |

---

## Project Structure

```
order-management-api/
│
├── app/
│   ├── main.py          # FastAPI app entry point, router registration
│   ├── config.py        # Environment variables loader
│   ├── database.py      # Supabase client connection
│   ├── auth.py          # JWT logic, password hashing, token verification
│   ├── models.py        # Pydantic schemas for request validation
│   └── routers/
│       ├── auth.py      # /auth/register, /auth/login endpoints
│       ├── products.py  # /products CRUD endpoints
│       └── orders.py    # /orders endpoints
│
├── tests/
│   ├── conftest.py      # Shared fixtures (test client, auth headers)
│   ├── test_auth.py     # Authentication tests
│   ├── test_products.py # Product CRUD tests
│   └── test_orders.py   # Order creation and retrieval tests
│
├── .env                 # Secret keys — never commit this file
├── .env.example         # Template for environment variables
├── .gitignore
├── pyproject.toml       # Project dependencies (Poetry)
├── poetry.lock          # Locked dependency versions
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- [Poetry](https://python-poetry.org/docs/#installation)
- A [Supabase](https://supabase.com) account with a project created

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/your-username/order-management-api.git
cd order-management-api
```

**2. Install dependencies**

```bash
poetry install
```

**3. Set up environment variables**

```bash
cp .env.example .env
```

Fill in your values in `.env` (see [Environment Variables](#environment-variables)).

**4. Set up the database**

Run the following SQL in your Supabase SQL Editor:

```sql
CREATE TABLE users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE products (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE orders (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL,
    status TEXT DEFAULT 'pending',
    total_price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE order_items (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    order_id UUID REFERENCES orders(id),
    product_id UUID REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL
);
```

**5. Run the development server**

```bash
poetry run uvicorn app.main:app --reload
```

The API is now running at `http://localhost:8000`

Interactive API docs available at `http://localhost:8000/docs`

---

## Environment Variables

Create a `.env` file based on `.env.example`:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SECRET_KEY=your_secret_key_minimum_32_characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

To generate a secure `SECRET_KEY`:

```bash
poetry run python -c "import secrets; print(secrets.token_hex(32))"
```

> ⚠️ Never commit your `.env` file. It contains sensitive credentials.

---

## API Reference

### Authentication

| Method | Endpoint         | Description                 | Auth required |
| ------ | ---------------- | --------------------------- | ------------- |
| POST   | `/auth/register` | Create a new account        | No            |
| POST   | `/auth/login`    | Login and receive JWT token | No            |

**Register:**

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "YourPassword123"}'
```

**Login:**

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "YourPassword123"}'
```

---

### Products

| Method | Endpoint         | Description          | Auth required |
| ------ | ---------------- | -------------------- | ------------- |
| GET    | `/products/`     | List all products    | No            |
| GET    | `/products/{id}` | Get a single product | No            |
| POST   | `/products/`     | Create a product     | ✅ Yes        |
| PATCH  | `/products/{id}` | Update a product     | ✅ Yes        |
| DELETE | `/products/{id}` | Delete a product     | ✅ Yes        |

**Create a product:**

```bash
curl -X POST http://localhost:8000/products/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Laptop", "description": "A great laptop", "price": 2999.99, "stock": 10}'
```

---

### Orders

| Method | Endpoint              | Description               | Auth required |
| ------ | --------------------- | ------------------------- | ------------- |
| POST   | `/orders/`            | Place a new order         | ✅ Yes        |
| GET    | `/orders/`            | Get current user's orders | ✅ Yes        |
| GET    | `/orders/{id}`        | Get order details         | ✅ Yes        |
| PATCH  | `/orders/{id}/status` | Update order status       | ✅ Yes        |

**Place an order:**

```bash
curl -X POST http://localhost:8000/orders/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"items": [{"product_id": "PRODUCT_UUID", "quantity": 2}]}'
```

**Order statuses:** `pending` → `confirmed` → `shipped` → `delivered` / `cancelled`

---

## Running Tests

```bash
poetry run pytest
```

For detailed output:

```bash
poetry run pytest -v
```

Expected output:

```
tests/test_auth.py::test_register_success           PASSED
tests/test_auth.py::test_register_duplicate_email   PASSED
tests/test_auth.py::test_login_success              PASSED
tests/test_auth.py::test_login_wrong_password       PASSED
tests/test_products.py::test_get_products_public    PASSED
tests/test_products.py::test_create_product         PASSED
tests/test_orders.py::test_create_order_success     PASSED
...
```

---

## Database Schema

```
users
 └── id, email, hashed_password, is_active, created_at

products
 └── id, name, description, price, stock, created_at

orders
 ├── id, user_id (→ users), status, total_price, created_at
 └── order_items
      └── id, order_id (→ orders), product_id (→ products), quantity, unit_price
```

---

## License

MIT
