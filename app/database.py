from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "mysql+pymysql://root:12345678@localhost/newuser1?charset=utf8"
engine = create_engine(DATABASE_URL)

#SessionLocal은 데이터베이스에 접속하기 위해 필요한 클래스이다. create_engin sessionmaker 등을 사용하는것은 sqlalchemy데베를 사용하기 위한 귀칙이다. 
#여기서 autocommit=False는 데이터를 변경했을때 commit이라는 사인을 주어야만 저장이된다. 이거 안하면 rollback이 안된다.
#create engine은 커넥션 풀을 생성한다. 컨넥션 풀이란 데이터베이스에 접속하는 객체를 일정 갯수만큼 만들어 놓고 돌려가며 사용하는것을 의미한다.
#(컨넥션풀은 데이터 베이스에 접속하는 세션수를 제어하고, 또 세션 접속에 소요되는 시간을 줄이고자 하는 용도로 사용된다.)
#마지막 declarative_base함수에 의해 반환된 Base 클래스는 데베 모델을 구성할때 사용되는 클래스이다.

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully")