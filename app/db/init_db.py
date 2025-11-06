from sqlalchemy.orm import Session

from app.models.base import Base
from app.db.session import engine
import app.models.user
import app.models.property
import app.models.inquiry
import app.models.call_session
import app.models.property_search
import app.models.property_favorite


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    

if __name__ == "__main__":
    init_db()
