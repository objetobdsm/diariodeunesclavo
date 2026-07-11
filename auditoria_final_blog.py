#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import re
from pathlib import Path
from urllib.parse import urlparse

# ============================================================
# CONFIG
# ============================================================

ROOT = Path("/home/gustavo/Escritorio/Descargas/blogger2static/migration_blog").resolve()

CONTENT_DIR = ROOT / "content" / "posts"
PUBLIC_DIR = ROOT / "public"
PUBLIC_POSTS_DIR = PUBLIC_DIR / "posts"
PUBLIC_UPLOADS_DIR = PUBLIC_DIR / "uploads"

OUT_DIR = ROOT / "auditoria_final_blog"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# extensiones que consideraremos "imagen"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".avif"}

# dominios Blogger / Googleusercontent a vigilar
BLOGGER_PATTERNS = [
    "bp.blogspot.com",
    ".bp.blogspot.com",
    "blogspot.com",
    "googleusercontent.com",
    "blogger.googleusercontent.com",
]

# ============================================================
# REGEX
# ============================================================

RE_MD_IMAGE = re.compile(r'!\[[^\]]*\]\(([^)]+)\)')
RE_MD_LINK = re.compile(r'(?<!!)\[[^\]]*\]\(([^)]+)\)')
RE_HTML_SRC = re.compile(r'''(?:src|href)=["']([^"']+)["']''', re.IGNORECASE)
RE_RAW_URL = re.compile(r'https?://[^\s<>"\'()]+')

# ============================================================
# UTILIDADES
# ============================================================

def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except Exception:
        return str(path)

def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")

def list_files(base: Path, suffixes=None):
    if not base.exists():
        return []
    files = [p for p in base.rglob("*") if p.is_file()]
    if suffixes:
        suffixes = {s.lower() for s in suffixes}
        files = [p for p in files if p.suffix.lower() in suffixes]
    return sorted(files)

def clean_url(url: str) -> str:
    url = url.strip()
    # quita título en markdown tipo: (url "title")
    if " " in url and url.startswith(("http://", "https://", "/")):
        url = url.split(" ")[0].strip()
    return url

def is_external_url(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")

def is_blogger_url(url: str) -> bool:
    u = url.lower()
    return any(p in u for p in BLOGGER_PATTERNS)

def is_probable_image_url(url: str) -> bool:
    parsed = urlparse(url)
    path = parsed.path.lower()
    if any(path.endswith(ext) for ext in IMAGE_EXTS):
        return True
    # muchos googleusercontent/blogger no terminan en extensión clara
    if "googleusercontent.com" in url.lower() or "blogspot.com" in url.lower():
        return True
    return False

def find_urls_in_md(text: str):
    urls = []

    for m in RE_MD_IMAGE.finditer(text):
        urls.append(("md_image", clean_url(m.group(1))))

    for m in RE_MD_LINK.finditer(text):
        urls.append(("md_link", clean_url(m.group(1))))

    # URLs crudas
    for m in RE_RAW_URL.finditer(text):
        urls.append(("raw_url", clean_url(m.group(0))))

    return urls

def find_urls_in_html(text: str):
    urls = []
    for m in RE_HTML_SRC.finditer(text):
        urls.append(("html_attr", clean_url(m.group(1))))
    for m in RE_RAW_URL.finditer(text):
        urls.append(("raw_url", clean_url(m.group(0))))
    return urls

def write_csv(path: Path, rows, fieldnames):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)

def write_txt(path: Path, text: str):
    path.write_text(text, encoding="utf-8")

def public_url_to_file(url: str) -> Path:
    """
    Convierte /uploads/x/y.jpg -> ROOT/public/uploads/x/y.jpg
    """
    url = url.strip()
    if not url.startswith("/"):
        return None
    return (PUBLIC_DIR / url.lstrip("/")).resolve()

def html_post_to_md_path(html_post: Path) -> Path:
    """
    public/posts/2020-01-01-slug/index.html -> content/posts/2020-01-01-slug.md
    """
    slug = html_post.parent.name
    return CONTENT_DIR / f"{slug}.md"

# ============================================================
# CARGA DE ARCHIVOS
# ============================================================

md_files = list_files(CONTENT_DIR, {".md"})
html_post_files = [p for p in list_files(PUBLIC_POSTS_DIR, {".html"}) if p.name == "index.html"]
upload_files = list_files(PUBLIC_UPLOADS_DIR)

# índices rápidos
upload_rel_set = set(rel(p) for p in upload_files)
upload_abs_set = set(p.resolve() for p in upload_files)

# ============================================================
# AUDITORÍAS
# ============================================================

external_in_content = []
blogger_in_content = []
posts_without_images = []
broken_local_images_in_md = []
md_without_public_html = []

external_in_public = []
blogger_in_public = []
public_without_md = []
uploads_orphans = []

# para detectar referencias a uploads
referenced_upload_paths = set()

