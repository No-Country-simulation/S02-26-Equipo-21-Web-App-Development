# Video Shorts Generator - Frontend

Frontend React moderno y eficiente para procesar videos y generar shorts automáticamente.

## 🚀 Características

- ✅ Carga de videos con validación
- ✅ Monitoreo en tiempo real del procesamiento
- ✅ Descarga de videos procesados
- ✅ Interfaz responsive y moderna
- ✅ Sistema de notificaciones
- ✅ Almacenamiento local de historial
- ✅ TypeScript con tipado completo

## 📦 Instalación

```bash
# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env
# Editar .env con la URL correcta del backend
```

## 🔧 Configuración

El frontend espera el backend en `https://localhost:7200/api`. Puedes cambiar esto en `.env`:

```env
VITE_API_URL=https://tu-url:puerto/api
```

## 🏃 Desarrollo

```bash
npm run dev
```

Se abrirá automáticamente en `http://localhost:3000`

## 🔨 Build para Producción

```bash
npm run build
```

Los archivos optimizados quedarán en la carpeta `dist/`.

## 📁 Estructura del Proyecto

```
src/
├── components/          # Componentes React
│   ├── FileUpload.tsx   # Cargar videos
│   ├── VideoCard.tsx    # Tarjeta de video
│   ├── VideoList.tsx    # Lista de videos
│   └── Notification.tsx # Notificaciones
├── services/
│   └── api.ts          # Cliente HTTP (Axios)
├── hooks/
│   └── useNotification.ts
├── types/
│   └── index.ts        # Tipos TypeScript
├── App.tsx             # Componente principal
└── main.tsx            # Punto de entrada
```

## 🎯 Endpoints Consumidos

### POST `/api/videos`

Sube un video para procesamiento

- **Body**: FormData con `file` y `params` (opcional)
- **Response**: `{ id: string }`

### GET `/api/videos/{id}`

Obtiene el estado de un video

- **Response**: `VideoResponse`

### GET `/api/videos/pending`

Obtiene todos los videos pendientes

- **Response**: `VideoResponse[]`

### GET `/api/videos/{id}/download`

Descarga el video procesado

- **Response**: Blob (video/mp4)

## 🎨 Estilos

El diseño es completamente responsive con:

- Gradientes modernos
- Animaciones suaves
- Tema oscuro en fondo
- Interfaz clara y limpia
- Accesibilidad mejorada

## 📱 Responsividad

- Desktop: Grid de 3 columnas
- Tablet: Grid de 2 columnas
- Mobile: 1 columna (100%)

## 🔐 Mejoras de Seguridad

- Validación de archivos (tipo y tamaño)
- HTTPS requerido
- Headers de seguridad
- Error handling completo

## 🚨 Manejo de Errores

- Validaciones del lado del cliente
- Mensajes de error claros
- Retry automático en actualizaciones
- Logging en consola

## 💾 Persistencia

Los videos se guardan en localStorage, permitiendo que la aplicación recuerde el historial incluso después de recargar la página.

## 🔄 Auto-actualización

Los videos en estado "Procesando" o "Pendiente" se actualizan automáticamente cada 3 segundos para mostrar el progreso en tiempo real.

## 📝 Licencia

Proyecto académico - Equipo 21
