from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
app = FastAPI()

# Question 1: Home route
@app.get("/")
def home():
    return {"message": "Welcome to MediCare Clinic"}

# Doctors data
doctors = [
    {"id": 1, "name": "Dr. Aanya Deshmukh", "specialization": "Cardiologist", "fee": 950, "experience_years": 11, "is_available": True},
    {"id": 2, "name": "Dr. Rohan Bhave", "specialization": "Dermatologist", "fee": 700, "experience_years": 9, "is_available": True},
    {"id": 3, "name": "Dr. Sneha Wankhede", "specialization": "Pediatrician", "fee": 650, "experience_years": 8, "is_available": True},
    {"id": 4, "name": "Dr. Kunal Patil", "specialization": "General", "fee": 300, "experience_years": 5, "is_available": True},
    {"id": 5, "name": "Dr. Subodh Gokhale", "specialization": "Cardiologist", "fee": 1100, "experience_years": 14, "is_available": True},
    {"id": 6, "name": "Dr. Neha Bansod", "specialization": "General", "fee": 500, "experience_years": 8, "is_available": False},
    {"id": 7, "name": "Dr. Arjun Mehta", "specialization": "gynecologist", "fee": 500, "experience_years": 7, "is_available": True},
    {"id": 8, "name": "Dr. Anjali Rao", "specialization": "orthopedic", "fee": 1200, "experience_years": 15, "is_available": False}
]

# Request model for booking an appointment
class AppointmentRequest(BaseModel):
    patient_name: str = Field(..., min_length=2)
    doctor_id: int = Field(..., gt=0)
    date: str = Field(..., min_length=8)
    reason: str = Field(..., min_length=5)
    appointment_type: str = "in-person"
    senior_citizen: bool = False

# Question 11: Model for adding a new doctor
class NewDoctor(BaseModel):
    name: str = Field(..., min_length=2)
    specialization: str = Field(..., min_length=2)
    fee: int = Field(..., gt=0)
    experience_years: int = Field(..., gt=0)
    is_available: bool = True

# Question 7: Helper function to find a doctor by ID
def find_doctor(doctor_id):
    for doctor in doctors:
        if doctor["id"] == doctor_id:
            return doctor
    return None

# Question 7: Helper function to calculate appointment fee based on type
def calculate_fee(base_fee, appointment_type, senior_citizen=False):
    original_fee = base_fee
 
    if appointment_type == "video":
        calculated_fee = base_fee * 0.8
    elif appointment_type == "emergency":
        calculated_fee = base_fee * 1.5
    else:
        calculated_fee = base_fee

    if senior_citizen:
        calculated_fee = calculated_fee * 0.85

    return {
        "original_fee": original_fee,
        "discounted_fee": round(calculated_fee, 2)
    }


# Helper function to filter doctors based on optional query parameters
def filter_doctors_logic(specialization=None, max_fee=None, min_experience=None, is_available=None):
    filtered_doctors = doctors

    if specialization is not None:
        filtered_doctors = [
            doctor for doctor in filtered_doctors
            if doctor["specialization"].lower() == specialization.lower()
        ]

    if max_fee is not None:
        filtered_doctors = [
            doctor for doctor in filtered_doctors
            if doctor["fee"] <= max_fee
        ]

    if min_experience is not None:
        filtered_doctors = [
            doctor for doctor in filtered_doctors
            if doctor["experience_years"] >= min_experience
        ]

    if is_available is not None:
        filtered_doctors = [
            doctor for doctor in filtered_doctors
            if doctor["is_available"] == is_available
        ]

    return filtered_doctors

# Store all booked appointments here
appointments = []

# This will help us assign a unique ID to every new appointment
appt_counter = 1

@app.get("/doctors")
def get_all_doctors():
    available_count = sum(1 for doctor in doctors if doctor["is_available"])
    return {
        "total": len(doctors),
        "available_count": available_count,
        "doctors": doctors
    }

