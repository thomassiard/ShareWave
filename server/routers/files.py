from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, database

router = APIRouter(
    prefix="/files",
    tags=["files"],
)

@router.post("/")
def upload_file(filename: str, content: str, db: Session = Depends(database.get_db)):
    file = models.File(filename=filename, content=content)
    db.add(file)
    db.commit()
    db.refresh(file)
    return file

@router.get("/")
def read_files(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    files = db.query(models.File).offset(skip).limit(limit).all()
    return files

@router.get("/{file_id}")
def read_file(file_id: int, db: Session = Depends(database.get_db)):
    file = db.query(models.File).filter(models.File.id == file_id).first()
    if file is None:
        raise HTTPException(status_code=404, detail="File not found")
    return file
