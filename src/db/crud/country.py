import pandas as pd
from sqlalchemy.orm import Session

from src.db.schemas.country import Country


def get_countries(db: Session):
    return db.query(Country).all()


def get_countries_as_dataframe(db: Session):
    return pd.read_sql(sql=db.query(Country).statement, con=db.bind)
