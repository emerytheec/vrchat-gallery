"""
Script para preparar fotos localmente antes de subir a GitHub.

Funciones:
1. Lee imagenes desde carpetas fuente (OneDrive, etc.)
2. Convierte todo a JPG
3. Redimensiona a maximo 1080px (manteniendo proporcion)
4. Nombra secuencialmente: foto_001.jpg, foto_002.jpg...
5. Las coloca en las carpetas destino del repositorio
6. Genera gallery-index.json actualizado

Ejecutar desde la raiz del repositorio vrchat-gallery:
  python scripts/prepare_photos_local.py
"""

import os
import sys
import json
import shutil
from pathlib import Path

try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False
    print("ERROR: Pillow es necesario para este script.")
    print("       Instalar con: pip install Pillow")
    sys.exit(1)

# ============================================================
# CONFIGURACION - Editar estas rutas segun tu PC
# ============================================================

# Carpetas fuente (donde tienes las fotos originales)
SOURCE_FOLDERS = {
    "groupA": Path("/mnt/c/Users/emery/OneDrive/Imágenes/GITHUB/GroupA"),
    "groupB": Path("/mnt/c/Users/emery/OneDrive/Imágenes/GITHUB/GroupB"),
}

# Carpeta raiz del repositorio (donde se ejecuta el script)
REPO_ROOT = Path(__file__).parent.parent

# ============================================================
# PARAMETROS DE CONVERSION
# ============================================================

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tif"}
MAX_DIMENSION = 1080  # Redimensionar a 1080px maximo
JPEG_QUALITY = 85     # Calidad de compresion JPG (85 = buen balance)


def get_source_images(source_dir):
    """Obtiene lista de archivos de imagen en la carpeta fuente, ordenados por nombre."""
    if not source_dir.exists():
        print(f"  ADVERTENCIA: Carpeta no encontrada: {source_dir}")
        return []

    files = []
    for f in sorted(source_dir.iterdir()):
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS:
            files.append(f)
    return files


def convert_and_resize(source_path, dest_path):
    """
    Convierte una imagen a JPG redimensionada.
    Retorna (exito, tamano_original, tamano_final, resolucion_original, resolucion_final).
    """
    try:
        with Image.open(source_path) as img:
            orig_w, orig_h = img.size
            orig_size = source_path.stat().st_size

            # Convertir a RGB si tiene alpha
            if img.mode in ("RGBA", "P", "LA", "PA"):
                img = img.convert("RGB")
            elif img.mode != "RGB":
                img = img.convert("RGB")

            # Redimensionar si excede MAX_DIMENSION
            new_w, new_h = orig_w, orig_h
            if orig_w > MAX_DIMENSION or orig_h > MAX_DIMENSION:
                ratio = min(MAX_DIMENSION / orig_w, MAX_DIMENSION / orig_h)
                new_w = int(orig_w * ratio)
                new_h = int(orig_h * ratio)
                img = img.resize((new_w, new_h), Image.LANCZOS)

            # Guardar como JPG
            img.save(dest_path, "JPEG", quality=JPEG_QUALITY, optimize=True)
            final_size = dest_path.stat().st_size

            return True, orig_size, final_size, (orig_w, orig_h), (new_w, new_h)

    except Exception as e:
        print(f"  ERROR procesando {source_path.name}: {e}")
        return False, 0, 0, (0, 0), (0, 0)


def clean_destination(dest_dir):
    """Limpia la carpeta destino, conservando .gitkeep."""
    if not dest_dir.exists():
        dest_dir.mkdir(parents=True, exist_ok=True)
        return 0

    removed = 0
    for f in dest_dir.iterdir():
        if f.name == ".gitkeep":
            continue
        if f.is_file():
            f.unlink()
            removed += 1
    return removed


