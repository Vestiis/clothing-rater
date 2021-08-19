import pandas as pd
from sqlalchemy.orm import Session

from src.db.schemas.material import Material


def get_materials(db: Session):
    return db.query(Material).all()


def get_materials_as_dataframe(db: Session):
    return pd.read_sql(sql=db.query(Material).statement, con=db.bind)
