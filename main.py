from fastapi import FastAPI
from routers import movies
import models
from database import engine

# This line instructs SQLAlchemy to create all tables defined in models.py
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Plug the "extension cord" into the main app!
app.include_router(movies.router)

@app.get("/")
def home_page():
    return {"Hello": "Welcome to the Movie API!"}