# ------------------------------------------------------------
# 1) AUDITORÍA DE CONTENT/POSTS (*.md)
# ------------------------------------------------------------
for md in md_files:
    text = read_text(md)
    urls = find_urls_in_md(text)

    image_count = 0
    seen_local_images = set()

    for kind, url in urls:
        if not url:
            continue

        # EXTERNAS
        if is_external_url(url):
            row = {
                "md_file": rel(md),
                "kind": kind,
                "url": url,
            }
            external_in_content.append(row)
            if is_blogger_url(url):
                blogger_in_content.append(row)

            if kind == "md_image" or is_probable_image_url(url):
                image_count += 1
            continue

        # LOCALES
        if kind == "md_image":
            image_count += 1

            # solo auditamos /uploads/...
            if url.startswith("/uploads/"):
                target = public_url_to_file(url)
                if target is None or not target.exists():
                    broken_local_images_in_md.append({
                        "md_file": rel(md),
                        "image_url": url,
                        "expected_file": rel(target) if target else "",
                        "motivo": "archivo_local_no_existe_en_public",
                    })
                else:
                    referenced_upload_paths.add(target.resolve())
                    seen_local_images.add(target.resolve())

    if image_count == 0:
        posts_without_images.append({
            "md_file": rel(md),
        })

    # md -> html esperado
    expected_html = PUBLIC_POSTS_DIR / md.stem / "index.html"
    if not expected_html.exists():
        md_without_public_html.append({
            "md_file": rel(md),
            "expected_html": rel(expected_html),
        })

# ------------------------------------------------------------
# 2) AUDITORÍA DE PUBLIC/POSTS (index.html)
# ------------------------------------------------------------
for html in html_post_files:
    text = read_text(html)
    urls = find_urls_in_html(text)

    for kind, url in urls:
        if not url:
            continue

        if is_external_url(url):
            row = {
                "html_file": rel(html),
                "kind": kind,
                "url": url,
            }
            external_in_public.append(row)
            if is_blogger_url(url):
                blogger_in_public.append(row)

        # referencias locales a uploads desde el HTML
        if url.startswith("/uploads/"):
            target = public_url_to_file(url)
            if target and target.exists():
                referenced_upload_paths.add(target.resolve())

    # html -> md esperado
    expected_md = html_post_to_md_path(html)
    if not expected_md.exists():
        public_without_md.append({
            "html_file": rel(html),
            "expected_md": rel(expected_md),
        })

# ------------------------------------------------------------
# 3) UPLOADS HUÉRFANOS
# ------------------------------------------------------------
for up in upload_files:
    if up.resolve() not in referenced_upload_paths:
        uploads_orphans.append({
            "upload_file": rel(up),
        })

# ============================================================
# SALIDAS CSV
# ============================================================

write_csv(
    OUT_DIR / "01_external_urls_in_content.csv",
    external_in_content,
    ["md_file", "kind", "url"]
)

write_csv(
    OUT_DIR / "02_blogger_urls_in_content.csv",
    blogger_in_content,
    ["md_file", "kind", "url"]
)

write_csv(
    OUT_DIR / "03_posts_without_images.csv",
    posts_without_images,
    ["md_file"]
)

write_csv(
    OUT_DIR / "04_broken_local_images_in_md.csv",
    broken_local_images_in_md,
    ["md_file", "image_url", "expected_file", "motivo"]
)

write_csv(
    OUT_DIR / "05_md_without_public_html.csv",
    md_without_public_html,
    ["md_file", "expected_html"]
)

write_csv(
    OUT_DIR / "06_external_urls_in_public.csv",
    external_in_public,
    ["html_file", "kind", "url"]
)

write_csv(
    OUT_DIR / "07_blogger_urls_in_public.csv",
    blogger_in_public,
    ["html_file", "kind", "url"]
)

write_csv(
    OUT_DIR / "08_public_without_md.csv",
    public_without_md,
    ["html_file", "expected_md"]
)

write_csv(
    OUT_DIR / "09_uploads_orphans.csv",
    uploads_orphans,
    ["upload_file"]
)

# ============================================================
# RESUMEN TXT
# ============================================================

summary = []
summary.append("AUDITORÍA FINAL BLOG MIGRADO")
summary.append("=" * 72)
summary.append(f"ROOT: {ROOT}")
summary.append("")
summary.append("CONTEOS")
summary.append("-" * 72)
summary.append(f"Markdown posts analizados:           {len(md_files)}")
summary.append(f"HTML públicos analizados:            {len(html_post_files)}")
summary.append(f"Uploads analizados:                  {len(upload_files)}")
summary.append("")
summary.append(f"URLs externas en content/:           {len(external_in_content)}")
summary.append(f"URLs Blogger/Google en content/:     {len(blogger_in_content)}")
summary.append(f"Posts sin imágenes:                  {len(posts_without_images)}")
summary.append(f"Imágenes locales rotas en MD:        {len(broken_local_images_in_md)}")
summary.append(f"MD sin HTML generado:                {len(md_without_public_html)}")
summary.append("")
summary.append(f"URLs externas en public/:            {len(external_in_public)}")
summary.append(f"URLs Blogger/Google en public/:      {len(blogger_in_public)}")
summary.append(f"HTML públicos sin MD origen:         {len(public_without_md)}")
summary.append(f"Uploads huérfanos:                   {len(uploads_orphans)}")
summary.append("")
summary.append("FICHEROS GENERADOS")
summary.append("-" * 72)
summary.append("01_external_urls_in_content.csv")
summary.append("02_blogger_urls_in_content.csv")
summary.append("03_posts_without_images.csv")
summary.append("04_broken_local_images_in_md.csv")
summary.append("05_md_without_public_html.csv")
summary.append("06_external_urls_in_public.csv")
summary.append("07_blogger_urls_in_public.csv")
summary.append("08_public_without_md.csv")
summary.append("09_uploads_orphans.csv")

write_txt(OUT_DIR / "RESUMEN_AUDITORIA_FINAL.txt", "\n".join(summary) + "\n")

print("\n".join(summary))
print()
print(f"Salida en: {OUT_DIR}")
