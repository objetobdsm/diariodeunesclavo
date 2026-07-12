#!/usr/bin/env python3
import csv
import re
from pathlib import Path

ROOT = Path(".").resolve()
CSV_POSTS = ROOT / "posts_con_blogger_public.csv"
CONTENT_POSTS = ROOT / "content" / "posts"
STATIC_UPLOADS = ROOT / "static" / "uploads"
PUBLIC_UPLOADS = ROOT / "public" / "uploads"

OUT_DIR = ROOT / "salida_resolver_blogger_restantes"
OUT_DIR.mkdir(exist_ok=True)

CSV_REEMPLAZADAS = OUT_DIR / "reemplazadas.csv"
CSV_NO_ENCONTRADAS = OUT_DIR / "no_encontradas.csv"
TXT_RESUMEN = OUT_DIR / "resumen.txt"

IMG_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg"}


def slug_from_public_html(html_file: str) -> str:
    """
    public/posts/2007-12-21-leathercowboy/index.html
      -> 2007-12-21-leathercowboy.md
    """
    p = Path(html_file)
    # ... / posts / slug / index.html
    slug = p.parent.name
    return slug + ".md"


def build_upload_index():
    """
    Recorre static/uploads y crea un índice:
      original_url -> /uploads/...
    leyendo el contenido de archivos sospechosos que contienen la URL original.
    """
    index = {}

    if not STATIC_UPLOADS.exists():
        return index

    for f in STATIC_UPLOADS.rglob("*"):
        if not f.is_file():
            continue

        rel = "/" + f.relative_to(STATIC_UPLOADS.parent).as_posix()

        # Intentamos leer el archivo como texto por si contiene la URL original
        # (muchos de esos "jpg" descargados en falso parecen guardarla dentro)
        try:
            data = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        # Buscar URLs blogger/googleusercontent dentro del archivo
        urls = re.findall(r'https?://[^\s<>"\')]+', data)
        for u in urls:
            if any(x in u for x in ("bp.blogspot.com", "googleusercontent.com", "gvt0.com")):
                index[u] = rel

    return index


def main():
    if not CSV_POSTS.exists():
        raise SystemExit(f"No existe {CSV_POSTS}")

    upload_index = build_upload_index()

    reemplazadas = []
    no_encontradas = []

    with CSV_POSTS.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for row in rows:
        html_file = row["html_file"]
        old_url = row["url"]

        md_name = slug_from_public_html(html_file)
        md_path = CONTENT_POSTS / md_name

        if not md_path.exists():
            no_encontradas.append({
                "html_file": html_file,
                "md_file": str(md_path.relative_to(ROOT)),
                "old_url": old_url,
                "motivo": "markdown_no_existe",
            })
            continue

        if old_url not in upload_index:
            no_encontradas.append({
                "html_file": html_file,
                "md_file": str(md_path.relative_to(ROOT)),
                "old_url": old_url,
                "motivo": "sin_ruta_local_en_uploads",
            })
            continue

        new_url = upload_index[old_url]

        content = md_path.read_text(encoding="utf-8")
        if old_url not in content:
            no_encontradas.append({
                "html_file": html_file,
                "md_file": str(md_path.relative_to(ROOT)),
                "old_url": old_url,
                "motivo": "url_no_aparece_en_markdown",
            })
            continue

        updated = content.replace(old_url, new_url)
        md_path.write_text(updated, encoding="utf-8")

        reemplazadas.append({
            "html_file": html_file,
            "md_file": str(md_path.relative_to(ROOT)),
            "old_url": old_url,
            "new_url": new_url,
        })

    # Guardar CSV reemplazadas
    with CSV_REEMPLAZADAS.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["html_file", "md_file", "old_url", "new_url"]
        )
        writer.writeheader()
        writer.writerows(reemplazadas)

    # Guardar CSV no encontradas
    with CSV_NO_ENCONTRADAS.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["html_file", "md_file", "old_url", "motivo"]
        )
        writer.writeheader()
        writer.writerows(no_encontradas)

    resumen = []
    resumen.append("RESUMEN RESOLVER BLOGGER RESTANTES")
    resumen.append("=" * 60)
    resumen.append(f"Posts del CSV: {len(rows)}")
    resumen.append(f"Reemplazadas: {len(reemplazadas)}")
    resumen.append(f"No encontradas / no resueltas: {len(no_encontradas)}")
    resumen.append("")
    resumen.append(f"CSV reemplazadas: {CSV_REEMPLAZADAS}")
    resumen.append(f"CSV no encontradas: {CSV_NO_ENCONTRADAS}")

    TXT_RESUMEN.write_text("\n".join(resumen), encoding="utf-8")

    print("[OK] Proceso completado")
    print(f"  - {CSV_REEMPLAZADAS}")
    print(f"  - {CSV_NO_ENCONTRADAS}")
    print(f"  - {TXT_RESUMEN}")
    print("")
    print(f"Reemplazadas: {len(reemplazadas)}")
    print(f"No encontradas: {len(no_encontradas)}")


if __name__ == "__main__":
    main()
