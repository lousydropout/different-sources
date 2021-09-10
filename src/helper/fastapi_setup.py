from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SQL injection check
def raise_exception_if_unsafe(name: str) -> None:
    """Raise exception if name contains quotes. Else, do nothing."""
    if "'" in name or '"' in name:
        detail = "The input name must not contain quotes."
        raise HTTPException(status_code=403, detail=detail)
