#!/usr/bin/env python3
import csv
import hashlib
import mimetypes
import os
import re
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(".").resolve()

CSV_INPUT = ROOT / "salida_resolver_blogger_restantes" / "no_encontradas.csv"
CONTENT_POSTS = ROOT / "content" / "posts"
STATIC_UPLOADS = ROOT / "static" / "uploads"

OUT_DIR = ROOT / "salida_descargar_blogger_faltantes"
OUT_DIR.mkdir(exist_ok=True)

CSV_OK = OUT_DIR / "descargadas_y_reemplazadas.csv"
CSV_FAIL = OUT_DIR / "fallidas.csv"
TXT_RESUMEN = OUT_DIR / "resumen.txt"

TIMEOUT = 45


def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def safe_ext_from_url_or_type(url: str, content_type: str | None):
    # 1) intentar por content-type
    if content_type:
        content_type = content_type.split(";")[0].strip().lower()
        ext = mimetypes.guess_extension(content_type)
        if ext:
            if ext == ".jpe":
                ext = ".jpg"
            return ext

    # 2) intentar por URL
    m = re.search(r"\.([A-Za-z0-9]{2,5})(?:$|[?#])", url)
    if m:
        ext = "." + m.group(1).lower()
        if ext in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg"]:
            return ext

    return ".jpg"


def hashed_upload_path(url: str, ext: str) -> Path:
    h = hashlib.sha256(url.encode("utf-8")).hexdigest()
    sub1 = h[:2]
    sub2 = h[2:4]
    filename = f"{h}{ext}"
    return STATIC_UPLOADS / sub1 / sub2 / filename


def slug_to_md_path(md_file_field: str) -> Path:
    # viene como content/posts/xxxx.md
    return ROOT / md_file_field


def is_image_response(content_type: str | None, url: str) -> bool:
    if content_type:
        c = content_type.lower()
        if c.startswith("image/"):
            return True
    # fallback por extensión
    return bool(re.search(r"\.(jpg|jpeg|png|gif|webp|bmp|svg)(?:$|[?#])", url, re.I))


def download_file(url: str):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        }
    )

    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        final_url = resp.geturl()
        content_type = resp.headers.get("Content-Type", "")
        data = resp.read()
        return final_url, content_type, data


def replace_in_markdown(md_path: Path, old_url: str, new_url: str) -> bool:
    if not md_path.exists():
        return False

    content = md_path.read_text(encoding="utf-8")
    if old_url not in content:
        return False

    content = content.replace(old_url, new_url)
    md_path.write_text(content, encoding="utf-8")
    return True


def main():
    if not CSV_INPUT.exists():
        print(f"[ERROR] No existe {CSV_INPUT}")
        sys.exit(1)

    ensure_dir(STATIC_UPLOADS)

    ok_rows = []
    fail_rows = []

    with CSV_INPUT.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    total = len(rows)

    for i, row in enumerate(rows, start=1):
        html_file = row.get("html_file", "")
        md_file = row.get("md_file", "")
        old_url = row.get("old_url", "")

        print(f"[{i}/{total}] Probando: {old_url}")

        md_path = slug_to_md_path(md_file)

        try:
            final_url, content_type, data = download_file(old_url)

            if not is_image_response(content_type, final_url):
                fail_rows.append({
                    "html_file": html_file,
                    "md_file": md_file,
                    "old_url": old_url,
                    "motivo": f"non_image ({content_type})"
                })
                print("   -> no es imagen")
                continue

            ext = safe_ext_from_url_or_type(final_url, content_type)
            local_path = hashed_upload_path(old_url, ext)
            ensure_dir(local_path.parent)
            local_path.write_bytes(data)

            new_url = "/" + local_path.relative_to(STATIC_UPLOADS.parent).as_posix()

            replaced = replace_in_markdown(md_path, old_url, new_url)
            if not replaced:
                fail_rows.append({
                    "html_file": html_file,
                    "md_file": md_file,
                    "old_url": old_url,
                    "motivo": "descargada_pero_no_reemplazada_en_markdown"
                })
                print("   -> descargada pero no se encontró la URL en el markdown")
                continue

            ok_rows.append({
                "html_file": html_file,
                "md_file": md_file,
                "old_url": old_url,
                "new_url": new_url,
                "content_type": content_type,
                "bytes": len(data),
            })
            print(f"   -> OK {new_url}")

        except urllib.error.HTTPError as e:
            fail_rows.append({
                "html_file": html_file,
                "md_file": md_file,
                "old_url": old_url,
                "motivo": f"http_error_{e.code}"
            })
            print(f"   -> HTTP {e.code}")

        except urllib.error.URLError as e:
            fail_rows.append({
                "html_file": html_file,
                "md_file": md_file,
                "old_url": old_url,
                "motivo": f"url_error_{e.reason}"
            })
            print(f"   -> URL error: {e.reason}")

        except Exception as e:
            fail_rows.append({
                "html_file": html_file,
                "md_file": md_file,
                "old_url": old_url,
                "motivo": f"error_{type(e).__name__}: {e}"
            })
            print(f"   -> ERROR: {e}")

        time.sleep(0.3)

    # guardar CSV ok
    with CSV_OK.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["html_file", "md_file", "old_url", "new_url", "content_type", "bytes"]
        )
        writer.writeheader()
        writer.writerows(ok_rows)

    # guardar CSV fail
    with CSV_FAIL.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["html_file", "md_file", "old_url", "motivo"]
        )
        writer.writeheader()
        writer.writerows(fail_rows)

    resumen = []
    resumen.append("RESUMEN DESCARGA BLOGGER FALTANTES")
    resumen.append("=" * 60)
    resumen.append(f"URLs intentadas: {len(rows)}")
    resumen.append(f"Descargadas y reemplazadas: {len(ok_rows)}")
    resumen.append(f"Fallidas: {len(fail_rows)}")
    resumen.append("")
    resumen.append(f"CSV OK: {CSV_OK}")
    resumen.append(f"CSV fallidas: {CSV_FAIL}")

    TXT_RESUMEN.write_text("\n".join(resumen), encoding="utf-8")

    print("")
    print("[OK] Proceso completado")
    print(f"  - {CSV_OK}")
    print(f"  - {CSV_FAIL}")
    print(f"  - {TXT_RESUMEN}")


if __name__ == "__main__":
    main()
