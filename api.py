from fastapi import FastAPI, HTTPException


app = FastAPI()


@app.get("/")
def root():
    return {"status": "ok"}

