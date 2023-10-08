from enum import Enum

from fastapi import FastAPI
from pydantic import BaseModel


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


app = FastAPI()


@app.get("/")
async def root() -> dict:
    return {"messsage": "Hello World"}


# Must have Union of None for optional query params
@app.get("/item/{item_id}")
async def read_item(item_id: int, q: str | None = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update({"description": "My long description here"})
    return item


@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: int, q: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update({"description": "My long description here"})
    return item


@app.get("/users")
async def read_users(skip: int = 0, limit: int = 10):
    list_of_users = [
        "morty",
        "rick",
        "foo",
        "bar",
        "baz",
        "qux",
        "quux",
        "corge",
        "grault",
        "garply",
        "waldo",
        "fred",
        "plugh",
        "xyzzy",
        "thud",
    ]
    return list_of_users[skip : skip + limit]


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


@app.get("/files/{file_path:path}")
async def read_file(file_path: str, required_param: str):
    return {"file_path": file_path, "test": required_param}


@app.post("/items/")
async def create_item(item: Item):
    return item
