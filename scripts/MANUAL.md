# Manual de la Galeria - Como subir fotos

## Carpetas de fotos (fuente)

Las fotos originales van en estas carpetas de tu PC:

- **GroupA:** `C:\Users\emery\OneDrive\Imágenes\GITHUB\GroupA`
- **GroupB:** `C:\Users\emery\OneDrive\Imágenes\GITHUB\GroupB`

Puedes poner fotos con cualquier nombre y formato (PNG, JPG, WEBP, BMP).
El script se encarga de convertir, redimensionar y renombrar todo.

---

## Como subir fotos nuevas

### 1. Agrega las fotos a las carpetas de arriba

### 2. Ejecuta este comando en la terminal (WSL):

```bash
cd /mnt/c/Users/emery/vrchat-gallery && python3 scripts/prepare_photos_local.py && git add -A && git commit -m "Update gallery photos" && git push
```

Eso es todo. El script automaticamente:
- Borra las fotos anteriores del repo
- Convierte todo a JPG 1080px (calidad 85)
- Renombra secuencialmente: foto_001.jpg, foto_002.jpg...
- Actualiza gallery-index.json con los nuevos conteos
- Sube todo a GitHub

---

## Despues de subir (solo si cambio la cantidad de fotos)

Si la cantidad de fotos cambio, ve a Unity:

1. Selecciona el GameObject del **GalleryGroup** (GroupA o GroupB)
2. En el Inspector, ajusta el slider **"Cantidad de URLs"** al nuevo numero
3. Clic en **"Generar URLs"**
4. Guarda la escena

Si solo reemplazaste fotos sin cambiar la cantidad, no necesitas tocar Unity.

---

## Datos utiles

| Dato | Valor |
|------|-------|
| Repo GitHub | https://github.com/emerytheec/vrchat-gallery |
| GitHub Pages | https://emerytheec.github.io/vrchat-gallery/ |
| Repo clonado | `/mnt/c/Users/emery/vrchat-gallery/` |
| Max fotos por grupo | 300 |
| Resolucion final | 1080px max |
| Formato final | JPG calidad 85 |
| Tiempo por foto en VRChat | 150 segundos (2.5 min) |
