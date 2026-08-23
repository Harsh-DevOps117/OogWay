from datetime import datetime
import uvicorn
from fastapi import FastAPI


app=FastAPI()
@app.get("/")
def read_root():
    return {
            "status":"ok",
            "message":"Starting Building the API for the OogWay",
            "version":"0.0.1"
            }

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "OogWay",
        "version": "0.0.1",
        "time": datetime.now()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
