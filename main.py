from fastapi import FastAPI# , HTTPException, APIRouter, Query
# from pydantic import BaseModel, Field
# from mangum import Mangum
from routers import movies

app = FastAPI()

# Plug the "extension cord" into the main app!
app.include_router(movies.router)

# handler = Mangum(app)

# class Review(BaseModel):
#     comment:str
#     rating:float

# class Theater(BaseModel):
#     city:str
#     district:str
#     movies:list[Movie]


@app.get("/")
def home_page():
    return {"Hello": "Welcome to the Movie API!"}