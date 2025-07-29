# FastPayQR

FastPayQR is a simple QR-based payment system built with FastAPI. It supports order creation, QR code payments, PDF invoice generation, and email sending via Celery.

## Features

- User authentication with JWT (login/register)
- Create orders with QR code linked to payment URL
- Generate invoice as PDF
- Send invoice via email using Celery
- Wallet top-up support
- Secure payment transaction handling

## Tech Stack

- FastAPI – Web API framework  
- Celery + Redis – Background task processing  
- WeasyPrint / ReportLab / FPDF – PDF generation (customizable)  
- Docker – Containerized services  
- SQLite / PostgreSQL / MySQL / MongoDB – Database options  

---

## Run with Docker

### 1. Build and start the containers

```
docker-compose up --build
```
### 2. Build and start the containers

FastAPI provides interactive API documentation at the `/docs` endpoint of your running server.  
For example, if your server is running at `http://your-domain-or-ip:port` or deployed with HTTPS, open:
```
http://your-domain-or-ip:port/docs
```
or
```
https://your-domain.com/docs
```