@app.post("/doctors", status_code=201)
def add_doctor(doctor: NewDoctor):
    # Check if doctor name already exists
    for existing_doctor in doctors:
        if existing_doctor["name"].lower() == doctor.name.lower():
            return {"error": "Doctor with this name already exists"}

    # Create new doctor record
    new_doctor = {
        "id": len(doctors) + 1,
        "name": doctor.name,
        "specialization": doctor.specialization,
        "fee": doctor.fee,
        "experience_years": doctor.experience_years,
        "is_available": doctor.is_available
    }

    # Add new doctor to the doctors list
    doctors.append(new_doctor)

    return new_doctor

@app.get("/doctors/summary")
def get_doctors_summary():
    # Count available doctors
    available_count = sum(1 for doctor in doctors if doctor["is_available"])

    # Find doctor with highest experience
    most_experienced_doctor = max(doctors, key=lambda doctor: doctor["experience_years"])

    # Find lowest consultation fee
    cheapest_fee = min(doctor["fee"] for doctor in doctors)

    # Count doctors in each specialization
    specialization_count = {}
    for doctor in doctors:
        specialization = doctor["specialization"]
        specialization_count[specialization] = specialization_count.get(specialization, 0) + 1

    return {
        "total_doctors": len(doctors),
        "available_count": available_count,
        "most_experienced_doctor": most_experienced_doctor["name"],
        "cheapest_consultation_fee": cheapest_fee,
        "specialization_count": specialization_count
    }

@app.get("/doctors/filter")
def filter_doctors(
    specialization: str = None,
    max_fee: int = None,
    min_experience: int = None,
    is_available: bool = None
):
    filtered_results = filter_doctors_logic(
        specialization=specialization,
        max_fee=max_fee,
        min_experience=min_experience,
        is_available=is_available
    )

    return {
        "total": len(filtered_results),
        "doctors": filtered_results
    }

# Question 16: Search doctors by keyword in name or specialization

@app.get("/doctors/search")
def search_doctors(keyword: str):
    # Search in doctor name and specialization, case-insensitive
    matched_doctors = [
        doctor for doctor in doctors
        if keyword.lower() in doctor["name"].lower() or keyword.lower() in doctor["specialization"].lower()
    ]

    if not matched_doctors:
        return {
            "message": f"No doctors found matching '{keyword}'",
            "total_found": 0,
            "doctors": []
        }

    return {
        "total_found": len(matched_doctors),
        "doctors": matched_doctors
    }

# Question 17: Sort doctors by fee, name or experience, with asc or desc order

@app.get("/doctors/sort")
def sort_doctors(sort_by: str = "fee", order: str = "asc"):
    # Validate sort field
    allowed_sort_fields = ["fee", "name", "experience_years"]
    if sort_by not in allowed_sort_fields:
        return {
            "error": "Invalid sort_by value. Use fee, name, or experience_years"
        }

    # Validate sort order
    if order not in ["asc", "desc"]:
        return {
            "error": "Invalid order value. Use asc or desc"
        }

    # Sort doctors based on given field and order
    sorted_doctors = sorted(
        doctors,
        key=lambda doctor: doctor[sort_by],
        reverse=True if order == "desc" else False
    )

    return {
        "sort_by": sort_by,
        "order": order,
        "total": len(sorted_doctors),
        "doctors": sorted_doctors
    }

# Question 18: Paginate doctors list with page and limit parameters
@app.get("/doctors/page")
def paginate_doctors(page: int = 1, limit: int = 3):
    # Validate page and limit values
    if page < 1 or limit < 1:
        return {"error": "Page and limit must be greater than 0"}

    # Calculate start and end index for slicing
    start = (page - 1) * limit
    end = start + limit

    # Get paginated doctor records
    paginated_doctors = doctors[start:end]

    # Calculate total pages using ceiling division
    total_pages = (len(doctors) + limit - 1) // limit

    return {
        "page": page,
        "limit": limit,
        "total_doctors": len(doctors),
        "total_pages": total_pages,
        "doctors": paginated_doctors
    }

