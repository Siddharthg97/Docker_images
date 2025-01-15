Dockerizing python application - https://www.youtube.com/watch?v=0UG2x2iWerk

### Creating webapp  using Fast API
https://fastapi.tiangolo.com/#requirements

1) Create your environment and actiavte it
2) now install fastapi and uvicorn using pip command
   pip install "fastapi[standard]"
   pip install uvicorn
3) create your main.py

   main.py ----------------------------------------
   from typing import Union

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
    
------------------------------------------------

