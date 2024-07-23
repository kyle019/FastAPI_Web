# Web server with FastAPI

[https://github.com/kyle019/FastAPI_Web](https://github.com/kyle019/FastAPI_Web)

## What is FastAPI?

FastAPI is a modern, fast (high-performance), web framework for building APIs with Python based on standard Python type hints.

Fastapi is fast because using ASGI which offered by Starlette.

ASGI(Asynchronous Server Gateway Interface) is Interface which is working between python web server with web framework for asynchronous web application.

FastAPI with ASGI make fast and efficient development in web application.

## Installation and Testing FastAPI

```jsx
pip install fastapi
pip install "uvicorn[standard]"
```

Using pip to install fastapi and uvicorn

Uvicorn is the web server which following ASGI

### Simple example of FastAPI

<main.py>

```jsx
from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
```

Using Pydantic to define ‘Item’ data model.

Pydantic is FastAPI library which deals data validation and parsing, for this we can develop server fast and efficient.

```jsx
@app.get("/")
async def read_root():
    return "This is root"

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str,  None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/items/")
async def create_item(item: Item):
    return item

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    result = {"item_id": item_id, **item.dict()}

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    return {"deleted": item_id}
```

This is simple API which address HTTP method(GET, POST, PUT, DEETE)

we can define function about URL by using DECORATOR method like @app.get(”/”)

## RUN

```jsx
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Test

FastAPI offer Swagger UI to address API easier. So link in ‘http://localhost:8000/docs’

![Untitled](Web%20server%20with%20FastAPI%2004ec5dcd673345efbe01eb534cfa1096/Untitled.png)

we can easily test web server by this UI.

## **FastAPI CRUD**

Then, let’s make real server by connecting with real database and develop CRUD to store data in DB and fix and delete.

```jsx
pip install sqlalchemy pymysql
```

sqlalchemy is library to using ORM, and pymysql is the MySQL Database.

Let’s make project like blow construction.

![Untitled](Web%20server%20with%20FastAPI%2004ec5dcd673345efbe01eb534cfa1096/Untitled%201.png)

Follow this link to install Mysql in your server.

https://jongsky.tistory.com/79

create your database and use.

```jsx
mysql> create database myweb;
mysql> use myweb;
```

Then, we make [models.py](http://models.py) to make Table by ORM(Object-Relational Mapping).

app/models.py

```jsx
from sqlalchemy import Column, Integer, String
from app.database import Base

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30))
    description = Column(String(30))
    price = Column(Integer)
```

Using sqlalchemy to define the database model.

app/database.py

```jsx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "mysql+pymysql://root:1234@localhost:3306/myweb?charset=utf8"
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully")
```

This code relates with connecting and creating/management of database 

‘SessionLocal’ is the class for connecting to database. Using such as create_engin, sessionmaker is the made rules to using sqlalchemy database.

autocommit=False is data is stored in database when only ‘commit’ sign is given, if you are not doing this you can’t rollback the work.

create engine is creating connection pool. The connection pool is used to control the number of sessions connecting to the database and to reduce the time it takes to connect to sessions.

The Base class returned by the last declarative_base function is the class used to construct the Debe model.

app/schema.py

```jsx
from pydantic import BaseModel

class ItemBase(BaseModel):
    name: str
    description: str
    price: int

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int

    class Config:
        orm_mode = True
```

Pydantic is also FastAPI library which is related with data. it can check availability of data and I'm in charge of requesting/response data conversion.

you can get a question why we already define the database model in ‘app/models.py’ but define again.

This is because, when we show the DB’s result, it can contain the unusable information. Specifically, ‘id’ value is not needed when we ‘INSERT’ but it need in another work.

Using Pydantic model, it can choose only required data, and don’t use the unusable data.

app/crud.py

```jsx
from sqlalchemy.orm import Session
from app.models import Item
from app.schema import ItemCreate

def get_items(db: Session):
    return db.query(Item).all()

