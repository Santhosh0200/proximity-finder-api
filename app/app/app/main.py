from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from pydantic import BaseModel

from . import models
from .database import engine, get_db

# This line creates the database tables if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Proximity Finder API",
    description="An API to find nearby points of interest.",
    version="1.0.0"
)

# --- Pydantic Models for Data Validation ---

class LocationBase(BaseModel):
    name: str
    category: str
    latitude: float
    longitude: float

class LocationCreate(LocationBase):
    pass

class LocationResponse(LocationBase):
    id: int
    distance_km: float | None = None

    class Config:
        from_attributes = True

# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Welcome to the Proximity Finder API"}

@app.post("/locations/", response_model=LocationResponse, status_code=201)
def create_location(location: LocationCreate, db: Session = Depends(get_db)):
    """
    Create a new location in the database.
    """
    db_location = models.Location(**location.model_dump())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

@app.get("/nearby/", response_model=List[LocationResponse])
def find_nearby_locations(
    lat: float = Query(..., description="User's latitude"),
    lon: float = Query(..., description="User's longitude"),
    radius_km: float = Query(5.0, description="Search radius in kilometers"),
    db: Session = Depends(get_db)
):
    """
    Find locations within a specified radius from the user's coordinates.
    """
    haversine_query = text("""
        SELECT id, name, category, latitude, longitude,
        ( 6371 * acos( cos( radians(:lat) ) * cos( radians( latitude ) ) * cos( radians( longitude ) - radians(:lon) ) + sin( radians(:lat) ) * sin( radians( latitude ) ) ) ) AS distance
        FROM locations
        HAVING distance < :radius_km
        ORDER BY distance;
    """)
    
    results = db.execute(haversine_query, {"lat": lat, "lon": lon, "radius_km": radius_km}).fetchall()

    if not results:
        return []

    nearby_locations = []
    for row in results:
        location_data = {
            "id": row[0],
            "name": row[1],
            "category": row[2],
            "latitude": float(row[3]),
            "longitude": float(row[4]),
            "distance_km": round(row[5], 2)
        }
        nearby_locations.append(LocationResponse(**location_data))
        
    return nearby_locations
