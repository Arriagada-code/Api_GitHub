import requests
import json

TOKEN = 'ghp_A1b2C3d4E5f6G7h8I9j0SECRETO'


def obtener_repositorios(usuario):
    
    url = 'https://api.github.com/users/' + usuario + '/repos'
    headers = {
        'Authorization': 'Bearer ' + TOKEN,
        'Accept': 'application/vnd.github+json'
    }
    respuesta = requests.get(url, headers=headers)
    datos = respuesta.json()
    return datos


def guardar_resultado(repositorios, archivo):
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(repositorios, f, indent=4)


usuario = input('Ingrese usuario de GitHub: ')

try:
    repositorios = obtener_repositorios(usuario)
    resumen = []
    for repo in repositorios:
        resumen.append({
            'nombre': repo.get('name'),
            'lenguaje': repo.get('language'),
            'estrellas': repo.get('stargazers_count')
        })
        print(repo.get('name'), '-', repo.get('stargazers_count'), 'estrellas')
    guardar_resultado(resumen, 'repositorios.json')
    print('Archivo repositorios.json generado.')
except Exception:
    pass

print('Proceso terminado.')
