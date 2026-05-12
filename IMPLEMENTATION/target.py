from fastapi import FastAPI

app = FastAPI()

@app.post("/target")
def target():
    print("TARGET HIT")
    return {"status": "EXECUTED"}
