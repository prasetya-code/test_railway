# from sqlalchemy import inspect
# from sqlalchemy.exc import (
#     ProgrammingError,
#     OperationalError,
#     SQLAlchemyError,
# )

# from .sqlalchemy_engine import fl_db
# from .sqlalchemy_config import USE_AUTO_CREATE_TABLES


# def get_existing_tables(app):
#     with app.app_context():
#         inspector = inspect(fl_db.engine)
#         return set(inspector.get_table_names(schema="public"))


# def create_tables(app):
#     if not USE_AUTO_CREATE_TABLES:
#         print("AUTO CREATE TABLE disabled")
#         return

#     try:
#         before = get_existing_tables(app)

#         with app.app_context():
#             fl_db.create_all()

#         after = get_existing_tables(app)

#         print("Created:", after - before)

#     except (ProgrammingError, OperationalError, SQLAlchemyError):
#         import traceback

#         print(traceback.format_exc())

#         raise
