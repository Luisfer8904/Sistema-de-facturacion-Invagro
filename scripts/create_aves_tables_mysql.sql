CREATE TABLE IF NOT EXISTS `inva_aves_usuarios` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `nombre_completo` VARCHAR(100) NULL,
  `activo` TINYINT(1) DEFAULT 1,
  `fecha_creacion` DATETIME NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_inva_aves_usuarios_username` (`username`)
);

CREATE TABLE IF NOT EXISTS `inva_aves_granja_clientes` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(120) NOT NULL,
  `contacto` VARCHAR(120) NULL,
  `telefono` VARCHAR(30) NULL,
  `email` VARCHAR(120) NULL,
  `direccion` TEXT NULL,
  `observaciones` TEXT NULL,
  `activo` TINYINT(1) DEFAULT 1,
  `fecha_registro` DATETIME NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `inva_aves_lotes` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(120) NOT NULL,
  `encargado` VARCHAR(120) NULL,
  `telefono` VARCHAR(30) NULL,
  `fecha_nacimiento` DATE NOT NULL,
  `plan_nombre` VARCHAR(120) NULL,
  `cantidad_aves` INT DEFAULT 0,
  `observaciones` TEXT NULL,
  `activo` TINYINT(1) DEFAULT 1,
  `fecha_registro` DATETIME NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `inva_aves_lote_actividades` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `lote_id` INT NOT NULL,
  `plan_id` INT NULL,
  `actividad_nombre` VARCHAR(120) NOT NULL,
  `tipo` VARCHAR(30) NOT NULL,
  `edad_dias` INT NOT NULL,
  `fecha_programada` DATE NOT NULL,
  `fecha_realizacion` DATE NOT NULL,
  `comentarios` TEXT NULL,
  `fecha_registro` DATETIME NULL,
  PRIMARY KEY (`id`),
  KEY `idx_inva_aves_lote_actividades_lote_id` (`lote_id`)
);
