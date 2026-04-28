from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

class Movie(BaseModel):
    id:int | None=None
    title:str
    description:str
    # poster_image_url:str | None = None
    # reviews: list[Review] = Field(default_factory=list)

class BulkMovies(BaseModel):
    message: str
    count: int

class MoviePatch(BaseModel):
    title:str | None = None
    description:str | None = None
    # poster_image_url:str | None = None
    # reviews: list[Review] = Field(default_factory=list)

router = APIRouter(prefix="/movies", tags=["Movies"])
movie_db = {}
id_counter = 0

@router.get("/", response_model=list[Movie])
def get_movies( movie_ids: list[int] | None = Query(default=None, max_length=50),
                skip:int=Query(default=0, ge=0),
                limit:int=Query(default=10, le=50)
                ):
    # 1. Did the user ask for specific IDs?
    if movie_ids is not None:
        # Loop through the requested IDs, check if they exist in the DB, and grab them
        filtered_movies = [movie_db[m_id] for m_id in movie_ids if m_id in movie_db]
        return filtered_movies
    # 2. If no specific IDs were requested, just return the paginated list
    return list(movie_db.values())[skip : skip+limit]

@router.get("/{movie_id}", response_model=Movie)
def get_movie(movie_id:int):
    if movie_id not in movie_db:
        raise HTTPException(status_code=404, detail=f"No movie with id {movie_id} found!")
    return movie_db[movie_id]
        
@router.post("/", response_model=Movie)
def post_movie(movie:Movie):
    # Increment global id_counter
    global id_counter
    id_counter += 1
    # Find ID yourself
    movie_id = id_counter
    movie_dict = movie.model_dump()
    movie_dict["id"] = movie_id
    movie_db[movie_id] = movie_dict
    return movie_db[movie_id]

@router.post("/bulk", response_model=BulkMovies)
def post_movies(movie_list:list[Movie]):
    # Tell python to look for id_counter outside the function
    global id_counter
    saved_movies = []
    for movie in movie_list:
        # Convert movie from BaseModel to dict
        movie_dict = movie.model_dump()
        # Increment global id_counter
        id_counter += 1
        # Update the id key inside movie
        movie_dict["id"] = id_counter
        movie_db[id_counter] = movie_dict
        # append new movie to saved_movies
        saved_movies.append(movie_db[id_counter])

    return {"message": "New movies successfully added!", "count": len(saved_movies)}

@router.delete("/")
def delete_movie(movie_ids: list[int] = Query(..., max_length=50)):
    deleted_count = 0
    for movie_id in movie_ids:
        if movie_id in movie_db:
            # raise HTTPException(status_code=404, detail=f"No movie with id {movie_id} found!")
            movie_db.pop(movie_id)
            deleted_count += 1
    return {"message": "Bulk delete complete", "deleted_count": deleted_count}

@router.put("/{movie_id}", response_model=Movie)
def put_movie(movie_id:int, movie:Movie):
    if movie_id not in movie_db:
        raise HTTPException(status_code=404, detail=f"No movie with id {movie_id} found!")
    movie_dict = movie.model_dump()
    # Re-inject the ID because it will be lost at this line
    movie_dict["id"] = movie_id
    movie_db[movie_id] = movie_dict
    return movie_db[movie_id]

@router.patch("/{movie_id}", response_model=Movie)
def patch_movie(movie_id:int, movie:MoviePatch):
    if movie_id not in movie_db:
        raise HTTPException(status_code=404, detail=f"No movie with id {movie_id} found!")
    # 2. Extract ONLY the data the user actually sent
    update_data = movie.model_dump(exclude_unset=True)
    # 3. Merge the new data into the existing database dictionary
    movie_db[movie_id].update(update_data)
    return movie_db[movie_id]