def get_item(db: Session, item_id: int):
    return db.query(Item).filter(Item.id == item_id).first()

def create_item(db: Session, item: ItemCreate):
    db_item = Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_item(db: Session, item: Item, updated_item: ItemCreate):
    for key, value in updated_item.dict().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item

def delete_item(db: Session, item: Item):
    db.delete(item)
    db.commit()
```

Address data to database we use CRUD function. It id defined as create, find, update, delete the item in database. app/main.py call these managing functions to use the real data.

app/main.py

 

```jsx
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
    return RedirectResponse(url="/items/")

@app.get("/items/")
async def get_items(db: Session = Depends(get_db)):
    items = crud.get_items(db)
    return items

@app.get("/items/{item_id}")
async def get_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.get_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.post("/items/")
async def create_item(item: schema.ItemCreate, db: Session = Depends(get_db)):
    db_item = crud.create_item(db, item)
    return db_item

@app.put("/items/{item_id}")
async def update_item(item_id: int, updated_item: schema.ItemCreate, db: Session = Depends(get_db)):
    db_item = crud.get_item(db, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    updated_item = crud.update_item(db, db_item, updated_item)
    return updated_item

@app.delete("/items/{item_id}")
async def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = crud.get_item(db, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    crud.delete_item(db, db_item)
    return {"message": "Item deleted successfully"}
```

When application is starting, it create the database table. and this code manipulate the all python file, we created.

## Test

By using curl to create and find the data

POST

```jsx
curl -X 'POST' \
  'http://localhost:8000/items/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "mouse",
  "description": "slim mouse",
  "price": 13.9
}'
```

Result

```jsx
{“description”:”slim mouse”,”id”:1,”name”:”mouse”,”price”:13.9}
```

GET

```jsx
curl -X 'GET' \
  'http://localhost:8000/items/' \
  -H 'accept: application/json'
```

REsult

```jsx
{“description”:”초경량 게이밍 마우스”,”id”:1,”name”:”마우스”,”price”:139000}
```

## Conclusion

This project shows basic concept and features of FastAPI, and show the simple REST API through developing CRUD example.

## Connection with MySQL database.

### mysql installation and initial setting (ubuntu)

1. Installation of MySQL
    
    ```jsx
    sudo apt update
    sudo apt install mysql-server
    ```
    
2.  Setting account for root access
    
    ```jsx
    # connect mysql
    sudo mysql -u root
    
    # create root account and password.
    mysql> ALTER USER 'root'@'localhost' IDENTIFIED BY '비밀번호';
    
    # push password 
    mysql> FLUSH PRIVILEGES;
    
    #change the access authetication about root account
    mysql> UPDATE user SET host='%' WHERE user='root' and host='localhost';
    
    #exit mysql and restart
    mysql>exit
    sudo mysql -u root
    
    # create database
    mysql> CREATE Databse <newuser>
    
    # allow external access
    sudo vi /etc/mysql/mysql.conf.d/mysqld.cnf
    #modify address part
    ...
    # bind-address            = 127.0.0.1 
    bind-address            = 0.0.0.0
    ...
    ```
    
3. simple command to use mysql
    
    ```jsx
    # show all database
    mysql> show databases;
    #create database
    mysql> CREATE DATABASE <newdb>;
    #change database
    mysql> use <newdb>;
    
    #show all table indb
    mysql> SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = <'newdb'>;
    #show specific table's columns
    mysql> SHOW FULL COLUMNS FROM <table>;
    
    #show all datas in table
    mysql> select * from <table>;
    ```
    
4. connect in FastAPI

FastAPI offer us ORM(object relational mapping) which can make us not using DB query. It make frequently used query in object so we don't need to manage database not using SQLlanguage.

SQLAlchemy : most famous ORM python library

<database.py>

```jsx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL ="mysql+pymysql://test:12345678@192.168.1.15:3306/newuser1?charset=utf8"
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully")
```
