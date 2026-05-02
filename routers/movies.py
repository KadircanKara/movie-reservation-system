from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy import insert
from sqlalchemy.orm import Session
from database import get_db
import models, schemas

router = APIRouter(prefix="/movies", tags=["Movies"])

@router.get("/", response_model=list[schemas.Movie])
def get_movies( movie_ids: list[int] | None = Query(default=None, max_length=50),
                skip:int=Query(default=0, ge=0),
                limit:int=Query(default=10, le=50),
                db: Session = Depends(get_db)
                ):
    if movie_ids is not None:
        filtered_movies = db.query(models.Movie).filter(models.Movie.id.in_(movie_ids)).all()
        return filtered_movies
    return db.query(models.Movie).offset(skip).limit(limit).all()

@router.get("/{movie_id}", response_model=schemas.Movie)
def get_movie(movie_id:int, db: Session = Depends(get_db)):
    db_movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not db_movie:
        raise HTTPException(status_code=404, detail=f"No movie with id {movie_id} found!")
    return db_movie
        
@router.post("/", response_model=schemas.Movie)
def post_movie(movie:schemas.MovieCreate, db: Session = Depends(get_db)):
    db_movie = models.Movie(title=movie.title, description=movie.description)
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie 


@router.post("/bulk", response_model=list[schemas.Movie])
def post_movies(movie_list:list[schemas.MovieCreate], db: Session = Depends(get_db)):
    # Convert the list of Pydantic models into a list of dictionaries
    movie_dicts = [movie.model_dump() for movie in movie_list]
    # Construct the SQL insert statement with the RETURNING clause
    stmt = insert(models.Movie).returning(models.Movie)
    # Execute the statement in a single database call
    db_movies = db.scalars(stmt, movie_dicts).all()
    db.commit()
    return db_movies

@router.delete("/")
def delete_movie(movie_ids: list[int] = Query(..., max_length=50), db: Session = Depends(get_db)):
    deleted_count = db.query(models.Movie).filter(models.Movie.id.in_(movie_ids)).delete(synchronize_session=False)
    db.commit()
    return {"message": "Bulk delete executed", "deleted_count": deleted_count}

@router.put("/{movie_id}", response_model=schemas.Movie)
def put_movie(movie_id:int, movie:schemas.MovieCreate, db: Session = Depends(get_db)):
    db_movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not db_movie:
        raise HTTPException(status_code=404, detail=f"No movie with id {movie_id} found!")
    db_movie.title = movie.title
    db_movie.description = movie.description
    db.commit()
    return db_movie

@router.patch("/{movie_id}", response_model=schemas.Movie)
def patch_movie(movie_id:int, movie:schemas.MoviePatch, db: Session = Depends(get_db)):
    db_movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not db_movie:
        raise HTTPException(status_code=404, detail=f"No movie with id {movie_id} found!")
    update_data = movie.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_movie, key, value)
    db.commit()
    return db_movie
