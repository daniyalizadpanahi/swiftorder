# SwiftOrder

SwiftOrder is a scalable and secure Order Management System for an online store. This project is built using **Django REST Framework (DRF)** with **PostgreSQL**, **Redis**, **Celery**, and **Docker** for containerization. It includes features such as user authentication, product and order management, payment processing, API security, and deployment.

## Features

### 1️⃣ User Authentication & Management
- JWT-based authentication (login, registration, logout)
- Role-based access control (Admin, User, Store Manager)
- Password reset via email (SMTP)

### 2️⃣ Product & Order Management
- Full CRUD operations for products
- Order management (Add to cart, checkout, order tracking)
- Online payment integration (Zarinpal or Stripe)

### 3️⃣ Security & Optimization
- API protection with Django Permissions & Rate Limiting
- PostgreSQL for efficient data storage
- Redis caching for performance improvement

### 4️⃣ Dockerization & Deployment
- Docker & Docker Compose setup for containerized development
- Deployment support for Render, Railway, or Heroku

### 5️⃣ API Documentation
- API documentation with Swagger or Postman Collection

---

## Installation & Setup

### Prerequisites
- Docker & Docker Compose installed
- PostgreSQL database

### Steps to Run the Project

1. Clone the repository:
   ```sh
   git clone <your-repo-url>
   cd swiftorder
   ```

2. Create an `.env` file in the project root and configure the following values:

   ```env
   DJANGO_ENV=docker
   
   # Database
   DB_NAME=swiftorder_db
   DB_USER=postgres
   DB_PASSWORD=<your_password>
   DB_HOST=db
   DB_PORT=5432
   
   # Django
   SECRET_KEY=rzdy#6oy85%4v3396n(%_1@6q_ic02jl0phaw%6q1wnesv+doo
   DEBUG=True
   ALLOWED_HOSTS=*
   
   # Redis
   REDIS_HOST=redis
   REDIS_PORT=6379
   
   # Email
   EMAIL_HOST_USER=<your_email>
   EMAIL_HOST_PASSWORD=<your_email_password>
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   ```

3. Run the project with Docker:
   ```sh
   docker-compose up --build
   ```

4. Apply migrations:
   ```sh
   docker-compose exec web python manage.py migrate
   ```

5. Create a superuser:
   ```sh
   docker-compose exec web python manage.py createsuperuser
   ```

6. Access the API at:
   - Swagger: `http://localhost:8000/swagger/`
   - Admin Panel: `http://localhost:8000/admin/`

---

## Dependencies
The project dependencies are listed in `requirements.txt`. Some key dependencies include:

- Django 4.2.9
- Django REST Framework
- JWT Authentication
- PostgreSQL
- Celery & Redis
- Swagger (drf-yasg) for API documentation

Install them manually if needed:
```sh
pip install -r requirements.txt
```

---

## API Documentation
API documentation is available using **Swagger** at:
```
http://localhost:8000/swagger/
```
Or a Postman Collection can be imported for testing.

---

## Testing
Run tests using:
```sh
docker-compose exec web pytest
```

---

## Contributor
👤 **Daniyal Izadpanahi**  
🚀 **Solo Developer**

---

## License
This project is licensed under the MIT License.
