from fastapi import FastAPI, HTTPException, Depends
from .security import create_access_token

app = FastAPI()

@app.post("/login")
def login(username: str, password: str):
    # Validacija korisnika
    if username == "user" and password == "pass":
        return {"access_token": create_access_token({"sub": username})}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/signup")
def signup(username: str, password: str):
    # Kreiranje korisnika
    return {"message": "User created successfully"}

@app.get("/validate-token")
def validate_token(token: str):
    # Validacija tokena
    return {"message": "Token is valid"}
