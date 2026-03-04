# VRChat Gallery - GitHub Pages

Sistema de galeria de imagenes para VRChat. Las fotos se sirven desde GitHub Pages
y se cargan automaticamente en los marcos del mundo.

## Setup Rapido

### 1. Crear el repositorio en GitHub

1. Crea un nuevo repositorio: `tu-usuario/vrchat-gallery`
2. Copia TODO el contenido de esta carpeta (`GitHubPages/`) a la raiz del nuevo repo
3. Asegurate de que la estructura quede asi:

```
vrchat-gallery/           <- raiz del repo
├── .github/
│   └── workflows/
│       └── update-gallery.yml
├── scripts/
│   └── update_gallery.py
├── groupA/               <- fotos del grupo A
├── groupB/               <- fotos del grupo B
├── gallery-index.json    <- se genera automaticamente
└── README.md
```

### 2. Activar GitHub Pages

1. Ve a Settings > Pages en tu repositorio
2. Source: "Deploy from a branch"
3. Branch: `main`, carpeta: `/ (root)`
4. Guarda. Tu sitio estara en: `https://tu-usuario.github.io/vrchat-gallery/`

### 3. Subir fotos

Simplemente sube imagenes (JPG, PNG, WEBP) a las carpetas `groupA/` y `groupB/`.

El workflow de GitHub Actions automaticamente:
- Renombra las fotos a `foto_001.jpg`, `foto_002.jpg`... (orden alfabetico)
- Redimensiona imagenes mayores a 2048x2048 (limite de VRChat)
- Convierte todo a JPG
- Actualiza `gallery-index.json` con el conteo

### 4. Configurar en Unity

1. En tu mundo de VRChat, busca el GameObject **GalleryManager**
2. En el campo `Index Url`, pon: `https://tu-usuario.github.io/vrchat-gallery/gallery-index.json`
3. En cada **GalleryGroup**:
   - Pon la URL base correcta (ej: `https://tu-usuario.github.io/vrchat-gallery/groupA/foto_`)
   - Haz click en "Generar URLs" en el Inspector
4. Sube el mundo a VRChat

## Limites de VRChat

| Limite | Valor |
|--------|-------|
| Resolucion maxima | 2048 x 2048 px |
| Tamano maximo | 32 MB por imagen |
| Rate limit | 1 imagen cada 5 segundos (global) |
| Dominios confiables | *.github.io esta permitido |

## Agregar mas fotos

1. Sube las fotos nuevas a `groupA/` o `groupB/` (cualquier nombre)
2. Haz push a `main`
3. El workflow las renombra automaticamente
4. Los marcos en VRChat las mostraran en el siguiente ciclo (~5 min)

## Notas

- Maximo recomendado: 50 fotos por grupo
- Las fotos se muestran en orden secuencial
- Cada marco cambia de foto cada 5 minutos (configurable)
- El cambio es sincronizado: todos los jugadores ven la misma foto
