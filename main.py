import uvicorn
import os
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from typing import Union
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from permit import Permit
from dotenv import load_dotenv

token_auth_scheme = HTTPBearer()

load_dotenv()

permit = Permit(
    pdp= os.getenv("permit_pdp_url"),
    token= os.getenv("permit_sdk_key")
)

app = FastAPI()

class Task(BaseModel):
    title: str
    checked: Union[bool, None] = False
    owner: Union[str, None] = None

tasks = [
    Task(title="Task 1", checked=False, owner="admin@permit-todo.app"),
    Task(title="Task 2", checked=True, owner="user@permit-todo.app"),
    Task(title="Task 3", checked=False, owner="admin@permit-todo.app"),
]

async def authenticate(token: str = Depends(token_auth_scheme)):
    return token

async def authorize(request: Request, token: str = Depends(token_auth_scheme), body={}):
    resource_name = request.url.path.strip('/').split('/')[0]
    method = request.method.lower()
    resource = await request.json() if method in ["post", "put"] else body
    user = token.credentials

    allowed = await permit.check(user, method, {
        "type": resource_name,
        "attributes": resource
    })

    if not allowed:
        raise HTTPException(status_code=403, detail="Not authorized")

@app.get("/tasks")
async def get_tasks():
    return tasks

@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    return tasks[task_id - 1]

@app.post("/tasks", dependencies=[Depends(authenticate), Depends(authorize)])
async def create_task(task: Task, token: str = Depends(token_auth_scheme)):
    task.owner = token.credentials
    tasks.append(task)
    return task

@app.put("/tasks/{task_id}", dependencies=[Depends(authenticate)])
async def update_task(task_id: int, task: Task):
    if task_id > len(tasks):
        raise HTTPException(status_code=404, detail="Task not found")
    task.owner = tasks[task_id - 1].owner
    tasks[task_id - 1] = task
    return task

@app.delete("/tasks/{task_id}", dependencies=[Depends(authenticate)])
async def delete_task(request: Request, task_id: int, token: str = Depends(token_auth_scheme)):
    task = tasks[task_id - 1]
    await authorize(request=request, token=token, body=task.dict())
    tasks.remove(task)
    return task

if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", reload=True)