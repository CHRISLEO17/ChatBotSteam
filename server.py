from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Chatbot Steam está en línea ✅"}

@app.post("/chat")
def chat_endpoint(message: dict):
    user_input = message.get("text", "")
    # Aquí puedes conectar tu lógica del chatbot
    respuesta = f"Recibí tu mensaje: {user_input}"
    return {"reply": respuesta}
