import random
from fastapi import FastAPI, Query
from typing import Annotated
from pydantic import AfterValidator
app = FastAPI()

# @app.get("/items/")
# async def read_items(q: Annotated[str | None, Query(min_length = 3, max_length=50, pattern="^fixedquery$")] = None):
#     results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
#     if q:
#         results.update({"q": q})
#     return results

data = {
    "isbn-9781529046137": "The Hitchhiker's Guide to the Galaxy",
    "imdb-tt0371724": "The Hitchhiker's Guide to the Galaxy",
    "isbn-9781439512982": "Isaac Asimov: The Complete Stories, Vol. 2",
}

def check_valid_id(id: str):
    if not id.startswith(("isbn-", "imdb-")):
        raise ValueError("Invalid ID format, it must start with 'isbn-' or 'imdb-'")
    return id

#  multiplos valores
@app.get("/items/")
async def read_items(
    id: Annotated[
        str | None,
        AfterValidator(check_valid_id),
        Query(
            include_in_schema=False,
            alias="item-query",
            title="test3e",
            description="Query string for the items to search in the database that have a good match", 
            min_length=3,
            max_length=50,
            pattern="^fixedquery$",
            deprecated=True
        ),
    ] = None,
):
    if id:
        item = data.get(id)
    else:
        id, item = random.choice(list(data.items()))
    return {"id": id, "item": item}