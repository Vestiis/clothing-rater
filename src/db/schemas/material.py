from sqlalchemy import Column, Float, String

from src.db.database import Base


class Material(Base):
    __tablename__ = "material"

    name = Column(String(), primary_key=True)
    description = Column(String())
    is_recyclable = Column(Float())
    has_plant_based_fibers = Column(String())
    has_animal_based_fibers = Column(String())
    is_synthetic = Column(String())
    is_semi_synthetic = Column(String())
    is_artificial = Column(String())
    health_harmfulness = Column(Float())
    skin_friendlyness = Column(Float())
