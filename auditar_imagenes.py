#!/usr/bin/env python3

from pathlib import Path
from PIL import Image
import os

BASE = Path("static/uploads")

extensiones = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}

total = 0
peso_total = 0

por_extension = {}
muy_grandes = []

print("Analizando imágenes...\n")

for fichero in BASE.rglob("*"):

    if not fichero.is_file():
        continue

    if fichero.suffix.lower() not in extensiones:
        continue

    total += 1

    peso = fichero.stat().st_size
    peso_total += peso

    ext = fichero.suffix.lower()

    por_extension.setdefault(ext, 0)
    por_extension[ext] += 1

    try:
        with Image.open(fichero) as img:
            ancho, alto = img.size
    except Exception:
        continue

    if ancho > 1800 or peso > 500000:
        muy_grandes.append(
            (
                peso,
                ancho,
                alto,
                fichero
            )
        )

print("=" * 60)
print("RESUMEN")
print("=" * 60)
print()

print(f"Imágenes: {total}")
print(f"Peso total: {peso_total/1024/1024:.1f} MB")
print()

print("Por formato:")

for ext, cantidad in sorted(
        por_extension.items(),
        key=lambda x: x[1],
        reverse=True):

    print(f"  {ext:6} {cantidad}")

print()

print("Las 30 imágenes más pesadas:\n")

muy_grandes.sort(reverse=True)

for peso, ancho, alto, ruta in muy_grandes[:30]:

    print(
        f"{peso/1024/1024:7.2f} MB   "
        f"{ancho:5}x{alto:<5}   "
        f"{ruta}"
    )
