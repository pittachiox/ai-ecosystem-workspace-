def get_db():
    db = "fake_db_session"
    try:
        yield db
    finally:
        pass
