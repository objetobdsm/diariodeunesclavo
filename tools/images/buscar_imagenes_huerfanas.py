from pathlib import Path
import re

content = Path("content")
uploads = Path("static/uploads")

# Extensiones de imagen
exts = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}

# Buscar todas las imágenes realmente referenciadas
usadas = set()

patron = re.compile(r'uploads/[^")\s>]+')

for archivo in content.rglob("*"):
    if archivo.suffix.lower() not in {".md", ".html"}:
        continue

    try:
        texto = archivo.read_text(encoding="utf-8", errors="ignore")
    except:
        continue

    for m in patron.findall(texto):
        usadas.add(m.replace("\\", "/"))

# Recorrer uploads
todas = []

for f in uploads.rglob("*"):
    if f.is_file() and f.suffix.lower() in exts:
        rel = f.relative_to("static").as_posix()
        todas.append(rel)

todas = set(todas)

huerfanas = sorted(todas - usadas)

print("="*60)
print("RESUMEN")
print("="*60)
print()

print(f"Imágenes totales : {len(todas)}")
print(f"Imágenes usadas  : {len(usadas)}")
print(f"Huérfanas        : {len(huerfanas)}")
print()

with open("imagenes_huerfanas.txt","w",encoding="utf8") as f:
    for img in huerfanas:
        f.write(img+"\n")

print("Listado guardado en imagenes_huerfanas.txt")
