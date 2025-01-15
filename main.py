from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
# Python 的 ORM 工具
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from typing import List, Optional


# 定義 SQLAlchemy 的 base，所有的ORM 模型都要繼承這個類別
# ORM 將Pyhton 中的類別映射到資料庫的資料表中  (一個類映射一個表)
Base = declarative_base()

# 定義 SQLAlchemy 的 ORM 模型(繼承Base)
class BookORM(Base):
    # 對應的資料表名稱
    __tablename__ = "books"

    # Column 用於定義資料表欄位
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    description = Column(String)


# 建立資料庫引擎
# create_engine()為 SQLAlchemy 框架用於建立資料庫連接的函式
# "sqlite:/" 表示使用 SQLite 作為資料庫
# "/book.db" 為資料庫檔案位置 (如果不存在的話會自動建立)
database_uri = 'sqlite:///books.db'
engine = create_engine(database_uri)

# 根據 ORM 模型建立表
# bind=engine 告訴SQLAlchemy要將資料表(books, l17)創建在哪個資料庫引擎(books.db, l29)中
Base.metadata.create_all(bind=engine)

# 定義資料庫連線依賴，管理每個請求的資料庫連線生命週期
def get_db():
    # Session 是 SQLAlchemy 提供的資料庫會話類
    # bind=engine 這個會話會使用指定的資料庫引擎(engine)與資料庫互動
    db = Session(bind=engine)
    try:
        # yield 將db(資料庫會話)作為生成器的輸出，提供給使用者在請求過程中使用
        yield db
    finally:
        db.close()

        
# 定義 Pydantic 的模型
# 驗證與處理 Python 應用程式的資料，用於處理API請求、回應與資料交換，不會直接和資料庫互動
class Book(BaseModel):
    id: Optional[int] = None
    title: str
    author: str
    description: Optional[str] = None
# Pydantic 中的一個類別，用於配置模型的名行為與設定
# 告訴模型可以從非字典類型的物件(像是ORM或其他有屬性結構的物件)中提取資料來初始化模型
    class Config:
        from_attributes = True

        
# 建立 fastAPI 的實例
app = FastAPI()

# 設置 CORS，前後端運行在不同Port仍需配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:53163"],  # 設置前端的來源
    allow_credentials=True,
    allow_methods=["*"],  # 允許的 HTTP 方法（GET, POST, PUT, DELETE 等）
    allow_headers=["*"],  # 允許的自定義請求頭
)


# 獲取對應書籍
# FastAPI 的路由裝飾器，用於定義一個GET請求的API路由，
# /book/{book_id} 為動態路由，{book_id}為路徑參數，表示要查詢的書籍ID，API會返回一個Book資料模型
@app.get("/books/{book_id}", response_model=Book)
# function 中的參數 book_id 需要和動態參數{}名稱一致
def get_book(book_id: int, db: Session = Depends(get_db)):
    # db.query(BookORM) 針對 BookORM 建立一個"查詢物件"(也就是尚未執行)= SELECT * FRPM book
    # .filter(BookORM.id == book_id)= WHERE id = book_id
    # .first() 為SQLAlchemy的方法，執行查詢並返回結果中第一筆資料
    book = db.query(BookORM).filter(BookORM.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book
    

# 顯示所有書籍
@app.get("/books", response_model=List[Book])
def get_books(db: Session = Depends(get_db)):
    books = db.query(BookORM).all()
    return books

# 新增書籍
@app.post("/books", response_model=Book)
def create_book(book: Book, db: Session = Depends(get_db)):
    db_book = BookORM(title=book.title, author=book.author, description=book.description)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

# 刪除對應書籍
@app.delete("/books/{book_id}")
def delete_book( book_id: int, db: Session = Depends(get_db)):
    # db.query(BookORM).filter(BookORM.id == book_id) 返回值為SQLAlchemy的查詢物件，
    # 而db.delete接收的對象為ORM模型的實例，因此要刪除的話要用.all()或.first()取得具體的ORM實例  
    book = db.query(BookORM).filter(BookORM.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book) #刪除目標
    db.commit() #提交刪除操作置資料庫

# 修改對應書籍
@app.put("/books/{book_id}")
def update_book(book: Book, book_id: int, db: Session = Depends(get_db)):
    book_upd = db.query(BookORM).filter(BookORM.id == book_id).first()
    if not book_upd:
        raise HTTPException(status_code=404, detail="Book not found")
    # book.model_dump()將傳入的book(Pydantic 模型物件)轉換為字典
    # exclude_unset=True 會排除None的值
    # .item() 將字典轉換成迭代器
    for key, value in book.model_dump(exclude_unset=True).items():
        if value is not None and value !="":
            setattr(book_upd, key, value)

    db.commit()
    db.refresh(book_upd)
    
app.mount("/static", StaticFiles(directory="static"), name="static")
