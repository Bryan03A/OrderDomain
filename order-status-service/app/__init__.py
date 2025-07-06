from .database import Base, get_engine
Base.metadata.create_all(bind=get_engine())