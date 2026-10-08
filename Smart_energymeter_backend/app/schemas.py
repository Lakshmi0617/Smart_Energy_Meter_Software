from pydantic import BaseModel, EmailStr

from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    contact_number: str


class UserLogin(BaseModel):
    username: str
    password: str


class PasswordUpdate(BaseModel):
    username: str
    new_password: str




# '''''''below schema is to fecth the data from the table
class MachineBase(BaseModel):
    machine_name: str
    machine_location: str
    status: str


class MachineCreate(MachineBase):
    pass


class MachineResponse(MachineBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class MachineReadingBase(BaseModel):
    machine: int
    timestamp: datetime
    watts_total: Optional[float] = 0.0
    watts_r_phase: Optional[float] = 0.0
    watts_y_phase: Optional[float] = 0.0
    watts_b_phase: Optional[float] = 0.0
    pf_ave: Optional[float] = 0.0
    pf_r_phase: Optional[float] = 0.0
    pf_y_phase: Optional[float] = 0.0
    pf_b_phase: Optional[float] = 0.0
    va_total: Optional[float] = 0.0
    va_r_phase: Optional[float] = 0.0
    va_y_phase: Optional[float] = 0.0
    va_b_phase: Optional[float] = 0.0
    vll_average: Optional[float] = 0.0
    vry_phase: Optional[float] = 0.0
    vyb_phase: Optional[float] = 0.0
    vbr_phase: Optional[float] = 0.0
    vln_average: Optional[float] = 0.0
    v_r_phase: Optional[float] = 0.0
    v_y_phase: Optional[float] = 0.0
    v_b_phase: Optional[float] = 0.0
    current_total: Optional[float] = 0.0
    current_r_phase: Optional[float] = 0.0
    current_y_phase: Optional[float] = 0.0
    current_b_phase: Optional[float] = 0.0
    frequency: Optional[float] = 0.0
    wh_received: Optional[float] = 0.0


class MachineReadingResponse(MachineReadingBase):
    id: int
    machine_name: str
    machine_location: str
    status: str

    class Config:
        from_attributes = True


class LatestMachineDataResponse(BaseModel):
    machine_id: int
    machine_name: str
    machine_location: str
    status: str
    latest_reading: Optional[MachineReadingBase] = None
    last_updated: Optional[datetime] = None

    class Config:
        from_attributes = True