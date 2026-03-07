<div align="center">

# S02-26-Equipo-21-Web-App-Development


# Video Shorts Generator

[![ASP.NET Core](https://img.shields.io/badge/ASP.NET_Core-8.0-512BD4?style=flat-square&logo=dotnet)](https://dotnet.microsoft.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=flat-square&logo=typescript)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/Licencia-Académica-green?style=flat-square)](./LICENSE)

No Country · Simulación S02-26 · Equipo 21*

</div>

---

## Sobre el proyecto

Video Shorts Generator es una plataforma que automatiza la conversión de videos horizontales (16:9) al formato vertical (9:16). El usuario sube un video, el sistema lo encola y un motor Python lo convierte a **1080×1920** con fondo negro, codificado en H.264 + AAC. Una vez procesado, puede descargarlo directamente desde la interfaz.

## Características

- Subida de videos con validación en cliente y servidor (tipo, extensión, tamaño)
- Cola de procesamiento asíncrona basada en .NET Background Services
- Motor de conversión Python con MoviePy y FFmpeg
- Monitoreo de estado en tiempo real con polling automático cada 3 segundos
- Historial de videos persistido en `localStorage`
- Interfaz responsiva con tema oscuro
- Notificaciones de estado (éxito, error, advertencia)

---

## Stack Tecnológico

| Área | Tecnología |
|------|-----------|
| Frontend | React 18, Vite, TypeScript, Tailwind CSS, Axios |
| Backend | ASP.NET Core 8, Entity Framework Core, Clean Architecture |
| Procesamiento | Python 3, MoviePy, FFmpeg (libx264 / AAC) |

---

## Requisitos Previos

- [Node.js](https://nodejs.org/) >= 18
- [.NET SDK](https://dotnet.microsoft.com/download) >= 8.0
- [Python](https://www.python.org/) >= 3.9 con `pip install moviepy`

---

## Inicio Rápido

### 1. Clonar el repositorio

```bash
git clone https://github.com/No-Country-simulation/S02-26-Equipo-21-Web-App-Development.git
cd S02-26-Equipo-21-Web-App-Development
```

### 2. Iniciar el Backend

```bash
# Opción A — CLI
dotnet run --project Backend/VideoShortsGenerator.WebApi

# Opción B — Visual Studio 2022
# Abrir Backend/Backend.sln y presionar F5
```

El servidor arranca en `https://localhost:7200`.

### 3. Iniciar el Frontend

```bash
cd Frontend
npm install
cp .env.example .env   # Editar si el backend corre en otro puerto
npm run dev
```

La aplicación abre en `http://localhost:3000`.

> Para instrucciones detalladas, consulta la [Guía de Inicio Rápido](./QUICK_START.md).

---

## Configuración

### Frontend — `Frontend/.env`

```env
# URL de la API del backend
VITE_API_URL=https://localhost:7200/api
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

---

## Endpoints de la API

**Base URL:** `https://localhost:7200/api/videos`

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/videos` | Sube un video para procesar |
| `GET` | `/api/videos/{id}` | Consulta el estado de un video |
| `GET` | `/api/videos/pending` | Lista todos los videos en proceso |
| `GET` | `/api/videos/{id}/download` | Descarga el video procesado |

<details>
<summary>Ver detalle de cada endpoint</summary>

### POST `/api/videos`

Valida y encola un video. Retorna el `id` del job creado.

- **Body:** `multipart/form-data` con campo `file`
- **Extensiones válidas:** `.mp4`, `.mov`, `.avi`, `.mkv`
- **Tamaño máximo:** 150 MB
- **Respuesta exitosa:** `201 Created` → `{ "id": "guid" }`

### GET `/api/videos/{id}`

- **Respuesta exitosa:** `200 OK` → `VideoJobResponse`
- **No encontrado:** `404 Not Found`

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

### GET `/api/videos/pending`

- **Respuesta exitosa:** `200 OK` → Array de `VideoJobResponse`

### GET `/api/videos/{id}/download`

Solo disponible cuando el job está en estado `Completed`.

- **Respuesta exitosa:** `200 OK` → Stream `video/mp4`
- **No disponible:** `404 Not Found`

</details>

---

## Modelo de Datos

### Estados de un Video

```
Pending  ──►  Processing  ──►  Completed
                              └──►  Failed
```

| Estado | Valor | Descripción |
|--------|-------|-------------|
| `Pending` | `0` | En cola, esperando ser procesado |
| `Processing` | `1` | Siendo convertido por el worker |
| `Completed` | `2` | Procesado y disponible para descarga |
| `Failed` | `3` | Error durante el procesamiento |

---

## Estructura del Proyecto

```
.
├── Frontend/
│   └── src/
│       ├── components/         # FileUpload, VideoCard, VideoList, Notification
│       ├── hooks/              # useNotification
│       ├── services/           # api.ts (cliente Axios)
│       ├── types/              # Interfaces TypeScript
│       └── App.tsx             # Componente raíz y estado global
│
└── Backend/
    ├── Backend.sln                                      # Solución con los cuatro proyectos
    │
    ├── VideoShortsGenerator.WebApi/                     # Capa de presentación (entrada HTTP)
    │   ├── Controllers/
    │   │   └── VideosController.cs                      # 4 endpoints REST: POST, GET x3
    │   ├── Properties/
    │   │   └── launchSettings.json                      # Puertos y perfiles de Kestrel
    │   ├── appsettings.json                             # Config de BackgroundWorker y Storage
    │   ├── appsettings.Development.json                 # Overrides para entorno local
    │   └── Program.cs                                   # DI, middleware, CORS y pipeline HTTP
    │
    ├── VideoShortsGenerator.Application/                # Lógica de negocio (sin dependencias de infra)
    │   ├── Abstractions/
    │   │   ├── IVideoStorage.cs                         # Contrato para guardar/leer archivos
    │   │   ├── IVideoProcessor.cs                       # Contrato para procesar videos
    │   │   └── IEventDispatcher.cs                      # Contrato para despachar domain events
    │   ├── DTOs/
    │   │   ├── CreateVideoJobRequest.cs                 # Payload de creación (inputPath)
    │   │   ├── VideoJobResponse.cs                      # Respuesta de estado de un job
    │   │   └── VideoJobListResponse.cs                  # Lista de jobs
    │   ├── Services/
    │   │   ├── VideoJobService.cs                       # Subida, creación de job y descarga
    │   │   └── VideoJobQueryService.cs                  # Consultas: GetById, GetPending
    │   ├── EventHandlers/                               # Manejadores de domain events
    │   └── EventHandling/                               # Dispatcher interno de eventos
    │
    ├── VideoShortsGenerator.Domain/                     # Núcleo del sistema (sin dependencias externas)
    │   ├── Entities/
    │   │   └── VideoJob.cs                              # Agregado raíz con máquina de estados
    │   ├── Enums/
    │   │   └── VideoStatus.cs                           # Pending | Processing | Completed | Failed
    │   ├── Events/                                      # VideoCreatedEvent, VideoCompletedEvent, etc.
    │   └── Repositories/
    │       └── IVideoRepository.cs                      # Interfaz de acceso a datos
    │
    └── VideoShortsGenerator.Infrastructure/             # Adaptadores técnicos (implementan interfaces)
        ├── BackgroundServices/
        │   └── VideoProcessingWorker.cs                 # Hosted Service: poll + procesamiento asíncrono
        ├── VideoProcessing/
        │   ├── PythonVideoProcessor.cs                  # Ejecuta process_video.py via Process.Start()
        │   └── Scripts/
        │       └── process_video.py                     # MoviePy: redimensiona a 1080x1920, H.264 + AAC
        ├── Storage/
        │   └── LocalVideoStorage.cs                     # Guarda y sirve archivos en disco local
        └── Persistence/
            ├── ApplicationDbContext.cs                  # DbContext de Entity Framework Core
            └── VideoRepository.cs                       # Implementación de IVideoRepository
```

---

## Flujo de Procesamiento

```
[Usuario] → Selecciona archivo → FileUpload valida (ext, MIME, tamaño)
         → POST /api/videos → Backend guarda en disco → Crea VideoJob (Pending)
         → VideoProcessingWorker detecta el job (poll cada 5s)
         → Invoca process_video.py → MoviePy convierte a 1080x1920 H.264
         → Job marcado como Completed → Frontend muestra botón "Descargar"
         → GET /api/videos/{id}/download → Archivo descargado
```

## Scripts del Backend

```bash
# Ejecutar en modo desarrollo
dotnet run --project Backend/VideoShortsGenerator.WebApi

# Compilar sin ejecutar
dotnet build Backend/Backend.sln

# Ejecutar en modo producción
dotnet run --project Backend/VideoShortsGenerator.WebApi --configuration Release

# Restaurar dependencias NuGet
dotnet restore Backend/Backend.sln

# Trustar el certificado SSL de desarrollo (solo la primera vez)
dotnet dev-certs https --trust
```

---

## Scripts del Frontend

```bash
npm run dev       # Servidor de desarrollo con HMR
npm run build     # Build de producción (dist/)
npm run preview   # Preview del build de producción
npm run lint      # Linter (próximamente)
```


