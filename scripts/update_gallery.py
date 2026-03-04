"""
Script para actualizar la galeria de imagenes.

Funciones:
1. Escanea carpetas groupA/ y groupB/ en busca de imagenes
2. Renombra las imagenes al formato secuencial foto_001.jpg, foto_002.jpg...
3. Redimensiona imagenes mayores a 2048x2048 (limite de VRChat)
4. Genera gallery-index.json con el conteo por grupo

Ejecutar: python scripts/update_gallery.py
"""

import os
import json
import shutil
from pathlib import Path

# Intentar importar Pillow para redimensionar
try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False
    print("AVISO: Pillow no instalado. No se redimensionaran imagenes.")
    print("       Instalar con: pip install Pillow")

# Configuracion
GROUPS = ["groupA", "groupB"]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
MAX_DIMENSION = 2048  # Limite de VRChat
JPEG_QUALITY = 85
ROOT_DIR = Path(__file__).parent.parent  # Sube de scripts/ a la raiz


def get_image_files(group_dir):
    """Obtiene lista de archivos de imagen en un directorio, ordenados alfabeticamente."""
    files = []
    if not group_dir.exists():
        group_dir.mkdir(parents=True, exist_ok=True)
        print(f"  Creada carpeta: {group_dir}")
        return files

    for f in sorted(group_dir.iterdir()):
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS:
            files.append(f)
    return files


def resize_if_needed(filepath):
    """Redimensiona la imagen si excede 2048x2048. Retorna True si fue modificada."""
    if not HAS_PILLOW:
        return False

    try:
        with Image.open(filepath) as img:
            w, h = img.size
            if w <= MAX_DIMENSION and h <= MAX_DIMENSION:
                return False

            # Calcular nuevo tamano manteniendo proporcion
            ratio = min(MAX_DIMENSION / w, MAX_DIMENSION / h)
            new_w = int(w * ratio)
            new_h = int(h * ratio)

            print(f"  Redimensionando {filepath.name}: {w}x{h} -> {new_w}x{new_h}")

            img_resized = img.resize((new_w, new_h), Image.LANCZOS)

            # Convertir a RGB si tiene alpha (JPEG no soporta alpha)
            if img_resized.mode in ("RGBA", "P"):
                img_resized = img_resized.convert("RGB")

            img_resized.save(filepath, "JPEG", quality=JPEG_QUALITY)
            return True
    except Exception as e:
        print(f"  ERROR redimensionando {filepath.name}: {e}")
        return False


def convert_to_jpg(filepath):
    """Convierte imagen a JPG si no lo es. Retorna la nueva ruta."""
    if filepath.suffix.lower() in (".jpg", ".jpeg"):
        return filepath

    if not HAS_PILLOW:
        return filepath

    try:
        new_path = filepath.with_suffix(".jpg")
        with Image.open(filepath) as img:
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(new_path, "JPEG", quality=JPEG_QUALITY)

        # Eliminar el original si la conversion fue exitosa
        filepath.unlink()
        print(f"  Convertido {filepath.name} -> {new_path.name}")
        return new_path
    except Exception as e:
        print(f"  ERROR convirtiendo {filepath.name}: {e}")
        return filepath


def rename_photos(group_dir):
    """
    Renombra las fotos al formato foto_001.jpg, foto_002.jpg...
    Retorna la cantidad de fotos procesadas.
    """
    files = get_image_files(group_dir)
    if not files:
        print(f"  Sin imagenes en {group_dir.name}/")
        return 0

    print(f"  Encontradas {len(files)} imagenes en {group_dir.name}/")

    # Fase 1: Convertir todo a JPG
    converted_files = []
    for f in files:
        converted = convert_to_jpg(f)
        converted_files.append(converted)

    # Fase 2: Re-escanear despues de conversiones
    converted_files = get_image_files(group_dir)

    # Fase 3: Renombrar a formato temporal para evitar colisiones
    temp_files = []
    for i, f in enumerate(converted_files):
        temp_name = group_dir / f"_temp_{i:03d}.jpg"
        if f != temp_name:
            shutil.move(str(f), str(temp_name))
        temp_files.append(temp_name)

    # Fase 4: Renombrar al formato final
    count = 0
    for i, temp_f in enumerate(temp_files):
        final_name = group_dir / f"foto_{i + 1:03d}.jpg"
        shutil.move(str(temp_f), str(final_name))

        # Redimensionar si es necesario
        resize_if_needed(final_name)
        count += 1

    return count


def generate_index(group_counts):
    """Genera el archivo gallery-index.json."""
    index = {}
    for group_name, count in group_counts.items():
        index[group_name] = {"count": count}

    index_path = ROOT_DIR / "gallery-index.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"\nGenerado gallery-index.json: {json.dumps(index, indent=2)}")


def main():
    print("=" * 50)
    print("Actualizando galeria de imagenes")
    print("=" * 50)

    group_counts = {}

    for group_name in GROUPS:
        group_dir = ROOT_DIR / group_name
        print(f"\nProcesando {group_name}/...")
        count = rename_photos(group_dir)
        group_counts[group_name] = count
        print(f"  Total: {count} fotos")

    generate_index(group_counts)

    print("\nProceso completado.")


if __name__ == "__main__":
    main()
