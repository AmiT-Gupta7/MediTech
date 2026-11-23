from fastapi import FastAPI

from routes.auth import router as auth_router
from routes.patients import router as patients_router
from routes.users import router as users_router
from routes.doctors import router as doctors_router
from routes.appointments import router as appointments_router


app = FastAPI(
    title="MediTech API",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(patients_router)
app.include_router(doctors_router)
app.include_router(appointments_router)


@app.get("/")
def home():
    return {
        "message": "MediTech API is running"
    }