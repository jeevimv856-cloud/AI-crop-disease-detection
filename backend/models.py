# models.py — SQLAlchemy ORM Table Definitions

from sqlalchemy import (Column, Integer, String, Float,
                        Boolean, DateTime, Text, Enum, ForeignKey)
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    user_id    = Column(Integer, primary_key=True, index=True)
    name       = Column(String(100), nullable=False)
    phone      = Column(String(15), unique=True)
    location   = Column(String(100))
    created_at = Column(DateTime, default=func.now())

class Crop(Base):
    __tablename__ = "crops"
    crop_id     = Column(Integer, primary_key=True)
    crop_name   = Column(String(50), unique=True, nullable=False)
    description = Column(Text)

class Disease(Base):
    __tablename__ = "diseases"
    disease_id   = Column(Integer, primary_key=True)
    crop_id      = Column(Integer, ForeignKey("crops.crop_id"))
    disease_name = Column(String(100), nullable=False)
    class_label  = Column(String(100), unique=True)
    description  = Column(Text)
    severity     = Column(Enum('None','Medium','High','Very High'))

class ScanRecord(Base):
    __tablename__ = "scan_records"
    scan_id    = Column(Integer, primary_key=True)
    user_id    = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    disease_id = Column(Integer, ForeignKey("diseases.disease_id"))
    image_path = Column(String(255), nullable=False)
    confidence = Column(Float, nullable=False)
    scanned_at = Column(DateTime, default=func.now())

class Feedback(Base):
    __tablename__ = "feedback"
    feedback_id  = Column(Integer, primary_key=True)
    scan_id      = Column(Integer, ForeignKey("scan_records.scan_id"))
    is_correct   = Column(Boolean, nullable=False)
    comments     = Column(Text)
    submitted_at = Column(DateTime, default=func.now())
