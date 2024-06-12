from sqlalchemy.orm import Session
from app.models import User
from app.schema import UserCreate
from app.schema import UserPost


def get_users(db: Session):
    return db.query(User).all()

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user: UserCreate):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def post_user(db: Session, user_id:int, user: UserPost):
    db_user = User(id =user_id, name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user: User, updated_user: UserCreate):
    for key, value in updated_user.dict().items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user: User):
    db.delete(User)
    db.commit()

    
def get_users_by_ids(db: Session, user_ids: list[int]):
    return db.query(User).filter(User.id.in_(user_ids)).all()