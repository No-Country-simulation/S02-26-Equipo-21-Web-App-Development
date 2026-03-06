# 🚀 Guía de Inicio Rápido

## Paso 1: Instalar dependencias

```bash
cd Frontend
npm install
```

## Paso 2: Configurar variables de entorno

```bash
# Copiar el archivo de ejemplo
copy .env.example .env

# Editar .env si es necesario (por defecto apunta a https://localhost:7200/api)
```

## Paso 3: Iniciar el servidor de desarrollo

```bash
npm run dev
```

La aplicación se abrirá automáticamente en `http://localhost:3000`

## Paso 4: Backend debe estar ejecutándo

Asegúrate que tu backend .NET esté ejecutándose en `https://localhost:7200`

---

## 📋 Funcionalidades Disponibles

### 1. **Cargar Video**

- Haz clic en "Seleccionar Archivo"
- Elige un archivo de video (MP4, MOV, AVI, MKV)
- Máximo 150 MB
- Haz clic en "Subir Video"

### 2. **Monitorear Progreso**

- El estado se actualiza automáticamente cada 3 segundos
- Estados disponibles: Pendiente → Procesando → Completado/Error

### 3. **Descargar Video**

- Una vez completado, aparece el botón "⬇ Descargar"
- Haz clic para descargar el video procesado

### 4. **Cargar Historial**

- Haz clic en "📋 Cargar Videos Pendientes"
- Se cargarán todos los videos en procesamiento

---

## 🔧 Scripts Disponibles

```bash
# Desarrollo con hot reload
npm run dev

# Build para producción
npm run build

# Previsualizar build de producción
npm run preview

# Linter (próximamente)
npm run lint
```

---

## 🌐 Integración Backend

El frontend consume estos endpoints:

| Método | Endpoint                    | Función           |
| ------ | --------------------------- | ----------------- |
| POST   | `/api/videos`               | Subir video       |
| GET    | `/api/videos/{id}`          | Obtener estado    |
| GET    | `/api/videos/pending`       | Videos pendientes |
| GET    | `/api/videos/{id}/download` | Descargar video   |

---

## 🎯 Características Clave

✅ **Validación de Archivos**

- Extensión correcta
- Tamaño máximo 150 MB
- MIME type válido

✅ **Experiencia de Usuario**

- Animaciones suaves
- Notificaciones en tiempo real
- Interfaz responsiva
- Dark theme con gradientes

✅ **Funcionalidad Avanzada**

- Auto-refresh cada 3 segundos (videos en proceso)
- Persistencia con localStorage
- Manejo de errores completo
- TypeScript con tipado total

✅ **Optimización**

- Lazy loading de componentes
- Cancelación de peticiones en desmontaje
- Debouncing de actualizaciones

---

## 🐛 Troubleshooting

### "No se puede conectar al backend"

- Verifica que el backend esté corriendo en `https://localhost:7200`
- Revisa la URL en `.env`
- En desarrollo, el SSL self-signed debería funcionar

### "CORS Error"

- El backend debe permitir solicitudes desde el frontend
- Verifica la configuración CORS del backend

### "El video no se sube"

- Máximo 150 MB
- Formatos permitidos: MP4, MOV, AVI, MKV
- Verifica la conexión a internet

---

## 📱 Responsive Design

- **Desktop**: Grid 3 columnas
- **Tablet**: Grid 2 columnas
- **Mobile**: 1 columna (100%)

---

## 💡 Tips

1. Abre las Developer Tools (F12) para ver los logs
2. Los videos se guardan en localStorage - puedes compartir la URL
3. Las notificaciones desaparecen después de 5 segundos
4. El botón de actualizar (🔄) en cada tarjeta recarga el estado manual

---

Happy coding! 🎬✨
