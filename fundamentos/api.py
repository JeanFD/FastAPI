from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

jogadores = {
    1: {
        "nome": "Rony",
        "idade": 22,
        "time": "Jogador"
    },
    2: {
        "nome": "Gustavo Gomex",
        "idade": 29,
        "time": "Palmeiras"
    }
}

class Jogador(BaseModel):
    nome: str
    idade: int
    time: str

class AtualizaJogador(BaseModel):
    nome: Optional[str] = None
    idade: Optional[int] = None
    time: Optional[str] = None

@app.get("/")
def inicio():
    return jogadores

@app.get("/get-jogador/{id_jogador}")
def get_jogador(id_jogador: int):
    return jogadores[id_jogador]

#get-jogador/1 - Path Parameter

#get-jogador/?id=1 - Query Parameter
#get-jogador-time?time="Palmeiras"
@app.get("/get-jogador-time/")
def get_jogador_time(time: str):
    for jogador_id in jogadores:
        if jogadores[jogador_id]["time"] == time:
            return jogadores[jogador_id]
    return {"mensagem": "Nenhum jogador encontrado para esse time."}

@app.post("/cadastra-jogador/{jogador_id}")
def cadastra_jogador(jogador_id: int, jogador: Jogador):
    if jogador_id in jogadores:
        return {"Erro": "Jogador já cadastrado."}
    jogadores[jogador_id] = jogador
    return jogadores[jogador_id]

@app.delete("/deleta-jogador/{jogador_id}")
def exclui_jogador(jogador_id: int):
    if jogador_id not in jogadores:
        return {"Erro": "Jogador não encontrado."}
    del jogadores[jogador_id]
    return {"Mensagem": "Jogador excluído com sucesso."}

@app.put("/atualiza-jogador/{jogador_id}")
def atualiza_jogador(jogador_id: int, jogador: AtualizaJogador):
    if jogador_id not in jogadores:
        return {"Erro": "Jogador não encontrado."}
    
    if jogador.nome is not None:
        jogadores[jogador_id]["nome"] = jogador.nome
    if jogador.idade is not None:
        jogadores[jogador_id]["idade"] = jogador.idade
    if jogador.time is not None:
        jogadores[jogador_id]["time"] = jogador.time
    
    return jogadores[jogador_id]