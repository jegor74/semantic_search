from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Semantic Search API is running"}
