import csv
from datetime import datetime
import os

import requests
from tabulate import tabulate

print("N° DE FARMACIAS DE TURNO")
while True:
    comuna_destino = input("ingresa la comuna: ").upper()  # comuna asociada al envío
    url = 'https://midas.minsal.cl/farmacia_v2/WS/getLocalesTurnos.php'
    try:
        respuesta = requests.get(url, timeout=10)
        respuesta.raise_for_status()
        farmacias = respuesta.json()
        print("Datos recibidos correctamente")
    except requests.exceptions.Timeout as error:
        print(f"La consulta superó los 10 segundos: {error}")
        farmacias = None
    except requests.exceptions.HTTPError as error:
        print(f"La API devolvió un error HTTP: {error}")
        farmacias = None
    except requests.exceptions.RequestException as error:
        print(f"No fue posible completar la solicitud: {error}")
        farmacias = None
    except Exception as error:
        print(f"Ocurrió un error inesperado: {type(error).__name__}: {error}")
        farmacias = None

    if farmacias is not None:
        farmacias_comuna = []
        for farmacia in farmacias:
            if farmacia.get('comuna_nombre', '').upper() == comuna_destino:
                fecha_hora = datetime.strptime(
                    f"{farmacia['fecha']} {farmacia['funcionamiento_hora_apertura']}", "%Y-%m-%d %H:%M:%S" ,)
                
                farmacias_comuna.append({
                    "timestamp": fecha_hora.strftime("%Y-%m-%d %H:%M:%S"),
                    "comuna": farmacia['comuna_nombre'],
                    "local_nombre": farmacia['local_nombre'],
                    "direccion": farmacia['local_direccion'], })

        columnas = ["timestamp", "comuna", "local_nombre", "direccion"]
        cantidad = len(farmacias_comuna)

        print(f'Se encontraron {cantidad} farmacias de turno en {comuna_destino}.')
        print(tabulate(farmacias_comuna, headers="keys", tablefmt="grid"))

        archivo_salida = os.path.join(
            os.path.dirname(__file__),
            "farmacias_turno.csv",
        )
        archivo_existe = os.path.exists(archivo_salida)
        with open(archivo_salida, "a", newline="", encoding="utf-8") as archivo_csv:
            escritor = csv.DictWriter(archivo_csv, fieldnames=columnas)
            if not archivo_existe:
                escritor.writeheader()
            escritor.writerows(farmacias_comuna)

        print(f"Resultados agregados en {os.path.basename(archivo_salida)}")
    try:
        seguir=int(input("Para seguir digita un 1 culaquier otro numero es para finalizar: "))
        if seguir !=1:
            break
        else:
            continue
    except ValueError:
        print("Debes digitar un digito")
print("ADIOS")
