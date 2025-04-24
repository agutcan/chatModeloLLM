import requests
import uuid
from typing import Optional
import time
import tkinter as Tk
from tkinter import filedialog  # Importa filedialog para abrir el explorador de archivos
import mimetypes


# Configuración de la API
API_BASE_URL = "http://192.168.9.102:8000"  # Cambia esto si tu API está en otro lugar

def generate_text(prompt: str, session_id: str = "",  file_text: str = "", file_type: str = "", file_name: str = "") -> Optional[dict]:
    """
    Función para enviar una solicitud a la API de generación de texto
    
    Args:
        prompt: El texto prompt para enviar al modelo
        session_id: Identificador de sesión del usuario
        
    Returns:
        dict: La respuesta de la API o None si hay error
    """
    # Cabecera con la cookie de sesión
    headers = {
        "Cookie": f"session_id={session_id}"  # Incluir el session_id en las cabeceras
    }

    # Definir la URL de la API
    url = f"{API_BASE_URL}/generate"
    
    # Definir el payload con los parámetros de la solicitud
    payload = {
        "prompt": prompt,
        "file_text": file_text,
        "file_type": file_type,
        "file_name": file_name
    }
    
    try:
        start_time = time.time()  # Registramos el tiempo de inicio
        response = requests.post(url, json=payload, headers=headers, )  # Enviar solicitud POST a la API
        response.raise_for_status()  # Verificar si hubo un error en la respuesta
        end_time = time.time()  # Registramos el tiempo de finalización
        
        response_data = response.json()  # Convertimos la respuesta en JSON
        response_data['response_time'] = end_time - start_time  # Añadimos el tiempo de respuesta
        
        return response_data  # Retornamos la respuesta procesada
    except requests.exceptions.RequestException as e:
        print(f"Error al llamar a la API: {e}")  # Imprimimos el error en caso de fallo
        return None

# Obtener el tipo MIME basado en la extensión del archivo
def get_mime_type(file_path: str):
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        # Si no se encuentra un tipo MIME válido, asignar un valor por defecto
        return "application/octet-stream"
    return mime_type

def upload_file(session_id: str) -> Optional[dict]:
    """
    Función para subir un archivo PDF, TXT, DOCX, PPTX, XLSX, PNG o JPG a la API y recibir el texto extraído
    
    Args:
        session_id: Identificador de sesión del usuario
        
    Returns:
        dict: La respuesta de la API con el texto extraído del archivo o None si hay error
    """
     # Iniciar tkinter para abrir el explorador de archivos
    root = Tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    # Abrir el cuadro de diálogo para seleccionar un archivo
    file_path = filedialog.askopenfilename(
        title="Selecciona un archivo PDF, TXT, DOCX, PPTX, XLSX, PNG o JPG",
        filetypes=[(
            "Archivos PDF, TXT, DOCX, PPTX, XLSX, PNG y JPG",
            "*.pdf;*.txt;*.docx;*.pptx;*.xlsx;*.png;*.jpg;*.jpeg"  # Usamos el punto y coma para separar las extensiones
        )]
    )

    
    if not file_path:  # Si el usuario no selecciona un archivo, retornar None
        print("No se seleccionó un archivo.")
        root.quit()  # Asegurarse de destruir la ventana después de usarla
        return None
    
    url = f"{API_BASE_URL}/upload_file"
    
    # Abrir el archivo en modo binario
    with open(file_path, "rb") as file:
        # Obtener el tipo MIME para el archivo
        mime_type = get_mime_type(file_path)
        
        # Crear los archivos para la solicitud
        files = {"file": (file_path, file, mime_type)}
        headers = {
            "Cookie": f"session_id={session_id}"  # Incluir el session_id en las cabeceras
        }
        
        try:
            start_time = time.time()  # Registrar el tiempo de inicio
            response = requests.post(url, files=files, headers=headers)  # Enviar archivo
            response.raise_for_status()  # Verificar si hubo un error en la respuesta
            end_time = time.time()  # Registrar el tiempo de finalización
            
            response_data = response.json()  # Convertir la respuesta en JSON
            response_data['response_time'] = end_time - start_time  # Añadir el tiempo de respuesta
            root.quit()  # Asegurarse de destruir la ventana después de usarla

            return response_data  # Retornar la respuesta procesada
        except requests.exceptions.RequestException as e:
            print(f"Error al subir el archivo: {e}")  # Imprimir el error en caso de fallo
            root.quit()  # Asegurarse de destruir la ventana después de usarla
            return None

def main():
    """
    Función principal para manejar la interacción con el usuario
    """
    
    session_id = str(uuid.uuid4())  # Generar un nuevo ID de sesión si no existe uno previo

    while True:
        print("\n--- Generador de respuestas con IA ---")
        print("Escribe tu pregunta (o 'salir' para terminar):")
        
        user_input = input("> ").strip()  # Obtener entrada del usuario y eliminar espacios innecesarios
        
        if user_input.lower() in ['salir', 'exit', 'quit']:  # Salir si el usuario lo indica
            break
        
        if not user_input:
            continue  # Si la entrada está vacía, repetir el bucle
        
        choice = input("Desea subir un archivo PDF, TXT, DOCX, PPTX, XLSX, PNG, WEBP o JPG (Y/N): ").strip()
        while choice.lower() != "y" and choice.lower() != "n":
            choice = input("Debe seleccionar una opción correcta (Y/N): ").strip()

        file_text = ""
        file_name = ""
        file_type = ""

        if choice.lower() == "y":
            print("Selecciona un archivo PDF, TXT, DOCX, PPTX, XLSX, PNG, WEBP o JPG para subirlo...")
            response = upload_file(session_id)
            if response:
                file_text = response.get("file_text", "No se pudo extraer texto")   
                file_type = response.get("file_type", "No se pudo extraer texto")
                file_name = response.get("file_name", "No se pudo extraer texto")
                file_name = file_name[file_name.rfind("/")+1:]
            else:
                print("No se pudo procesar el archivo.")
                continue
        
        print("\nGenerando respuesta...\n")
        
        # Llamar a la API con el prompt del usuario y el session_id
        response = generate_text(prompt=user_input, session_id=session_id, file_text=file_text, file_type=file_type, file_name=file_name)
        
        if response:  # Si la respuesta de la API es válida
            print("\nRespuesta:")
            print(response.get("response", "No se recibió respuesta"))
            
            # Mostramos el tiempo de respuesta en segundos con 2 decimales
            print(f"\nTiempo de respuesta: {response.get('response_time', 0):.2f} segundos")
        else:
            print("No se pudo obtener una respuesta de la API")  # Mensaje de error si no hay respuesta


if __name__ == "__main__":
    try:
        root = Tk()
        root.withdraw()
        root.destroy()
    except:
        pass
    main()  # Ejecutar la función principal si el script se ejecuta directamente
