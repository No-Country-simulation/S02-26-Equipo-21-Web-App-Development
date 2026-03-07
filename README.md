# S02-26-Equipo-21-Web-App-Development

---

## Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Stack Tecnológico](#stack-tecnologico)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Configuración y Variables de Entorno](#configuracion-y-variables-de-entorno)
5. [Inicio Rápido](#inicio-rapido)
6. [Arquitectura del Backend](#arquitectura-del-backend)
7. [Modelo de Dominio](#modelo-de-dominio)
8. [Endpoints de la API](#endpoints-de-la-api)
9. [Arquitectura del Frontend](#arquitectura-del-frontend)
10. [Flujo Completo de un Video](#flujo-completo-de-un-video)
11. [Troubleshooting](#troubleshooting)
12. [Equipo](#equipo)

---

## Requisitos Previos

| Herramienta | Versión mínima | Notas |
| :--- | :--- | :--- |
| Node.js | 18.x o superior | Para el Frontend |
| .NET SDK | 8.0 o superior | Para el Backend |
| Python | 3.9 o superior | Para el motor de procesamiento |
| MoviePy | 1.0.x | `pip install moviepy` |

---

## Stack Tecnológico

### Frontend
| Tecnología | Rol |
| :--- | :--- |
| React 18 + Vite | Framework de UI y bundler |
| TypeScript | Tipado estático |
| Tailwind CSS | Estilizado utilitario |
| Axios | Cliente HTTP con interceptores y timeout |

### Backend (.NET)
| Tecnología | Rol |
| :--- | :--- |
| ASP.NET Core Web API (.NET 8) | Capa de presentación REST |
| Entity Framework Core | Persistencia y ORM |
| .NET Background Services | Cola de procesamiento asíncrona |
| Clean Architecture | Organización por capas (Domain / Application / Infrastructure / WebAPI) |

### Motor de Video
| Tecnología | Rol |
| :--- | :--- |
| Python 3 | Lenguaje del script de conversión |
| MoviePy | Manipulación y exportación de video |
| FFmpeg (libx264 + AAC) | Codificación H.264 para máxima compatibilidad |

---

## Estructura del Proyecto

```text
S02-26-Equipo-21-Web-App-Development/
├── Frontend/                        # Aplicación React
├── Backend/                         # Solución .NET 8
├── QUICK_START.md                   # Guía paso a paso
└── README.md                        # Este archivo
```

### Estructura Detallada del Frontend

```text
Frontend/
├── public/                          # Assets estáticos servidos directamente
├── src/
│   ├── components/                  # Componentes de UI
│   │   ├── FileUpload.tsx           # Drag & drop + validación de archivos
│   │   ├── FileUpload.css           # Estilos del componente de subida
│   │   ├── VideoCard.tsx            # Tarjeta de estado por video (refresco manual)
│   │   ├── VideoCard.css
│   │   ├── VideoList.tsx            # Grid de VideoCards con auto-refresh cada 3s
│   │   ├── VideoList.css
│   │   ├── Notification.tsx         # Toast de feedback (success / error / info / warning)
│   │   ├── Notification.css
│   │   └── index.ts                 # Re-exportaciones barrel
│   ├── hooks/
│   │   └── useNotification.ts       # Hook para centralizar el estado de notificaciones
│   ├── services/
│   │   └── api.ts                   # Cliente Axios + funciones tipadas de la API
│   ├── types/
│   │   └── index.ts                 # Interfaces TypeScript (Video, VideoStatus, etc.)
│   ├── App.tsx                      # Componente raíz: orquesta estado global y lógica
│   ├── App.css
│   ├── main.tsx                     # Punto de entrada (React.StrictMode)
│   ├── index.css                    # Estilos base y Tailwind
│   └── vite-env.d.ts                # Tipos de variables de entorno Vite
├── index.html                       # HTML raíz con div#root
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts                   # Proxy dev configurado a https://localhost:7200
```

### Estructura Detallada del Backend

```text
Backend/
├── Backend.sln                       # Solución con los cuatro proyectos
│
├── VideoShortsGenerator.WebApi/      # Capa de presentación (entrada HTTP)
│   ├── Controllers/
│   │   └── VideosController.cs       # Único controlador — 4 endpoints REST
│   ├── Properties/
│   │   └── launchSettings.json       # Puertos y perfiles de Kestrel
│   ├── appsettings.json              # Configuración principal (BackgroundWorker, Storage)
│   ├── appsettings.Development.json  # Overrides para desarrollo
│   └── Program.cs                    # Registro de DI, middleware y CORS
│
├── VideoShortsGenerator.Application/ # Lógica de negocio pura
│   ├── Abstractions/                 # Interfaces: IVideoStorage, IVideoProcessor, IEventDispatcher
│   ├── DTOs/
│   │   ├── CreateVideoJobRequest.cs  # Payload de creación (inputPath)
│   │   ├── VideoJobResponse.cs       # Respuesta de estado de un job
│   │   └── VideoJobListResponse.cs   # Lista de jobs pendientes
│   ├── Services/
│   │   ├── VideoJobService.cs        # Subida, creación de job y descarga
│   │   └── VideoJobQueryService.cs   # Consultas de estado y listado
│   ├── EventHandlers/                # Manejadores de domain events
│   └── EventHandling/                # Dispatcher de eventos (mediator interno)
│
├── VideoShortsGenerator.Domain/      # Núcleo del sistema — sin dependencias externas
│   ├── Entities/
│   │   └── VideoJob.cs               # Agregado raíz con lógica de estado
│   ├── Enums/
│   │   └── VideoStatus.cs            # Pending | Processing | Completed | Failed
│   ├── Events/                       # Domain Events (VideoCreated, VideoCompleted, etc.)
│   └── Repositories/                 # Interfaz IVideoRepository
│
└── VideoShortsGenerator.Infrastructure/ # Adaptadores técnicos
    ├── BackgroundServices/
    │   └── VideoProcessingWorker.cs   # Hosted Service: poll + procesamiento concurrente
    ├── VideoProcessing/
    │   ├── PythonVideoProcessor.cs    # Llama al script Python via Process.Start()
    │   └── Scripts/
    │       └── process_video.py       # Conversión con MoviePy (1080x1920, H.264, AAC)
    ├── Storage/
    │   └── LocalVideoStorage.cs       # Guarda y lee archivos en disco local
    └── Persistence/
        ├── ApplicationDbContext.cs    # DbContext de EF Core
        └── VideoRepository.cs        # Implementación de IVideoRepository
```

---

## Configuración y Variables de Entorno

### Frontend — `Frontend/.env`

```env
# URL base de la API del backend (sin trailing slash)
VITE_API_URL=https://localhost:7200/api
```

Si el archivo no existe, el cliente Axios apunta por defecto a `http://localhost:5273/api`. Copia el ejemplo con:

```bash
cd Frontend
copy .env.example .env
```

### Backend — `appsettings.json`

```json
{
  "BackgroundWorker": {
    "PollingIntervalSeconds": 5,
    "MaxConcurrentJobs": 1
  }
}
```

| Clave | Descripción | Defecto |
| :--- | :--- | :--- |
| `PollingIntervalSeconds` | Cada cuántos segundos el worker busca jobs pendientes | `5` |
| `MaxConcurrentJobs` | Máximo de videos procesados en paralelo | `1` |

---

## Inicio Rápido

### 1. Frontend

```bash
cd Frontend
npm install        # Instala dependencias
npm run dev        # Servidor de desarrollo en http://localhost:3000
```

Scripts disponibles:

```bash
npm run dev        # Desarrollo con Hot Module Replacement
npm run build      # Build de producción (salida en dist/)
npm run preview    # Preview del build de producción
```

### 2. Backend

```bash
# Opción A — Visual Studio 2022
# Abrir Backend/Backend.sln y presionar F5

# Opción B — CLI
dotnet run --project Backend/VideoShortsGenerator.WebApi
```

El backend arranca en `https://localhost:7200` en modo Development.

### 3. Dependencias de Python

```bash
pip install moviepy
# moviepy instalará FFmpeg automáticamente si no está disponible
```

---

## Arquitectura del Backend

El backend sigue **Clean Architecture** con cuatro capas que respetan la regla de dependencia (las capas externas dependen de las internas, nunca al revés):

```
WebApi  -->  Application  -->  Domain
              |
         Infrastructure  -->  Application (implementa interfaces)
```

### VideoProcessingWorker (Background Service)

El worker es el motor central del sistema. Se ejecuta como un `IHostedService` en paralelo a la API y realiza las siguientes acciones en un bucle:

1. Consulta la base de datos buscando jobs en estado `Pending`.
2. Para cada job encontrado, llama a `IVideoProcessor.ProcessAsync()` (que ejecuta el script Python).
3. Si el procesamiento es exitoso, guarda el video de salida en disco y marca el job como `Completed`.
4. Si el procesamiento falla, marca el job como `Failed` y registra el error en los logs.
5. Espera `PollingIntervalSeconds` y repite el ciclo.

### PythonVideoProcessor

Invoca `process_video.py` usando `System.Diagnostics.Process`, pasando el path de entrada y el path de salida como argumentos. Captura `stdout` y `stderr` para el logging.

---

## Modelo de Dominio

### Entidad `VideoJob`

| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `Id` | `Guid` | Identificador único generado al crear el job |
| `InputPath` | `string` | Ruta en disco del archivo de video original |
| `OutputPath` | `string?` | Ruta en disco del video procesado (null hasta completar) |
| `Status` | `VideoStatus` | Estado actual del job |
| `CreatedAt` | `DateTime` | Timestamp UTC de creación |
| `CompletedAt` | `DateTime?` | Timestamp UTC de finalización (completado o fallido) |

### Enum `VideoStatus`

| Valor | Código | Descripción |
| :--- | :--- | :--- |
| `Pending` | `0` | Esperando ser tomado por el worker |
| `Processing` | `1` | Siendo procesado activamente |
| `Completed` | `2` | Video procesado y disponible para descarga |
| `Failed` | `3` | El procesamiento falló |

### Domain Events

La entidad `VideoJob` emite eventos de dominio en cada transición de estado:

| Evento | Cuándo se emite |
| :--- | :--- |
| `VideoCreatedEvent` | Al crear un nuevo job |
| `VideoProcessingStartedEvent` | Al llamar a `MarkAsProcessing()` |
| `VideoCompletedEvent` | Al llamar a `MarkAsCompleted(outputPath)` |
| `VideoFailedEvent` | Al llamar a `MarkAsFailed()` |

### DTO de Respuesta `VideoJobResponse`

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "inputPath": "uploads/original/abc123.mp4",
  "outputPath": "uploads/processed/3fa85f64.mp4",
  "status": "Completed",
  "createdAt": "2026-03-06T20:00:00Z",
  "completedAt": "2026-03-06T20:01:30Z"
}
```

---

## Endpoints de la API

**Base URL:** `https://localhost:7200/api/videos`

---

### POST `/api/videos` — Subir video

Valida y encola un video para procesamiento. Retorna el ID del job creado.

**Request:**
- Content-Type: `multipart/form-data`
- Body: campo `file` con el archivo de video

**Restricciones de validación:**

| Regla | Valor |
| :--- | :--- |
| Extensiones permitidas | `.mp4`, `.mov`, `.avi`, `.mkv` |
| MIME types permitidos | `video/mp4`, `video/quicktime`, `video/x-msvideo`, `video/x-matroska` |
| Tamaño máximo | 150 MB |

**Respuestas:**

| Código | Descripción |
| :--- | :--- |
| `201 Created` | Job creado. Body: `{ "id": "guid" }` |
| `400 Bad Request` | Archivo faltante, tipo inválido o excede el tamaño |

---

### GET `/api/videos/{id}` — Consultar estado de un video

Retorna el estado actual y los metadatos de un job específico.

**Parámetros de ruta:**

| Parámetro | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | `Guid` | ID del job devuelto al momento de la subida |

**Respuestas:**

| Código | Descripción |
| :--- | :--- |
| `200 OK` | Body: `VideoJobResponse` con el estado actual |
| `404 Not Found` | No existe un job con ese ID |

---

### GET `/api/videos/pending` — Listar videos pendientes

Retorna todos los jobs que aún no han sido completados ni fallaron. Útil para restaurar el estado del frontend tras recargar la página.

**Respuestas:**

| Código | Descripción |
| :--- | :--- |
| `200 OK` | Body: array de `VideoJobResponse` (puede estar vacío `[]`) |

---

### GET `/api/videos/{id}/download` — Descargar video procesado

Descarga el archivo MP4 de salida. Solo funciona si el job está en estado `Completed`.

**Parámetros de ruta:**

| Parámetro | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | `Guid` | ID del job completado |

**Respuestas:**

| Código | Descripción |
| :--- | :--- |
| `200 OK` | Body: stream binario `video/mp4`, Content-Disposition: `video_{id}.mp4` |
| `404 Not Found` | El job no existe o no está en estado `Completed` |

---

## Arquitectura del Frontend

### Tipos TypeScript (`src/types/index.ts`)

```typescript
type VideoStatus = 'Pending' | 'Processing' | 'Completed' | 'Failed';

interface Video {
  id: string;
  fileName: string;
  status: VideoStatus;
  createdAt: string;
  completedAt?: string;
  errorMessage?: string;
  progress?: number;
}

interface NotificationState {
  id?: string;
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
}
```

### Cliente de la API (`src/services/api.ts`)

El cliente Axios está configurado con un timeout de 30 segundos. Expone cuatro funciones:

| Función | Método | Endpoint | Retorna |
| :--- | :--- | :--- | :--- |
| `uploadVideo(file, params?)` | POST | `/videos` | `Promise<string>` (id) |
| `getVideoById(id)` | GET | `/videos/{id}` | `Promise<VideoResponse>` |
| `getPendingVideos()` | GET | `/videos/pending` | `Promise<VideoResponse[]>` |
| `downloadVideo(id)` | GET | `/videos/{id}/download` | `Promise<Blob>` |

### Componentes Principales

| Componente | Responsabilidad |
| :--- | :--- |
| `App.tsx` | Estado global (`videos[]`, `notification`), lógica de subida, refresco y persistencia en `localStorage` |
| `FileUpload.tsx` | Drag & drop o click para seleccionar. Valida extensión, MIME type y tamaño (150MB) antes de llamar a la API |
| `VideoList.tsx` | Renderiza el grid de `VideoCard`. Activa un interval de 3s para refrescar jobs en estado `Pending` o `Processing` |
| `VideoCard.tsx` | Muestra estado, timestamps y botón de descarga (solo visible en `Completed`). Botón de refresco manual |
| `Notification.tsx` | Toast que se cierra automáticamente a los 5 segundos |

### Persistencia local

El array `videos` se sincroniza con `localStorage` en cada cambio mediante un `useEffect`. Al montar la app, se carga el historial previo, permitiendo que el usuario vea sus videos anteriores sin necesidad de hacer login.

---

## Flujo Completo de un Video

```
Usuario selecciona archivo
        |
        v
FileUpload.tsx valida (extensión, MIME, tamaño)
        |
        v
POST /api/videos  (FormData con el archivo)
        |
        v
VideosController.cs valida nuevamente en el servidor
        |
        v
VideoJobService.VideoUploadAsync()
    1. Guarda el archivo en disco (LocalVideoStorage)
    2. Crea entidad VideoJob (Status = Pending)
    3. Persiste en base de datos (EF Core)
    4. Emite VideoCreatedEvent
        |
        v
Retorna 201 Created con { id: "guid" }
        |
        v
Frontend agrega el video a la lista con status "Pending"
VideoList activa el auto-refresh cada 3s
        |
        v
VideoProcessingWorker (Background Service)
    1. Detecta el job en la cola (poll cada 5s)
    2. Llama a PythonVideoProcessor.ProcessAsync()
    3. Python redimensiona a 1080x1920, centra en fondo negro
    4. Exporta con libx264 / AAC a 30fps
    5. Guarda el output en disco
    6. Marca el job como Completed
        |
        v
Frontend detecta el cambio de estado en el próximo poll
VideoCard muestra el botón "Descargar"
        |
        v
GET /api/videos/{id}/download
        |
        v
Archivo MP4 descargado al dispositivo del usuario
```

---

## Troubleshooting

### No se puede conectar al backend

- Verifica que el proyecto `VideoShortsGenerator.WebApi` esté corriendo.
- Confirma que la URL en `Frontend/.env` coincida con el puerto del backend (por defecto `https://localhost:7200`).
- En desarrollo, el certificado SSL de Kestrel es self-signed — ignora la advertencia del navegador o ejecuta `dotnet dev-certs https --trust`.

### Error de CORS

- El backend debe tener el origen del frontend en su política CORS configurada en `Program.cs`.
- En desarrollo, el Vite proxy de `vite.config.ts` puede evitar el problema enrutando las llamadas a la API.

### El video no sube

- Verifica que el archivo no supere los 150 MB.
- Formatos aceptados: `.mp4`, `.mov`, `.avi`, `.mkv`.
- Abre la consola del navegador (F12) para ver el error exacto de Axios.

### El video queda siempre en "Procesando"

- Verifica que Python esté instalado y accesible desde la línea de comandos (`python --version`).
- Verifica que `moviepy` esté instalado (`pip show moviepy`).
- Revisa los logs del backend — el `VideoProcessingWorker` registra cada paso del procesamiento.

### Responsive Design

| Breakpoint | Layout |
| :--- | :--- |
| Desktop (> 1024px) | Grid de 3 columnas |
| Tablet (768px–1024px) | Grid de 2 columnas |
| Mobile (< 768px) | 1 columna (100%) |


*Hecho para creadores de contenido.*

