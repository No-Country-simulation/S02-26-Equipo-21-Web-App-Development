-- Tabla: videos_generados
CREATE TABLE videos_generados (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    video_original_id BIGINT NOT NULL,
    nombre_archivo VARCHAR(255) NOT NULL,
    tipo_salida ENUM('short', 'completo_vertical', 'todos') NOT NULL,
    duracion_segundos INT UNSIGNED NULL,
    resolucion VARCHAR(20) NULL,
    ruta_archivo VARCHAR(500) NOT NULL,
    estado ENUM('generado', 'error') NOT NULL DEFAULT 'generado',
    configuracion_proceso JSON NULL,
    version_modelo_ia VARCHAR(50) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (video_original_id) REFERENCES videos_originales(id) ON DELETE CASCADE
);