from datetime import datetime
import uvicorn
from fastapi import FastAPI
from app.api.routes.auth import router as auth_router
from app.api.routes.chat import router as chat_router


app=FastAPI()
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(chat_router, prefix="/api/v1/chat", tags=["chat"])
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
