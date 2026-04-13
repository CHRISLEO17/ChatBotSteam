import os
import sqlite3
import time
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Configuración de la API de OpenAI
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Configuración del administrador
ADMIN_CODE = "admin_mode"
ADMIN_PASS = "12072122"

# Inicializar base de datos
def inicializar_db():
    conn = sqlite3.connect("chatbot_memory.db")
    cursor = conn.cursor()
    # Tabla de memoria
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memoria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entrada TEXT,
        respuesta TEXT
    )
    """)
    # Tabla de historial
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historial (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        chatbot TEXT,
        fecha TEXT
    )
    """)
    # Tabla de resumenes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resumenes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contenido TEXT,
        fecha TEXT
    )
    """)
    # Tabla de documenetos (.txt con informacion)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        contenido TEXT,
        fecha TEXT
    )
    """)


    conn.commit()
    conn.close()

# Guardar conocimiento
def guardar_memoria(entrada, respuesta):
    conn = sqlite3.connect("chatbot_memory.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO memoria (entrada, respuesta) VALUES (?, ?)", (entrada, respuesta))
    conn.commit()
    conn.close()

# Buscar conocimiento exacto
def buscar_memoria(entrada):
    conn = sqlite3.connect("chatbot_memory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT respuesta FROM memoria WHERE entrada = ?", (entrada,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None

# Buscar conocimiento avanzado (por palabra clave)
def buscar_avanzado(palabra):
    conn = sqlite3.connect("chatbot_memory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, entrada, respuesta FROM memoria WHERE entrada LIKE ? OR respuesta LIKE ?", (f"%{palabra}%", f"%{palabra}%"))
    resultados = cursor.fetchall()
    conn.close()
    return resultados

# Ver todos los conocimientos
def ver_memoria():
    conn = sqlite3.connect("chatbot_memory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, entrada, respuesta FROM memoria")
    filas = cursor.fetchall()
    conn.close()
    return filas

# Eliminar conocimiento
def eliminar_memoria(id_registro):
    conn = sqlite3.connect("chatbot_memory.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM memoria WHERE id = ?", (id_registro,))
    conn.commit()
    conn.close()

# Reordenar IDs después de eliminar
def reordenar_ids():
    conn = sqlite3.connect("chatbot_memory.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE memoria_temp (id INTEGER PRIMARY KEY AUTOINCREMENT, entrada TEXT, respuesta TEXT)")
    cursor.execute("INSERT INTO memoria_temp (entrada, respuesta) SELECT entrada, respuesta FROM memoria ORDER BY id")
    cursor.execute("DROP TABLE memoria")
    cursor.execute("ALTER TABLE memoria_temp RENAME TO memoria")
    conn.commit()
    conn.close()

# Guardar historial
def guardar_historial(usuario, chatbot):
    conn = sqlite3.connect("chatbot_memory.db")
    cursor = conn.cursor()
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO historial (usuario, chatbot, fecha) VALUES (?, ?, ?)", (usuario, chatbot, fecha))
    conn.commit()
    conn.close()

# Ver historial
def ver_historial():
    conn = sqlite3.connect("chatbot_memory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, usuario, chatbot, fecha FROM historial")
    filas = cursor.fetchall()
    conn.close()
    return filas

# Obtener contexto (últimas 20 conversaciones)
def obtener_contexto():
    conn = sqlite3.connect("chatbot_memory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT usuario, chatbot FROM historial ORDER BY id ASC")
    conversaciones = cursor.fetchall()
    conn.close()
    return conversaciones

# Funcion para eliminar el Historial
def eliminar_historial():
    conn = sqlite3.connect("chatbot_memory.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM historial")  # borra todos los registros
    conn.commit()
    conn.close()

#Funcion que sirve para sacar conocimiento de un .txt
def  importar_txt(ruta):
    conn = sqlite3.connect("chatbot_memory.db")
    cursor = conn.cursor()
    with open(ruta, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            if ":" in linea:
                entrada, respuesta = linea.strip().split(":", 1)
                cursor.execute("INSERT INTO memoria (entrada, respuesta) VALUES (?, ?)", (entrada.strip(), respuesta.strip()))
    conn.commit()
    conn.close()

#Funcion para actualizar la Memoria
def actualizar_memoria(entrada, nueva_respuesta):
    conn = sqlite3.connect("chatbot_memory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM memoria WHERE entrada = ?", (entrada,))
    resultado = cursor.fetchone()
    if resultado:
        cursor.execute("UPDATE memoria SET respuesta = ? WHERE id = ?", (nueva_respuesta, resultado[0]))
    else:
        cursor.execute("INSERT INTO memoria (entrada, respuesta) VALUES (?, ?)", (entrada, nueva_respuesta))
    conn.commit()
    conn.close()   

# Funcion para guardar el Resumen
def guardar_resumen(contenido):
    conn = sqlite3.connect("chatbot_memory.db")
    cursor = conn.cursor()
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO resumenes (contenido, fecha) VALUES (?, ?)", (contenido, fecha))
    conn.commit()
    conn.close()     

# Funcion para obtener dichos Resumenes
def obtener_resumenes():
    conn = sqlite3.connect("chatbot_memory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT contenido FROM resumenes ORDER BY id ASC")
    resumenes = cursor.fetchall()
    conn.close()
    return resumenes

# Funcion para ingresar un .txt con texto
def importar_txt_completo(ruta):
    conn = sqlite3.connect("chatbot_memory.db")
    cursor = conn.cursor()
    with open(ruta, "r", encoding="utf-8") as archivo:
        contenido = archivo.read()
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nombre = os.path.basename(ruta)
        cursor.execute("INSERT INTO documentos (nombre, contenido, fecha) VALUES (?, ?, ?)", (nombre, contenido, fecha))
    conn.commit()
    conn.close()

# Funcion para buscar dentro de los documentos
def buscar_en_documentos(palabra):
    conn = sqlite3.connect("chatbot_memory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT contenido FROM documentos")
    documentos = cursor.fetchall()
    conn.close()
    resultados = []
    for doc in documentos:
        if palabra.lower() in doc[0].lower():
            resultados.append(doc[0])
    return resultados

# Eliminar Documentos con todo e informacion (Id)
def eliminar_documento(id_registro):
    conn = sqlite3.connect("chatbot_memory.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documentos WHERE id = ?", (id_registro,))
    conn.commit()
    conn.close()

# Ver a detalle los documentos cargados dentro del Software
def ver_documentos():
    conn = sqlite3.connect("chatbot_memory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM documentos")
    filas = cursor.fetchall()
    conn.close()
    return filas

# Funcion para crear una respuesta conforme a los documentos
def responder_usuario(mensaje):
    # Recuperar todos los documentos
    conn = sqlite3.connect("chatbot_memory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT contenido FROM documentos")
    documentos = cursor.fetchall()
    conn.close()

    if documentos:
        # Construir prompt con todos los documentos como contexto
        mensajes = [
            {"role": "system", "content": "Eres un asistente que responde de manera natural basándote en la información de documentos cargados."}
        ]

        for doc in documentos:
            mensajes.append({"role": "assistant", "content": doc[0]})

        mensajes.append({"role": "user", "content": mensaje})

        try:
            respuesta = client.chat.completions.create(
                model="gpt-5.4-mini",
                messages=mensajes
            )
            return respuesta.choices[0].message.content
        except Exception as e:
            return f"Error al generar respuesta: {e}"
    else:
        return "No encontré información en mis documentos."

# Genera la respuesta con info de los Documetos
def generar_respuesta(pregunta, contexto):
    # Construimos un prompt dinámico para el modelo
    mensajes = [
        {"role": "system", "content": "Eres un asistente que responde de manera natural basándote en la información de documentos cargados."},
        {"role": "assistant", "content": contexto},
        {"role": "user", "content": pregunta}
    ]

    try:
        respuesta = client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=mensajes
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"No pude generar respuesta dinámica: {e}"


# Funcion que responde con contexto
def responder_con_contexto(mensaje):
    resultados = buscar_en_documentos(mensaje)
    if resultados:
        contexto = resultados[0]
        return f"Con base en lo que tengo registrado: {contexto}"
    else:
        return "No encontré información sobre eso."

# Funcion para separar por categoría Academico, Emocional, General
def clasificar_info(texto):
    academico_keywords = ["estudio", "examen", "profesor", "tarea", "ceti", "materia", "clase", "estudiar", "materia", "mtro", "mtra", "profe"]
    emocional_keywords = ["amigo", "novio", "sentimiento", "feliz", "triste", "relación", "amor", "novia", "enojado", "deprimido", "amiga"]

    texto_lower = texto.lower()
    if any(palabra in texto_lower for palabra in academico_keywords):
        return "Académico"
    elif any(palabra in texto_lower for palabra in emocional_keywords):
        return "Emocional"
    else:
        return "General"

# Funcion para vaciar la pantalla
def limpiar_pantalla():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")
    print("=== Chatbot Académico ===")
    print("Escribe 'salir' para terminar.")
    print("Escribe 'vaciar_chat' para Vaciar la Pantalla.\n")

# Funcion que reordena las ids de los documentos .txt
def reordenar_ids_documentos():
    conn = sqlite3.connect("chatbot_memory.db")
    cursor = conn.cursor()

    # Obtener todos los documentos ordenados por id actual
    cursor.execute("SELECT id FROM documentos ORDER BY id")
    ids = cursor.fetchall()

    # Reasignar IDs consecutivos
    nuevo_id = 1
    for (id_actual,) in ids:
        cursor.execute("UPDATE documentos SET id = ? WHERE id = ?", (nuevo_id, id_actual))
        nuevo_id += 1

    conn.commit()
    conn.close()
    print("IDs de documentos reordenados correctamente.")

# Chat principal
def main():
    inicializar_db()
    print("=== Chatbot Académico ===")
    print("Escribe 'salir' para terminar.")
    print("Escribe 'vaciar_chat' para Vaciar la Pantalla.\n")

    while True:
        mensaje = input("Tú: ")
        if mensaje.lower() in ["salir", "exit"]:
            print("Chatbot: ¡Hasta luego!, Gracias Por Usar Este Software")
            time.sleep(2)
            break

        if mensaje.lower() == "vaciar_chat":
            limpiar_pantalla()
            continue

        # Activar modo administrador
        if mensaje == ADMIN_CODE:
            clave = input("Ingresa contraseña de administrador: ")
            if clave == ADMIN_PASS:
                print("\n Modo administrador activado.")
                print("Opciones:")
                print("1) Agregar conocimiento fijo → escribir: 'entrada:respuesta'")
                print("2) Ver base de datos → escribir: 'ver'")
                print("3) Eliminar conocimiento fijo → escribir: 'del:id'")
                print("4) Buscar avanzado → escribir: 'buscar:palabra'")
                print("5) Ver historial → escribir: 'historial'")
                print("6) Eliminar Historial → escribir: 'borrar_historial'")
                print("7) Añadir documentos .txt → escribir: 'importar_txt:(nombre).txt'")
                print("8) Ver documentos dentro del Software → escribir: 'ver_documentos'")
                print("9) Eliminar documento por Id → escribir: 'del_doc:id'")
                print("Escribe 'salir' para volver al chat normal.\n")

                while True:
                    admin_msg = input("Admin: ")
                    if admin_msg.lower() == "salir":
                        print("Saliendo de modo administrador.\n")
                        break
                    elif admin_msg.lower() == "ver":
                        registros = ver_memoria()
                        for r in registros:
                            print(f"{r[0]}: {r[1]} → {r[2]}")
                    elif admin_msg.startswith("del:"):
                        try:
                            id_registro = int(admin_msg.split(":")[1])
                            eliminar_memoria(id_registro)
                            reordenar_ids()
                            print(f"Registro {id_registro} eliminado y IDs reordenados.")
                        except:
                            print("Formato incorrecto. Usa del:id")
                    elif admin_msg.startswith("buscar:"):
                        palabra = admin_msg.split(":")[1]
                        resultados = buscar_avanzado(palabra)
                        if resultados:
                            for r in resultados:
                                print(f"{r[0]}: {r[1]} → {r[2]}")
                        else:
                            print("No se encontraron coincidencias.")
                    elif admin_msg.lower() == "historial":
                        registros = ver_historial()
                        for r in registros:
                            print(f"{r[0]} | Usuario: {r[1]} | Chatbot: {r[2]} | Fecha: {r[3]}")
                    elif admin_msg.lower() == "borrar_historial":
                        eliminar_historial()
                        print("Historial Eliminado")
                    elif admin_msg.startswith("importar_txt:"):
                        ruta = admin_msg.split(":", 1)[1].strip()
                        try:
                            importar_txt_completo(ruta)
                            print(f"Conocimientos Agregados correctamente desde {ruta}")
                        except Exception as e:
                            print("Error al importar el archivo: ", e)
                    elif admin_msg.lower() == "ver_documentos":
                        registros = ver_documentos()
                        for r in registros:
                            print(f"ID: {r[0]} | Nombre: {r[1]}")
                    elif admin_msg.startswith("del_doc:"):
                        try:
                            id_registro = int(admin_msg.split(":", 1)[1])
                            eliminar_documento(id_registro)
                            reordenar_ids_documentos()
                            print(f"Documento con id {id_registro} eliminado con Exito.")
                        except Exception as e:
                            print("Error al eliminar documento ", e)
                    elif ":" in admin_msg:
                        entrada, respuesta = admin_msg.split(":", 1)
                        guardar_memoria(entrada.strip(), respuesta.strip())
                        print(f"Guardado: '{entrada.strip()}' → '{respuesta.strip()}'")
                    else:
                        print("Comando no reconocido.")
            else:
                print("Contraseña incorrecta.")
            continue

        # Recuperar todos los documentos
        conn = sqlite3.connect("chatbot_memory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT contenido FROM documentos")
        documentos = cursor.fetchall()
        conn.close()

        # Construir contexto
        mensajes = [
            {"role": "system", "content": "Responde basándote en documentos, resúmenes y el historial. Si no hay información en documentos, usa resúmenes e historial. Si tampoco hay nada, responde: 'De eso no hemos hablado todavía, ¿me lo podrías explicar? Así lo guardo y podré responderte mejor después.'"}
        ]

        # Incluir resúmenes
        for r in obtener_resumenes():
            mensajes.append({"role": "assistant", "content": r[0]})

        # Incluir historial
        contexto = obtener_contexto()
        for usuario, chatbot in contexto:
            mensajes.append({"role": "user", "content": usuario})
            mensajes.append({"role": "assistant", "content": chatbot})

        # Incluir documentos
        for doc in documentos:
            mensajes.append({"role": "assistant", "content": doc[0]})

        # Mensaje actual
        mensajes.append({"role": "user", "content": mensaje})

        try:
            respuesta = client.chat.completions.create(
                model="gpt-5.4-mini",
                messages=mensajes
            )
            texto = respuesta.choices[0].message.content
            print("Chatbot:", texto)
            guardar_historial(mensaje, texto)

            # Cada 50 conversaciones, generar resumen
            if len(ver_historial()) % 50 == 0:
                historial = ver_historial()
                texto_historial = "\n".join([f"Usuario: {h[1]} | Chatbot: {h[2]}" for h in historial[-50:]])
                resumen = client.chat.completions.create(
                    model="gpt-5.4-mini",
                    messages=[{"role": "system", "content": "Resume las siguientes conversaciones destacando datos importantes y preferencias del usuario."},
                              {"role": "user", "content": texto_historial}]
                )
                guardar_resumen(resumen.choices[0].message.content)

            # Este If hace la clasificacion
            if "me lo podrías explicar" in texto.lower():
                nueva_info = input("Tú: ")
                categoria = clasificar_info(nueva_info)
                guardar_memoria(mensaje, f"[{categoria}] {nueva_info}")
                print(f"Chatbot: Gracias, lo guardaré dentro de mi memoria.")

        except Exception as e:
            print("Error:", e)

        # Separador entre conversaciones
        print("\n")

if __name__ == "__main__":
    main()
