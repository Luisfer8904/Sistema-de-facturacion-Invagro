-- =====================================================================
-- Migración: roles de usuario (admin / vendedor)
-- Se ejecuta una sola vez en cada ambiente (local y producción).
-- Es idempotente: si la columna ya existe, no falla.
-- =====================================================================

-- 1) Asegurar que la columna 'rol' exista con los valores correctos
--    (si el modelo SQLAlchemy ya la creó, este ALTER no la duplica)
SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'inva-usuarios'
    AND COLUMN_NAME = 'rol'
);

SET @sql := IF(
  @col_exists = 0,
  "ALTER TABLE `inva-usuarios` ADD COLUMN `rol` ENUM('admin','vendedor','contador') NOT NULL DEFAULT 'vendedor' AFTER `email`",
  "SELECT 'columna rol ya existe' AS info"
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 2) Garantizar que el usuario 'admin' (o quien tengas como primario) sea admin
--    Ajusta el WHERE si tu usuario principal tiene otro nombre.
UPDATE `inva-usuarios`
SET rol = 'admin'
WHERE username = 'admin';

-- 3) Si ningún usuario quedó como admin, promover al primero creado
--    (red de seguridad para no quedarse sin admin)
SET @admin_count := (SELECT COUNT(*) FROM `inva-usuarios` WHERE rol = 'admin');

SET @sql := IF(
  @admin_count = 0,
  "UPDATE `inva-usuarios` SET rol = 'admin' ORDER BY id ASC LIMIT 1",
  "SELECT 'ya hay al menos un admin' AS info"
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 4) Reporte rápido para verificar
SELECT id, username, nombre_completo, rol, activo
FROM `inva-usuarios`
ORDER BY rol, username;