# Question 20: Combine search, sort and pagination for doctors in a single endpoint
@app.get("/doctors/browse")
def browse_doctors(
    keyword: str = None,
    sort_by: str = "fee",
    order: str = "asc",
    page: int = 1,
    limit: int = 4
):
    # Start with all doctors
    filtered_doctors = doctors

    # Apply keyword search on name and specialization
    if keyword is not None:
        filtered_doctors = [
            doctor for doctor in filtered_doctors
            if keyword.lower() in doctor["name"].lower() or keyword.lower() in doctor["specialization"].lower()
        ]

    # Validate sort field
    allowed_sort_fields = ["fee", "name", "experience_years"]
    if sort_by not in allowed_sort_fields:
        return {"error": "Invalid sort_by value. Use fee, name, or experience_years"}

    # Validate sort order
    if order not in ["asc", "desc"]:
        return {"error": "Invalid order value. Use asc or desc"}

    # Apply sorting
    filtered_doctors = sorted(
        filtered_doctors,
        key=lambda doctor: doctor[sort_by],
        reverse=True if order == "desc" else False
    )

    # Validate page and limit
    if page < 1 or limit < 1:
        return {"error": "Page and limit must be greater than 0"}

    # Apply pagination
    start = (page - 1) * limit
    end = start + limit
    paginated_doctors = filtered_doctors[start:end]

    # Calculate total pages after filtering
    total_results = len(filtered_doctors)
    total_pages = (total_results + limit - 1) // limit

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_results": total_results,
        "total_pages": total_pages,
        "doctors": paginated_doctors
    }


@app.put("/doctors/{doctor_id}")
def update_doctor(doctor_id: int, fee: int = None, is_available: bool = None):
    # Find the doctor by ID
    for doctor in doctors:
        if doctor["id"] == doctor_id:
            # Update fee only if a new value is provided
            if fee is not None:
                doctor["fee"] = fee

            # Update availability only if a new value is provided
            if is_available is not None:
                doctor["is_available"] = is_available

            return {
                "message": "Doctor updated successfully",
                "doctor": doctor
            }

    raise HTTPException(status_code=404, detail="Doctor not found")

#Question 13: Delete a doctor by ID, but only if they have no active scheduled appointments
@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: int):
    # Find the doctor by ID
    for doctor in doctors:
        if doctor["id"] == doctor_id:
            # Check if the doctor has any active scheduled appointments
            for appointment in appointments:
                if appointment["doctor_name"] == doctor["name"] and appointment["status"] == "scheduled":
                    raise HTTPException(status_code=400, detail="Cannot delete doctor with active appointments")
        

            # Remove doctor if no active appointments exist
            doctors.remove(doctor)
            return {"message": "Doctor deleted successfully"}

    raise HTTPException(status_code=404, detail="Doctor not found")


@app.get("/doctors/{doctor_id}")
def get_doctor_by_id(doctor_id: int):
    for doctor in doctors:
        if doctor["id"] == doctor_id:
            return doctor
    return {"error": "Doctor not found"}

@app.post("/appointments")
def book_appointment(appointment: AppointmentRequest):
    global appt_counter

    # Find doctor using helper function
    doctor = find_doctor(appointment.doctor_id)

    # Return error if doctor is not found
    if not doctor:
        return {"error": "Doctor not found"}

    # Check if doctor is available for appointment
    if not doctor["is_available"]:
        return {"error": "Doctor is not available"}

    # Calculate final fee based on appointment type
    fee_details = calculate_fee(doctor["fee"], appointment.appointment_type, appointment.senior_citizen)

    # Create appointment record
    new_appointment = {
        "appointment_id": appt_counter,
        "patient": appointment.patient_name,
        "doctor_name": doctor["name"],
        "date": appointment.date,
        "type": appointment.appointment_type,
        "original_fee": fee_details["original_fee"],
        "discounted_fee": fee_details["discounted_fee"],
        "status": "scheduled"
    }

    doctor["is_available"] = False

    # Store appointment and increase counter
    appointments.append(new_appointment)
    appt_counter += 1

    return new_appointment

@app.get("/appointments/active")
def get_active_appointments():
    # Return only scheduled or confirmed appointments
    active_appointments = [
        appointment for appointment in appointments
        if appointment["status"] in ["scheduled", "confirmed"]
    ]

    return {
        "total": len(active_appointments),
        "appointments": active_appointments
    }

