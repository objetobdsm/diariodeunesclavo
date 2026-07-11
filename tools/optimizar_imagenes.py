#!/usr/bin/env python3

from pathlib import Path
from PIL import Image

BASE = Path("static/uploads")

ANCHO_MAX = 1800
PESO_MINIMO = 1 * 1024 * 1024      # 1 MB

extensiones = {".jpg", ".jpeg"}

candidatas = []

peso_actual = 0
peso_estimado = 0

for fichero in BASE.rglob("*"):

    if not fichero.is_file():
        continue

    if fichero.suffix.lower() not in extensiones:
        continue

    try:
        with Image.open(fichero) as img:
            ancho, alto = img.size
    except Exception:
        continue

    peso = fichero.stat().st_size

    if ancho <= ANCHO_MAX and peso <= PESO_MINIMO:
        continue

    nuevo_ancho = min(ancho, ANCHO_MAX)
    nuevo_alto = int(alto * nuevo_ancho / ancho)

    estimado = peso * (nuevo_ancho / ancho) ** 2 * 0.85

    peso_actual += peso
    peso_estimado += estimado

    candidatas.append(
        (
            peso,
            ancho,
            alto,
            nuevo_ancho,
            nuevo_alto,
            fichero
        )
    )

candidatas.sort(reverse=True)

print()
print("=" * 70)
print("SIMULACIÓN DE OPTIMIZACIÓN")
print("=" * 70)
print()

print(f"Imágenes candidatas: {len(candidatas)}")
print()

for peso, ancho, alto, na, nalto, ruta in candidatas[:30]:

    print(
        f"{peso/1024/1024:6.2f} MB   "
        f"{ancho}x{alto}  →  "
        f"{na}x{nalto}   "
        f"{ruta}"
    )

print()
print("-" * 70)

print(f"Peso actual : {peso_actual/1024/1024:.1f} MB")
print(f"Peso estimado: {peso_estimado/1024/1024:.1f} MB")
print(f"Ahorro estimado: {(peso_actual-peso_estimado)/1024/1024:.1f} MB")
