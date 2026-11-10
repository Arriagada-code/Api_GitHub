import json
import os
import sys
from pathlib import Path

import requests
from tabulate import tabulate

API_URL = "https://api.github.com"
OUTPUT_FILE = Path("repositorios.json")
TIMEOUT_SECONDS = 15
REPOS_PER_PAGE = 100


def obtener_repositorios(usuario_ingresado):
    """Verifica el usuario y obtiene sus repositorios públicos y privados."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("Configura la variable de entorno GITHUB_TOKEN.")

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"Bearer {token}",
    }

    respuesta_usuario = requests.get(
        f"{API_URL}/user",
        headers=headers,
        timeout=TIMEOUT_SECONDS,
    )
    respuesta_usuario.raise_for_status()
    datos_usuario = respuesta_usuario.json()
    usuario_autenticado = datos_usuario.get("login") if isinstance(datos_usuario, dict) else None
    if not usuario_autenticado:
        raise ValueError("GitHub no devolvió el nombre de la cuenta autenticada.")
    if usuario_ingresado.strip().casefold() != usuario_autenticado.casefold():
        raise ValueError(
            "El usuario ingresado no coincide con la cuenta del token "
            f"({usuario_autenticado})."
        )

    repositorios = []
    pagina = 1
    while True:
        respuesta = requests.get(
            f"{API_URL}/user/repos",
            headers=headers,
            params={
                "visibility": "all",
                "affiliation": "owner",
                "per_page": REPOS_PER_PAGE,
                "page": pagina,
            },
            timeout=TIMEOUT_SECONDS,
        )
        respuesta.raise_for_status()
        datos = respuesta.json()
        if not isinstance(datos, list):
            raise ValueError("La respuesta de GitHub no tiene el formato esperado.")
        repositorios.extend(datos)
        if len(datos) < REPOS_PER_PAGE:
            break
        pagina += 1
    return repositorios


def guardar_resultado(repositorios, archivo=OUTPUT_FILE):
    """Guarda el resumen de repositorios en un archivo JSON."""
    resumen = [
        {
            "nombre": repo.get("name"),
            "tipo": "privado" if repo.get("private") else "público",
            "descripcion": repo.get("description") or "Sin descripción",
            "lenguaje": repo.get("language") or "No especificado",
            "estrellas": repo.get("stargazers_count", 0),
        }
        for repo in repositorios
    ]
    with archivo.open("w", encoding="utf-8") as salida:
        json.dump(resumen, salida, ensure_ascii=False, indent=4)


def main():
    try:
        usuario = input("Ingrese su nombre de usuario de GitHub: ").strip()
        if not usuario:
            raise ValueError("El nombre de usuario no puede estar vacío.")

        repositorios = obtener_repositorios(usuario)
        filas = [
            [
                repo.get("name") or "Sin nombre",
                "privado" if repo.get("private") else "público",
                repo.get("description") or "Sin descripción",
                repo.get("language") or "No especificado",
                repo.get("stargazers_count", 0),
            ]
            for repo in repositorios
        ]
        columnas = ["Nombre", "Tipo", "Descripción", "Lenguaje", "Estrellas"]
        print(f"\nRepositorios encontrados: {len(repositorios)}")
        print(tabulate(filas, headers=columnas, tablefmt="grid"))

        guardar_resultado(repositorios)
        print(f"Se guardaron {len(repositorios)} repositorios en {OUTPUT_FILE}.")
    except ValueError as error:
        print(f"Configuración o respuesta inválida: {error}", file=sys.stderr)
        return 1
    except requests.exceptions.HTTPError as error:
        codigo = error.response.status_code if error.response is not None else "desconocido"
        if codigo == 401:
            mensaje = "GitHub rechazó el token. Comprueba que sea válido."
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
