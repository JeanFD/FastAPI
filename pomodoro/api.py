from fastapi import FastAPI, HTTPException, Path, Query, Body, status, File, UploadFile, Form
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

app = FastAPI()

db_sessions = []

class PomodoroSession(BaseModel):
    id: Optional[UUID] = None
    task_name: str = Field(..., min_length=3, max_length=50, description="O que você vai fazer?")
    work_minutes: int = Field(25, ge=1, le=60, description="Duração do foco em minutos")
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    completed: bool = False

@app.post("/sessions/", status_code=status.HTTP_201_CREATED)
def create_session(session: PomodoroSession):
    session.id = uuid4() # gera um ID único
    db_sessions.append(session)
    return session

@app.get("/sessions/")
def read_sessions(
    completed: bool = Query(None, description="Filtrar por status de conclusão"),
    limit: int = Query(10, gt=0, le=50)
):
    if completed is not None:
        filtered_sessions = [s for s in db_sessions if s.completed == completed]
        return filtered_sessions[:limit]
    
    return db_sessions[:limit]
    
@app.post("/sessions/{session_id}/start")
def start_timer(session_id: UUID = Path(..., title="ID da sessão")):
    session = next((s for s in db_sessions if s.id == session_id), None)

    if not session:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Sessão não encontrada")
    
    if session.start_time:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="O timer já foi iniciado!")
    
    session.start_time = datetime.now()

    session.end_time = session.start_time + timedelta(minutes=session.work_minutes)

    return {"message": "Foco iniciado!", "end_time": session.end_time}

@app.post("/sessions/upload-evidence")
def upload_evidence(
     notes: str = Form(...),
     file: UploadFile = File(...)
):
     return{
          "notes_received": notes,
          "filename": file.filename,
          "content_type": file.content_type,
          "size_in_memory": "Spooling..."
     }
