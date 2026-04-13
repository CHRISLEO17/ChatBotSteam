from fastapi import FastAPI
from pydantic import BaseModel
import os
from openai import OpenAI

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    user_msg = req.message
    # Aquí llamas a tu lógica del chatbot
    respuesta = f"Procesando: {user_msg}"  # reemplaza con tu función procesar_mensaje
    return {"respuesta": respuesta}
