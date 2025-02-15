from fastapi import FastAPI, HTTPException, Query
from tasks import execute_task, read_file_content

app = FastAPI()

@app.post("/run")
async def run_task(task: str = Query(..., description="Task description in plain English")):
    try:
        result = execute_task(task)
        return {"status": "success", "detail": result}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/read")
async def read_file(path: str = Query(..., description="Path of the file to read")):
    content = read_file_content(path)
    if content is None:
        raise HTTPException(status_code=404, detail="File not found")
    return content
