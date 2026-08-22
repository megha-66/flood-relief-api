import jwt # jwt imports the Json Web Token library. APIs will use JWT to authenticate users after login.

import os 

from datetime import datetime, timedelta
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from sqlalchemy import func
from passlib.context import CryptContext

from database import Base, engine, get_db, User, ReliefCamp, ResourceInventory, RoleEnum

from dotenv import load_dotenv

load_dotenv()

# Security Constants
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # password hashing configuration, "bcrypt" is used for hashing
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login") # OAUTH2 token configuration

app = FastAPI(title="Flood Relief Resource & Donation Tracker API")

# --- Pydantic Schemas ---
class UserCreate(BaseModel):
    email: str
    password: str = Field(..., min_length=8, max_length=72)
    role: RoleEnum

class CampCreate(BaseModel):
    name: str
    district: str
    contact_person: str

class InventoryCreate(BaseModel):
    camp_id: int
    item_name: str
    unit: str
    required_quantity: int

# --- Auth Helpers ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password):
    truncated_password = password.encode('utf-8')[:72]
    return pwd_context.hash(truncated_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# --- Authentication Endpoints ---
@app.post("/auth/register", status_code=201)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        email=user_data.email, 
        password_hash=hash_password(user_data.password),
        role=user_data.role
    )
    db.add(user)
    db.commit()
    return {"message": "User created successfully"}

@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

# --- Business Logic Endpoints ---
@app.post("/camps/", status_code=201)
def create_relief_camp(camp: CampCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != RoleEnum.CAMP_COORDINATOR:
        raise HTTPException(status_code=403, detail="Only Camp Coordinators can add relief camps.")
    
    new_camp = ReliefCamp(**camp.model_dump())
    db.add(new_camp)
    db.commit()
    db.refresh(new_camp)
    return new_camp

@app.post("/inventory/", status_code=201)
def log_inventory_requirement(item: InventoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != RoleEnum.CAMP_COORDINATOR:
        raise HTTPException(status_code=403, detail="Only Camp Coordinators can log requirements.")
    
    inventory_item = ResourceInventory(**item.model_dump())
    db.add(inventory_item)
    db.commit()
    return inventory_item

@app.patch("/inventory/{item_id}/pledge")
def pledge_donation(item_id: int, quantity: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.query(ResourceInventory).filter(ResourceInventory.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item.fulfilled_quantity += quantity
    db.commit()
    return {"message": f"Successfully pledged {quantity} units", "current_fulfilled": item.fulfilled_quantity}


@app.get("/inventory/")
def get_inventory(db: Session = Depends(get_db)):
    items = db.query(ResourceInventory).all()

    return [
        {
            "id": item.id,
            "camp_id": item.camp_id,
            "item_name": item.item_name,
            "unit": item.unit,
            "required_quantity": item.required_quantity,
            "fulfilled_quantity": item.fulfilled_quantity,
        }
        for item in items
    ]

# Analytical SQL Aggregation Route
@app.get("/analytics/district-shortages")
def get_district_shortages(db: Session = Depends(get_db)):
    """Computes total pending resource shortages aggregated by district"""
    results = db.query(
        ReliefCamp.district,
        ResourceInventory.item_name,
        ResourceInventory.unit,
        func.sum(ResourceInventory.required_quantity - ResourceInventory.fulfilled_quantity).label("shortage")      ).join(ResourceInventory).group_by(ReliefCamp.district, ResourceInventory.item_name, ResourceInventory.unit).all()
    
    return [{"district": r[0], "item": r[1], "unit": r[2], "shortage_quantity": max(0, r[3])} for r in results]
