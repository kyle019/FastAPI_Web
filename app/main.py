from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from app import crud, database, models, schema

app = FastAPI()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    database.create_tables()

@app.get("/")
async def root():
    return RedirectResponse(url="/users/")

@app.get("/allUsers/")
async def get_users(db: Session = Depends(get_db)):
    users = crud.get_users(db)
    return users

@app.get("/findUsers/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/createUsers/")
async def create_user(user: schema.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.create_user(db, user)
    return db_user

@app.put("/users/{user_id}")
async def update_user(user_id: int, updated_user: schema.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = crud.update_user(db, db_user, updated_user)
    return updated_user

@app.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    crud.delete_item(db, db_user)
    return {"message": "User deleted successfully"}