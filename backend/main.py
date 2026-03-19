from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from routes import admin, adviser, student, auth as auth_router

app = FastAPI(title="UniVote API")

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": str(exc.detail), "detail": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"message": "Validation Error", "detail": exc.errors()},
    )

@app.exception_handler(Exception)
async def universal_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "An internal server error occurred.", "detail": str(exc)},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Public: no auth required
app.include_router(auth_router.router, prefix="/api/auth", tags=["auth"])

# Student voting: validated by student_id only (no account required)
app.include_router(student.router, prefix="/api/student", tags=["student"])

# Protected: admin and adviser routes require a valid Supabase JWT
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(adviser.router, prefix="/api/adviser", tags=["adviser"])


@app.get("/")
def read_root():
    return {"message": "Welcome to UniVote API"}
