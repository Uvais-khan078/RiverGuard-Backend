import os
from sqlalchemy import create_engine, Column, Integer, String, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Read the database URL from environment variable or use default for local development
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://myuser:mypassword@localhost:5432/riverguard")

engine = create_engine(DATABASE_URL, connect_args={}, execution_options={"schema_translate_map": {"public": "myuser_schema"}})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class ExcelData(Base):
    __tablename__ = "excel_data"
    __table_args__ = {'schema': 'myuser_schema'}

    id = Column(Integer, primary_key=True, index=True)
    state_name = Column(String, nullable=True)
    district_name = Column(String, nullable=True)
    factory_name = Column(String, nullable=True)
    bod = Column(String, nullable=True)
    cod = Column(String, nullable=True)
    ph = Column(String, nullable=True)
    nitrate = Column(String, nullable=True)
    do = Column(String, nullable=True)
    tds = Column(String, nullable=True)
    zone = Column(String, nullable=True)

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'schema': 'myuser_schema'}

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    clearance = Column(Integer, nullable=False)
    # Add other user fields as needed

class Factory(Base):
    __tablename__ = "factories"
    __table_args__ = {'schema': 'myuser_schema'}

    id = Column(Integer, primary_key=True, index=True)
    factory_name = Column(String, nullable=False)
    license_number = Column(String, nullable=False)
    waste_type = Column(String, nullable=False)
    discharge_method = Column(String, nullable=False)
    location_coordinates = Column(String, nullable=False)
    registered_by = Column(String, nullable=False)
    license_document = Column(String, nullable=True)  # Could store file path or URL

class ChartData(Base):
    __tablename__ = "chart_data"
    __table_args__ = {'schema': 'myuser_schema'}

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, nullable=False)  # e.g., factory name or year
    bad = Column(Float, nullable=False)
    moderate = Column(Float, nullable=False)
    good = Column(Float, nullable=False)

    
def init_db():
    Base.metadata.create_all(bind=engine)
