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
