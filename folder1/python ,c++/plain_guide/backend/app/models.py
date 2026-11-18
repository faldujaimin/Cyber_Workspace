from datetime import datetime

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    role = Column(String(50), default="pilot")
    created_at = Column(String(30), default=lambda: datetime.utcnow().isoformat())


class AircraftProfile(Base):
    __tablename__ = "aircraft_profiles"

    id = Column(Integer, primary_key=True, index=True)
    registration = Column(String(20), unique=True, nullable=False)
    aircraft_type = Column(String(50), nullable=False)
    cruise_altitude = Column(Float, default=30000)
    max_altitude = Column(Float, default=41000)
    fuel_capacity = Column(Float, default=22000)
    created_at = Column(String(30), default=lambda: datetime.utcnow().isoformat())


class FlightSession(Base):
    __tablename__ = "flight_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_name = Column(String(120), nullable=False)
    departure_airport = Column(String(10), nullable=False)
    destination_airport = Column(String(10), nullable=False)
    active = Column(Boolean, default=True)
    started_at = Column(String(30), default=lambda: datetime.utcnow().isoformat())
    user_id = Column(Integer, ForeignKey("users.id"))
    aircraft_id = Column(Integer, ForeignKey("aircraft_profiles.id"))

    user = relationship("User")
    aircraft = relationship("AircraftProfile")


class FlightTelemetry(Base):
    __tablename__ = "flight_telemetry"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("flight_sessions.id"), nullable=False)
    timestamp = Column(String(30), default=lambda: datetime.utcnow().isoformat())
    altitude = Column(Float, default=0.0)
    airspeed = Column(Float, default=0.0)
    ground_speed = Column(Float, default=0.0)
    vertical_speed = Column(Float, default=0.0)
    heading = Column(Float, default=0.0)
    pitch = Column(Float, default=0.0)
    roll = Column(Float, default=0.0)
    fuel = Column(Float, default=100.0)
    outside_temp = Column(Float, default=0.0)
    latitude = Column(Float, default=0.0)
    longitude = Column(Float, default=0.0)
    flight_phase = Column(String(30), default="cruise")


class WeatherRecord(Base):
    __tablename__ = "weather_records"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("flight_sessions.id"), nullable=False)
    condition = Column(String(100), default="Clear")
    wind_speed = Column(Float, default=0.0)
    wind_direction = Column(Float, default=0.0)
    visibility = Column(Float, default=10.0)
    turbulence = Column(String(40), default="Low")
    source = Column(String(80), default="Simulated")
    timestamp = Column(String(30), default=lambda: datetime.utcnow().isoformat())


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("flight_sessions.id"), nullable=False)
    category = Column(String(60), default="monitoring")
    severity = Column(String(20), default="info")
    message = Column(Text, nullable=False)
    explanation = Column(Text, default="")
    recommendation = Column(Text, default="")
    timestamp = Column(String(30), default=lambda: datetime.utcnow().isoformat())


class EmergencyScenario(Base):
    __tablename__ = "emergency_scenarios"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("flight_sessions.id"), nullable=False)
    scenario = Column(String(80), nullable=False)
    status = Column(String(30), default="active")
    warning = Column(Text, default="")
    checklist_reference = Column(Text, default="")
    created_at = Column(String(30), default=lambda: datetime.utcnow().isoformat())


class AssistantConversation(Base):
    __tablename__ = "assistant_conversations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("flight_sessions.id"), nullable=False)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    created_at = Column(String(30), default=lambda: datetime.utcnow().isoformat())


class FlightReport(Base):
    __tablename__ = "flight_reports"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("flight_sessions.id"), nullable=False)
    summary = Column(Text, nullable=False)
    route_status = Column(String(80), default="normal")
    generated_at = Column(String(30), default=lambda: datetime.utcnow().isoformat())