# Question 19: Search appointments by patient name
@app.get("/appointments/search")
def search_appointments(patient_name: str):
    # Search appointments by patient name, case-insensitive
    matched_appointments = [
        appointment for appointment in appointments
        if patient_name.lower() in appointment["patient"].lower()
    ]

    if not matched_appointments:
        return {
            "message": f"No appointments found for patient name '{patient_name}'",
            "total_found": 0,
            "appointments": []
        }

    return {
        "total_found": len(matched_appointments),
        "appointments": matched_appointments
    }


@app.get("/appointments/sort")
def sort_appointments(sort_by: str = "date", order: str = "asc"):
    # Validate sort field
    allowed_sort_fields = ["discounted_fee", "date"]
    if sort_by not in allowed_sort_fields:
        return {"error": "Invalid sort_by value. Use discounted_fee or date"}

    # Validate sort order
    if order not in ["asc", "desc"]:
        return {"error": "Invalid order value. Use asc or desc"}

    # Sort appointments based on selected field and order
    sorted_appointments = sorted(
        appointments,
        key=lambda appointment: appointment[sort_by],
        reverse=True if order == "desc" else False
    )

    return {
        "sort_by": sort_by,
        "order": order,
        "total": len(sorted_appointments),
        "appointments": sorted_appointments
    }


@app.get("/appointments/page")
def paginate_appointments(page: int = 1, limit: int = 3):
    # Validate page and limit values
    if page < 1 or limit < 1:
        return {"error": "Page and limit must be greater than 0"}

    # Calculate start and end index for slicing
    start = (page - 1) * limit
    end = start + limit

    # Get paginated appointments
    paginated_appointments = appointments[start:end]

    # Calculate total pages using ceiling division
    total_pages = (len(appointments) + limit - 1) // limit

    return {
        "page": page,
        "limit": limit,
        "total_appointments": len(appointments),
        "total_pages": total_pages,
        "appointments": paginated_appointments
    }


@app.post("/appointments/{appointment_id}/confirm")
def confirm_appointment(appointment_id: int):
    # Find appointment by ID
    for appointment in appointments:
        if appointment["appointment_id"] == appointment_id:
            appointment["status"] = "confirmed"
            return {
                "message": "Appointment confirmed successfully",
                "appointment": appointment
            }

    raise HTTPException(status_code=404, detail="Appointment not found")


@app.post("/appointments/{appointment_id}/cancel")
def cancel_appointment(appointment_id: int):
    # Find appointment by ID
    for appointment in appointments:
        if appointment["appointment_id"] == appointment_id:
            appointment["status"] = "cancelled"

            # Mark doctor available again after cancellation
            for doctor in doctors:
                if doctor["name"] == appointment["doctor_name"]:
                    doctor["is_available"] = True
                    break

            return {
                "message": "Appointment cancelled successfully",
                "appointment": appointment
            }

    raise HTTPException(status_code=404, detail="Appointment not found")

@app.post("/appointments/{appointment_id}/complete")
def complete_appointment(appointment_id: int):
    # Find appointment by ID
    for appointment in appointments:
        if appointment["appointment_id"] == appointment_id:
            appointment["status"] = "completed"

            # Mark doctor available again after completion
            for doctor in doctors:
                if doctor["name"] == appointment["doctor_name"]:
                    doctor["is_available"] = True
                    break

            return {
                "message": "Appointment completed successfully",
                "appointment": appointment
            }

    raise HTTPException(status_code=404, detail="Appointment not found")

@app.get("/appointments/by-doctor/{doctor_id}")
def get_appointments_by_doctor(doctor_id: int):
    # Find doctor by ID
    doctor = find_doctor(doctor_id)

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Return all appointments for the selected doctor
    doctor_appointments = [
        appointment for appointment in appointments
        if appointment["doctor_name"] == doctor["name"]
    ]

    return {
        "doctor_id": doctor_id,
        "doctor_name": doctor["name"],
        "total": len(doctor_appointments),
        "appointments": doctor_appointments
    }

@app.get("/appointments")
def get_all_appointments():
    # Return all appointments along with the total count
    return {
        "total": len(appointments),
        "appointments": appointments
    }




