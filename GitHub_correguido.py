import json
import os
import sys
from pathlib import Path
from urllib.parse import quote
import requests

API_URL = "https://api.github.com"
OUTPUT_FILE = Path("repositorios.json")
TIMEOUT_SECONDS = 15

def obtener_repositorios(usuario):
    """Obtiene todos los repositorios públicos de un usuario de GitHub."""
    usuario = usuario.strip()
    if not usuario:
        raise ValueError("El nombre de usuario no puede estar vacío.")

    url = f"{API_URL}/users/{quote(usuario, safe='')}/repos"


    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    repositorios = []
    pagina = 1

    while True:
        respuesta = requests.get( url,
            headers=headers,
            params={"per_page": 100, "page": pagina, "type": "owner"},
            timeout=TIMEOUT_SECONDS, )
        respuesta.raise_for_status()
        datos = respuesta.json()
        if not isinstance(datos, list):
            raise ValueError("La respuesta de GitHub no tiene el formato esperado.")
        repositorios.extend(datos)
        if len(datos) < 100:
            break
        pagina += 1
    return repositorios

def guardar_resultado(repositorios, archivo=OUTPUT_FILE):
    """Guarda un resumen de los repositorios en un archivo JSON."""
    resumen = [
        {
            "nombre": repo.get("name"),
            "lenguaje": repo.get("language"),
            "estrellas": repo.get("stargazers_count"),
        }
        for repo in repositorios
    ]
    with archivo.open("w", encoding="utf-8") as salida:
        json.dump(resumen, salida, ensure_ascii=False, indent=4)

def main():
    usuario = input("Ingrese usuario de GitHub: ").strip()
    try:
        repositorios = obtener_repositorios(usuario)
        for repo in repositorios:
            print(f"{repo.get('name')} - {repo.get('stargazers_count')} estrellas")

        guardar_resultado(repositorios)
        print(f"Se guardaron {len(repositorios)} repositorios en {OUTPUT_FILE}.")
    except ValueError as error:
        print(f"Entrada o respuesta inválida: {error}", file=sys.stderr)
        return 1
    except requests.exceptions.HTTPError as error:
        codigo = error.response.status_code if error.response is not None else "desconocido"
        if codigo == 404:
            mensaje = "No se encontró ese usuario de GitHub."
        elif codigo == 403:
            mensaje = "GitHub rechazó la solicitud o se alcanzó el límite de consultas."
        else:
            mensaje = f"GitHub respondió con un error HTTP ({codigo})."
        print(mensaje, file=sys.stderr)
        return 1
    except requests.exceptions.RequestException as error:
        print(f"No se pudo conectar con GitHub: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"No se pudo guardar {OUTPUT_FILE}: {error}", file=sys.stderr)
        return 1
    print("Proceso terminado.")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
