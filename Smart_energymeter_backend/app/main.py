from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends,Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, desc
from sqlalchemy.orm import Session,joinedload
from passlib.context import CryptContext
from app.database import get_db, engine
from app.models import User, Base
from app.schemas import UserCreate, UserLogin, PasswordUpdate



from typing import List, Optional
from app.models import Machine, MachineReading
from app.schemas import (
    MachineResponse,
    MachineReadingResponse,
    LatestMachineDataResponse,
    MachineReadingBase
)


# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="Energy Meter User Management API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if username already exists
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Check if email already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password and create user
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        password=hashed_password,
        contact_number=user.contact_number
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User registered successfully"}


@app.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    # Find user by username
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # Verify password
    if not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"message": "Login successful"}


@app.post("/update-password")
def update_password(password_update: PasswordUpdate, db: Session = Depends(get_db)):
    # Find user by username
    db_user = db.query(User).filter(User.username == password_update.username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Hash new password and update
    hashed_password = pwd_context.hash(password_update.new_password)
    db_user.password = hashed_password
    db.commit()

    return {"message": "Password updated successfully"}


# ''''below is the endpoints to fecth the data from the table
@app.get("/machines", response_model=List[MachineResponse])
def get_all_machines(db: Session = Depends(get_db)):
    """Get all machines"""
    machines = db.query(Machine).all()
    return machines


@app.get("/machine/{machine_id}", response_model=MachineResponse)
def get_machine(machine_id: int, db: Session = Depends(get_db)):
    """Get a specific machine by ID"""
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine


@app.get("/machine/{machine_id}/latest-data", response_model=LatestMachineDataResponse)
def get_latest_machine_data(machine_id: int, db: Session = Depends(get_db)):
    """Get latest reading data for a specific machine"""

    # First check if machine exists
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    # Get the latest reading for this machine
    latest_reading = (
        db.query(MachineReading)
        .filter(MachineReading.machine == machine_id)
        .order_by(desc(MachineReading.timestamp))
        .first()
    )

    # Prepare response
    response = LatestMachineDataResponse(
        machine_id=machine.id,
        machine_name=machine.machine_name,
        machine_location=machine.machine_location,
        status=machine.status,
        latest_reading=None,
        last_updated=None
    )

    if latest_reading:
        # Convert reading to base model
        reading_data = MachineReadingBase(
            machine=latest_reading.machine,
            timestamp=latest_reading.timestamp,
            watts_total=latest_reading.watts_total,
            watts_r_phase=latest_reading.watts_r_phase,
            watts_y_phase=latest_reading.watts_y_phase,
            watts_b_phase=latest_reading.watts_b_phase,
            pf_ave=latest_reading.pf_ave,
            pf_r_phase=latest_reading.pf_r_phase,
            pf_y_phase=latest_reading.pf_y_phase,
            pf_b_phase=latest_reading.pf_b_phase,
            va_total=latest_reading.va_total,
            va_r_phase=latest_reading.va_r_phase,
            va_y_phase=latest_reading.va_y_phase,
            va_b_phase=latest_reading.va_b_phase,
            vll_average=latest_reading.vll_average,
            vry_phase=latest_reading.vry_phase,
            vyb_phase=latest_reading.vyb_phase,
            vbr_phase=latest_reading.vbr_phase,
            vln_average=latest_reading.vln_average,
            v_r_phase=latest_reading.v_r_phase,
            v_y_phase=latest_reading.v_y_phase,
            v_b_phase=latest_reading.v_b_phase,
            current_total=latest_reading.current_total,
            current_r_phase=latest_reading.current_r_phase,
            current_y_phase=latest_reading.current_y_phase,
            current_b_phase=latest_reading.current_b_phase,
            frequency=latest_reading.frequency,
            wh_received=latest_reading.wh_received
        )

        response.latest_reading = reading_data
        response.last_updated = latest_reading.timestamp

    return response


@app.get("/machine/{machine_id}/readings", response_model=List[MachineReadingResponse])
def get_machine_readings(
        machine_id: int,
        limit: int = Query(default=10, le=100),
        db: Session = Depends(get_db)
):
    """Get readings for a specific machine with limit"""

    # Check if machine exists
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    # Get readings with machine details
    readings = (
        db.query(MachineReading, Machine)
        .join(Machine, MachineReading.machine == Machine.id)
        .filter(MachineReading.machine == machine_id)
        .order_by(desc(MachineReading.timestamp))
        .limit(limit)
        .all()
    )

    # Format response
    result = []
    for reading, machine_info in readings:
        reading_dict = {
            "id": reading.id,
            "machine": reading.machine,
            "timestamp": reading.timestamp,
            "watts_total": reading.watts_total,
            "watts_r_phase": reading.watts_r_phase,
            "watts_y_phase": reading.watts_y_phase,
            "watts_b_phase": reading.watts_b_phase,
            "pf_ave": reading.pf_ave,
            "pf_r_phase": reading.pf_r_phase,
            "pf_y_phase": reading.pf_y_phase,
            "pf_b_phase": reading.pf_b_phase,
            "va_total": reading.va_total,
            "va_r_phase": reading.va_r_phase,
            "va_y_phase": reading.va_y_phase,
            "va_b_phase": reading.va_b_phase,
            "vil_average": reading.vil_average,
            "vry_phase": reading.vry_phase,
            "vyb_phase": reading.vyb_phase,
            "vbr_phase": reading.vbr_phase,
            "vin_average": reading.vin_average,
            "v_r_phase": reading.v_r_phase,
            "v_y_phase": reading.v_y_phase,
            "v_b_phase": reading.v_b_phase,
            "current_total": reading.current_total,
            "current_r_phase": reading.current_r_phase,
            "current_y_phase": reading.current_y_phase,
            "current_b_phase": reading.current_b_phase,
            "frequency": reading.frequency,
            "wh_received": reading.wh_received,
            "machine_name": machine_info.machine_name,
            "machine_location": machine_info.machine_location,
            "status": machine_info.status
        }
        result.append(reading_dict)

    return result


@app.get("/machines/status-summary")
def get_machines_status_summary(db: Session = Depends(get_db)):
    """Get summary of all machines with their latest reading timestamp"""

    # Get all machines with their latest reading timestamp
    subquery = (
        db.query(
            MachineReading.machine,
            func.max(MachineReading.timestamp).label('latest_timestamp')
        )
        .group_by(MachineReading.machine)
        .subquery()
    )

    machines_with_latest = (
        db.query(Machine, subquery.c.latest_timestamp)
        .outerjoin(subquery, Machine.id == subquery.c.machine)
        .all()
    )

    result = []
    for machine, latest_timestamp in machines_with_latest:
        result.append({
            "machine_id": machine.id,
            "machine_name": machine.machine_name,
            "machine_location": machine.machine_location,
            "status": machine.status,
            "last_reading_time": latest_timestamp,
            "has_data": latest_timestamp is not None
        })

    return {"machines": result, "total_machines": len(result)}


@app.get("/machine/{machine_id}/readings/date-range")
def get_machine_readings_by_date_range(
        machine_id: int,
        start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
        end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
        parameters: Optional[str] = Query(None,
                                          description="Comma-separated list of parameters to include (e.g., 'watts_total,current_total,frequency')"),
        limit: int = Query(default=100, le=1000, description="Maximum number of records to return"),
        db: Session = Depends(get_db)
):
    """
    Get machine readings within a date range with optional parameter filtering

    Parameters:
    - machine_id: ID of the machine
    - start_date: Start date in YYYY-MM-DD format (without timezone)
    - end_date: End date in YYYY-MM-DD format (without timezone)
    - parameters: Optional comma-separated list of specific parameters to include
    - limit: Maximum number of records (default 100, max 1000)
    """

    # Check if machine exists
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    try:
        # Parse dates (assuming no timezone, treating as naive datetime)
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)

        if start_datetime > end_datetime:
            raise HTTPException(status_code=400, detail="Start date must be before or equal to end date")

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD format")

    # Define all available parameters from MachineReading model
    available_parameters = {
        'timestamp', 'watts_total', 'watts_r_phase', 'watts_y_phase', 'watts_b_phase',
        'pf_ave', 'pf_r_phase', 'pf_y_phase', 'pf_b_phase',
        'va_total', 'va_r_phase', 'va_y_phase', 'va_b_phase',
        'vll_average', 'vry_phase', 'vyb_phase', 'vbr_phase',
        'vln_average', 'v_r_phase', 'v_y_phase', 'v_b_phase',
        'current_total', 'current_r_phase', 'current_y_phase', 'current_b_phase',
        'frequency', 'wh_received'
    }

    # Parse requested parameters
    selected_parameters = None
    if parameters:
        selected_parameters = [param.strip() for param in parameters.split(',')]
        # Validate parameters
        invalid_params = set(selected_parameters) - available_parameters
        if invalid_params:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid parameters: {', '.join(invalid_params)}. Available parameters: {', '.join(sorted(available_parameters))}"
            )

    # Build query
    query = db.query(MachineReading).filter(
        MachineReading.machine == machine_id,
        MachineReading.timestamp >= start_datetime,
        MachineReading.timestamp <= end_datetime
    ).order_by(desc(MachineReading.timestamp)).limit(limit)

    readings = query.all()

    # Format response
    result = []
    for reading in readings:
        reading_dict = {
            "id": reading.id,
            "machine_id": reading.machine,
            "timestamp": reading.timestamp
        }

        # If specific parameters are requested, include only those
        if selected_parameters:
            for param in selected_parameters:
                if param != 'timestamp':  # timestamp is already included
                    reading_dict[param] = getattr(reading, param, None)
        else:
            # Include all parameters
            reading_dict.update({
                "watts_total": reading.watts_total,
                "watts_r_phase": reading.watts_r_phase,
                "watts_y_phase": reading.watts_y_phase,
                "watts_b_phase": reading.watts_b_phase,
                "pf_ave": reading.pf_ave,
                "pf_r_phase": reading.pf_r_phase,
                "pf_y_phase": reading.pf_y_phase,
                "pf_b_phase": reading.pf_b_phase,
                "va_total": reading.va_total,
                "va_r_phase": reading.va_r_phase,
                "va_y_phase": reading.va_y_phase,
                "va_b_phase": reading.va_b_phase,
                "vll_average": reading.vll_average,
                "vry_phase": reading.vry_phase,
                "vyb_phase": reading.vyb_phase,
                "vbr_phase": reading.vbr_phase,
                "vln_average": reading.vln_average,
                "v_r_phase": reading.v_r_phase,
                "v_y_phase": reading.v_y_phase,
                "v_b_phase": reading.v_b_phase,
                "current_total": reading.current_total,
                "current_r_phase": reading.current_r_phase,
                "current_y_phase": reading.current_y_phase,
                "current_b_phase": reading.current_b_phase,
                "frequency": reading.frequency,
                "wh_received": reading.wh_received
            })

        result.append(reading_dict)

    return {
        "machine_id": machine_id,
        "machine_name": machine.machine_name,
        "machine_location": machine.machine_location,
        "date_range": {
            "start_date": start_date,
            "end_date": end_date
        },
        "total_records": len(result),
        "selected_parameters": selected_parameters or "all",
        "readings": result
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="172.18.100.214", port=8009)

# to run this backend use this below command
# python -m app.main --reload
