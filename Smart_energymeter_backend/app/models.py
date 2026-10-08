from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, func
from sqlalchemy.orm import validates
from app.database import Base
import re




from sqlalchemy import Double, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    contact_number = Column(String(20))
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    reset_token = Column(String)
    reset_token_expires = Column(DateTime(timezone=True))
    preferences = Column(Text, default="{}")

    @validates('email')
    def validate_email(self, key, email):
        if not email:
            raise ValueError("Email is required")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Invalid email format")
        return email

    @validates('contact_number')
    def validate_phone(self, key, number):
        if number and not re.match(r'^\+?1?\d{9,15}$', number):
            raise ValueError("Invalid phone number format")
        return number

    @validates('username')
    def validate_username(self, key, username):
        if not username:
            raise ValueError("Username is required")
        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters long")
        if not re.match("^[a-zA-Z0-9_.-]+$", username):
            raise ValueError("Username can only contain letters, numbers, and _.-")
        return username


class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    machine_name = Column(String(255), nullable=False)
    machine_location = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to machine readings
    readings = relationship("MachineReading", back_populates="machine_details")


class MachineReading(Base):
    __tablename__ = "machine_readings"

    id = Column(Integer, primary_key=True, index=True)
    machine = Column(Integer, ForeignKey("machines.id"), nullable=False)  # This is the foreign key
    timestamp = Column(DateTime, nullable=False)
    watts_total = Column(Double, default=0.0)
    watts_r_phase = Column(Double, default=0.0)
    watts_y_phase = Column(Double, default=0.0)
    watts_b_phase = Column(Double, default=0.0)
    pf_ave = Column(Double, default=0.0)
    pf_r_phase = Column(Double, default=0.0)
    pf_y_phase = Column(Double, default=0.0)
    pf_b_phase = Column(Double, default=0.0)
    va_total = Column(Double, default=0.0)
    va_r_phase = Column(Double, default=0.0)
    va_y_phase = Column(Double, default=0.0)
    va_b_phase = Column(Double, default=0.0)
    vll_average = Column(Double, default=0.0)
    vry_phase = Column(Double, default=0.0)
    vyb_phase = Column(Double, default=0.0)
    vbr_phase = Column(Double, default=0.0)
    vln_average = Column(Double, default=0.0)
    v_r_phase = Column(Double, default=0.0)
    v_y_phase = Column(Double, default=0.0)
    v_b_phase = Column(Double, default=0.0)
    current_total = Column(Double, default=0.0)
    current_r_phase = Column(Double, default=0.0)
    current_y_phase = Column(Double, default=0.0)
    current_b_phase = Column(Double, default=0.0)
    frequency = Column(Double, default=0.0)
    wh_received = Column(Double, default=0.0)

    # Relationship to machine (this is the actual relationship object)
    machine_details = relationship("Machine", back_populates="readings")