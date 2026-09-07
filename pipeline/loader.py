from db.session import SessionLocal
from db.queries import upsert_fare_quotes


def load(df):
    records = df.to_dicts()

    session = SessionLocal()

    try:
        return upsert_fare_quotes(session, records)
    finally:
        session.close()