def process_group(group_name, source_dir):
    """Procesa un grupo completo: limpia destino, convierte y copia fotos."""
    dest_dir = REPO_ROOT / group_name
    print(f"\n{'='*60}")
    print(f"Procesando {group_name}")
    print(f"{'='*60}")
    print(f"  Fuente:  {source_dir}")
    print(f"  Destino: {dest_dir}")

    # Obtener fotos fuente
    source_files = get_source_images(source_dir)
    if not source_files:
        print(f"  Sin imagenes en la carpeta fuente!")
        return 0

    print(f"  Encontradas {len(source_files)} imagenes")

    # Limpiar destino
    removed = clean_destination(dest_dir)
    if removed > 0:
        print(f"  Eliminadas {removed} fotos anteriores del destino")

    # Procesar cada foto
    total_orig_size = 0
    total_final_size = 0
    count = 0
    errors = 0
    resized_count = 0

    for i, source_file in enumerate(source_files):
        number = (i + 1)
        dest_name = f"foto_{number:03d}.jpg"
        dest_path = dest_dir / dest_name

        success, orig_size, final_size, orig_res, final_res = convert_and_resize(
            source_file, dest_path
        )

        if success:
            count += 1
            total_orig_size += orig_size
            total_final_size += final_size

            was_resized = orig_res != final_res
            if was_resized:
                resized_count += 1

            # Mostrar progreso cada 10 fotos o si fue redimensionada
            if (i + 1) % 25 == 0 or was_resized:
                status = f"  [{i+1:3d}/{len(source_files)}] {source_file.name}"
                if was_resized:
                    status += f" ({orig_res[0]}x{orig_res[1]} -> {final_res[0]}x{final_res[1]})"
                size_mb = final_size / (1024 * 1024)
                status += f" -> {dest_name} ({size_mb:.1f} MB)" if size_mb >= 1 else f" -> {dest_name} ({final_size/1024:.0f} KB)"
                print(status)
        else:
            errors += 1

    # Resumen
    orig_mb = total_orig_size / (1024 * 1024)
    final_mb = total_final_size / (1024 * 1024)
    savings = (1 - total_final_size / total_orig_size) * 100 if total_orig_size > 0 else 0

    print(f"\n  Resumen {group_name}:")
    print(f"    Fotos procesadas: {count}")
    print(f"    Errores: {errors}")
    print(f"    Redimensionadas: {resized_count}")
    print(f"    Tamano original:  {orig_mb:.1f} MB")
    print(f"    Tamano final:     {final_mb:.1f} MB")
    print(f"    Ahorro:           {savings:.1f}%")

    return count


def generate_index(group_counts):
    """Genera el archivo gallery-index.json."""
    index = {}
    for group_name, count in group_counts.items():
        index[group_name] = {"count": count}

    index_path = REPO_ROOT / "gallery-index.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"\nGenerado gallery-index.json:")
    print(f"  {json.dumps(index, indent=2)}")


def main():
    print("=" * 60)
    print("Preparacion local de fotos para VRChat Gallery")
    print("=" * 60)
    print(f"Resolucion maxima: {MAX_DIMENSION}px")
    print(f"Calidad JPG: {JPEG_QUALITY}")
    print(f"Repositorio: {REPO_ROOT}")

    # Verificar que estamos en el repo correcto
    if not (REPO_ROOT / "gallery-index.json").exists():
        print("\nERROR: No se encontro gallery-index.json en la raiz del repo.")
        print(f"       Verifica que ejecutas el script desde el repo: {REPO_ROOT}")
        sys.exit(1)

    # Verificar carpetas fuente
    for name, path in SOURCE_FOLDERS.items():
        if not path.exists():
            print(f"\nADVERTENCIA: Carpeta fuente no encontrada: {path}")
            print(f"             El grupo '{name}' sera omitido.")

    group_counts = {}

    for group_name, source_dir in SOURCE_FOLDERS.items():
        count = process_group(group_name, source_dir)
        group_counts[group_name] = count

    # Generar index
    generate_index(group_counts)

    # Resumen final
    total = sum(group_counts.values())
    print(f"\n{'='*60}")
    print(f"COMPLETADO: {total} fotos preparadas en total")
    print(f"{'='*60}")
    print(f"\nSiguientes pasos:")
    print(f"  1. Revisa las fotos en las carpetas destino")
    print(f"  2. git add -A")
    print(f"  3. git commit -m \"Update gallery: {total} photos\"")
    print(f"  4. git push")
    print(f"\nEn Unity:")
    for name, count in group_counts.items():
        print(f"  - {name}: Generar {count} URLs en el Inspector de GalleryGroup")


if __name__ == "__main__":
    main()
