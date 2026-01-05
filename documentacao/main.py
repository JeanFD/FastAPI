from typing import Annotated

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.post("/file/")
async def create_files(file: Annotated[bytes | None, File(description="A file read as bytes")] = None):
    if not file:
        return {"message": "No file sent"}
    else:
        return {"file_size": len(file)}

@app.post("/uploadfile")
async def create_upload_file(file: Annotated[UploadFile | None, File(description="A file read as UploadFile")] = None):
    if not file:
        return {"message": "No upload file sent"}
    else:
        return {"filename": file.filename}
    
@app.post("files")
async def create_files(files: Annotated[list[bytes], File(description= "Multiple files as bytes")]):
    return {"file_sizes": [len(file) for file in files]}

@app.post("/uploadfiles/")
async def create_upload_files(files: Annotated[list[UploadFile], File(description = "Multiple files as UploadFile")]):
    return {"filenames": [file.filename for file in files]}


@app.get("/")
async def main():
    content = """
        <body>
        <form action="/files/" enctype="multipart/form-data" method="post">
        <input name="files" type="file" multiple>
        <input type="submit">
        </form>
        <form action="/uploadfiles/" enctype="multipart/form-data" method="post">
        <input name="files" type="file" multiple>
        <input type="submit">
        </form>
        </body>
    """
    return HTMLResponse(content=content)