from pydantic import BaseModel, ConfigDict

class MoviePatch(BaseModel):
    title:str | None = None
    description:str | None = None

class MovieBase(BaseModel):
    title:str
    description:str

class MovieCreate(MovieBase):
    pass

class Movie(MovieBase):
    id:int
    model_config = ConfigDict(from_attributes=True)