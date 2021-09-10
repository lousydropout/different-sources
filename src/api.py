import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from mangum import Mangum


app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# /data
class Data(BaseModel):
    name: str


@app.get("/data")
def list_data():
    return {"data": []}


def handler(event: dict, context):
    print(f"Event: {json.dumps(event, default=str)}")

    api_handler = Mangum(app)
    return api_handler(event, context)
