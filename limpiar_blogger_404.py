#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import re
from pathlib import Path

# ============================================================
# CONFIG
# ============================================================

CSV_FALLIDAS = Path(
    "/home/gustavo/Escritorio/Descargas/blogger2static/migration_blog/"
    "salida_descargar_blogger_faltantes/fallidas.csv"
)

ROOT = Path(
    "/home/gustavo/Escritorio/Descargas/blogger2static/migration_blog"
)

DRY_RUN = False   # pon True si quieres probar sin escribir cambios


# ============================================================
# HELPERS
# ============================================================

def read_failed_rows(csv_path: Path):
    rows = []
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            html_file = (row.get("html_file") or "").strip()
            md_file = (row.get("md_file") or "").strip()
            old_url = (row.get("old_url") or "").strip()
            motivo = (row.get("motivo") or "").strip()
            if md_file and old_url:
                rows.append({
                    "html_file": html_file,
                    "md_file": md_file,
                    "old_url": old_url,
                    "motivo": motivo,
                })
    return rows


def remove_markdown_image_lines(text: str, url: str):
    """
    Elimina líneas enteras que sean una imagen Markdown y contengan la URL.
    Ej:
      ![](https://...)
      ![alt](https://...)
    """
    changed = False
    new_lines = []
    for line in text.splitlines(keepends=True):
        line_no_nl = line.rstrip("\r\n")
        if url in line_no_nl and re.search(r'!\[[^\]]*\]\([^)]+\)', line_no_nl):
            changed = True
            continue
        new_lines.append(line)
    return "".join(new_lines), changed


def remove_html_img_tags(text: str, url: str):
    """
    Elimina etiquetas <img ...> que contengan exactamente la URL.
    """
    pattern = re.compile(
        r'<img\b[^>]*\bsrc=(["\'])' + re.escape(url) + r'\1[^>]*>',
        re.IGNORECASE | re.DOTALL
    )
    new_text, n = pattern.subn("", text)
    return new_text, (n > 0)


def remove_url_inside_markdown_image_inline(text: str, url: str):
    """
    Por si la imagen Markdown no ocupa una línea sola, elimina el fragmento ![](...)
    que contenga esa URL.
    """
    pattern = re.compile(
        r'!\[[^\]]*\]\(' + re.escape(url) + r'\)'
    )
    new_text, n = pattern.subn("", text)
    return new_text, (n > 0)


def remove_raw_url(text: str, url: str):
    """
    Último recurso: elimina la URL exacta si quedó suelta en el contenido.
    """
    if url in text:
        return text.replace(url, ""), True
    return text, False


def cleanup_extra_blank_lines(text: str):
    """
    Reduce bloques de 3+ saltos de línea a 2.
    """
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text


def resolve_md_path(md_file_value: str) -> Path:
    """
    md_file ya viene como:
      content/posts/xxxx.md
    Lo resolvemos relativo a ROOT.
    """
    p = ROOT / md_file_value
    return p.resolve()


# ============================================================
# MAIN
# ============================================================

def main():
    if not CSV_FALLIDAS.exists():
        raise SystemExit(f"No existe el CSV: {CSV_FALLIDAS}")

    rows = read_failed_rows(CSV_FALLIDAS)
    if not rows:
        print("No hay filas en fallidas.csv")
        return

    total = len(rows)
    modificados = 0
    sin_cambios = 0

    print("LIMPIEZA DE IMÁGENES BLOGGER 404")
    print("=" * 60)
    print(f"Entradas en CSV: {total}")
    print(f"DRY_RUN: {DRY_RUN}")
    print()

    for row in rows:
        md_path = resolve_md_path(row["md_file"])
        old_url = row["old_url"]

        if not md_path.exists():
            print(f"[NO EXISTE MD] {md_path}")
            sin_cambios += 1
            continue

        original = md_path.read_text(encoding="utf-8")
        text = original
        changed_any = False

        # 1) borrar líneas Markdown completas con ![](...)
        text, changed = remove_markdown_image_lines(text, old_url)
        changed_any = changed_any or changed

        # 2) borrar <img src="old_url" ...>
        text, changed = remove_html_img_tags(text, old_url)
        changed_any = changed_any or changed

        # 3) borrar ![](...) inline si quedó incrustado en párrafo
        text, changed = remove_url_inside_markdown_image_inline(text, old_url)
        changed_any = changed_any or changed

        # 4) último recurso: borrar la URL suelta
        text, changed = remove_raw_url(text, old_url)
        changed_any = changed_any or changed

        if changed_any:
            text = cleanup_extra_blank_lines(text)

            if not DRY_RUN:
                md_path.write_text(text, encoding="utf-8")

            modificados += 1
            print(f"[OK] limpiado: {md_path}")
            print(f"     URL: {old_url}")
        else:
            sin_cambios += 1
            print(f"[SIN CAMBIOS] {md_path}")
            print(f"     URL no encontrada en el MD: {old_url}")

    print()
    print("RESUMEN")
    print("=" * 60)
    print(f"Entradas CSV: {total}")
    print(f"MD modificados: {modificados}")
    print(f"Sin cambios: {sin_cambios}")


if __name__ == "__main__":
    main()
