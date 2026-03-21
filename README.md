# 🩺 FastAPI Medical Appointment System

A backend project built using **FastAPI** as part of my internship training at **Innomatics Research Labs**. This project simulates a real-world **medical appointment booking system** where patients can explore doctors, book appointments, manage appointment status, and access doctor and appointment data using filtering, search, sorting, and pagination.

## Project Overview

The **Medical Appointment System** is designed to manage doctor records and patient appointments through clean and structured APIs. It covers core backend workflows such as doctor management, appointment booking, appointment status tracking, and advanced data browsing.

This project was developed to apply all major FastAPI concepts learned during training, including:
- GET APIs
- POST APIs with Pydantic validation
- Helper functions
- CRUD operations
- Multi-step workflows
- Search, sorting, and pagination

## Core Features

### Doctor Management
- View all doctors
- Get doctor details by ID
- View doctor summary statistics
- Filter doctors by specialization, consultation fee, experience, and availability
- Add new doctors
- Update doctor fee and availability
- Delete doctors with safety checks

### Appointment Management
- Book a new appointment
- Confirm scheduled appointments
- Cancel appointments
- Complete appointments
- View all appointments
- View active appointments
- View appointments for a specific doctor

### Advanced API Features
- Search doctors by name or specialization
- Sort doctors by name, fee, or experience
- Paginate doctors list
- Combined doctor browse endpoint with search + sort + pagination
- Search appointments by patient name
- Sort appointments by date or discounted fee
- Paginate appointments list

## Appointment Workflow

The project follows a structured appointment lifecycle:

- **Book Appointment** → creates a new appointment with status `scheduled`
- **Confirm Appointment** → updates status to `confirmed`
- **Cancel Appointment** → updates status to `cancelled` and releases doctor availability
- **Complete Appointment** → updates status to `completed` and makes the doctor available again

This multi-step workflow reflects a realistic backend process for appointment handling.

## Business Logic

A key part of the system is the consultation fee calculation logic.

### Fee Rules
- **In-person appointment** → full doctor fee
- **Video consultation** → 80% of doctor fee
- **Emergency consultation** → 150% of doctor fee

### Senior Citizen Discount
- If the patient is a senior citizen, an additional **15% discount** is applied on the calculated fee.

The system stores both:
- `original_fee`
- `discounted_fee`

This keeps the billing process transparent and easy to understand.

## Tech Stack

- **Python**
- **FastAPI**
- **Pydantic**
- **Uvicorn**
- **Swagger UI**

## Project Structure

```bash
fastapi-medical-appointment-system/
│
├── screenshots/
├── main.py
├── requirements.txt
└── README.md
```
▶️ How to Run the Project

### 1. Install dependencies
```bash
pip install fastapi uvicorn
```

### 2. Run the server
```bash
uvicorn main:app --reload
```

### 3. Open API Docs
```
http://127.0.0.1:8000/docs
```

> This will open Swagger UI where all endpoints can be tested interactively.

## Conclusion

Working on this project gave me hands-on experience in building a complete backend system using **FastAPI**, from designing APIs to managing real application workflows. The **Medical Appointment System** helped me combine technical concepts like CRUD operations, validation, and advanced API features into one practical project.
