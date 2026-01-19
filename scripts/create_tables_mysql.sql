-- Script SQL para crear las tablas del Sistema de Facturación Invagro
-- Base de datos: dbapp
-- Todas las tablas con prefijo "inva-"

-- Usar la base de datos
USE dbapp;

-- Tabla de Usuarios
CREATE TABLE IF NOT EXISTS `inva-usuarios` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(100),
    email VARCHAR(100),
    rol ENUM('admin', 'vendedor', 'contador') DEFAULT 'vendedor',
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso TIMESTAMP NULL,
    INDEX idx_username (username),
    INDEX idx_rol (rol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de Clientes
CREATE TABLE IF NOT EXISTS `inva-clientes` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    ruc_dni VARCHAR(20) UNIQUE,
    direccion TEXT,
    telefono VARCHAR(20),
    email VARCHAR(100),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_ruc_dni (ruc_dni),
    INDEX idx_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de Categorias
CREATE TABLE IF NOT EXISTS `inva-categorias` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_nombre (nombre),
    INDEX idx_activo (activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de Ajustes del Negocio
CREATE TABLE IF NOT EXISTS `inva-ajustes_negocio` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    rtn VARCHAR(30),
    telefono VARCHAR(30),
    email VARCHAR(120),
    direccion VARCHAR(255),
    cai VARCHAR(60),
    rango_autorizado VARCHAR(120),
    rango_autorizado_inicio VARCHAR(120),
    rango_autorizado_fin VARCHAR(120),
    fecha_limite_emision VARCHAR(30),
    mensaje VARCHAR(255)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de Productos
CREATE TABLE IF NOT EXISTS `inva-productos` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    stock INT DEFAULT 0,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    isv_aplica BOOLEAN DEFAULT FALSE,
    foto VARCHAR(255),
    INDEX idx_codigo (codigo),
    INDEX idx_categoria (categoria),
    INDEX idx_activo (activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de Facturas
CREATE TABLE IF NOT EXISTS `inva-facturas` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_factura VARCHAR(50) UNIQUE NOT NULL,
    cliente_id INT,
    usuario_id INT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    subtotal DECIMAL(10,2),
    igv DECIMAL(10,2),
    total DECIMAL(10,2),
    estado ENUM('pendiente', 'pagada', 'anulada') DEFAULT 'pendiente',
    FOREIGN KEY (cliente_id) REFERENCES `inva-clientes`(id) ON DELETE SET NULL,
    FOREIGN KEY (usuario_id) REFERENCES `inva-usuarios`(id) ON DELETE SET NULL,
    INDEX idx_numero_factura (numero_factura),
    INDEX idx_fecha (fecha),
    INDEX idx_estado (estado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de Pedidos
CREATE TABLE IF NOT EXISTS `inva-pedidos` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_pedido VARCHAR(50) UNIQUE NOT NULL,
    cliente_id INT,
    usuario_id INT,
    rtn VARCHAR(20),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    subtotal DECIMAL(10,2),
    isv DECIMAL(10,2),
    descuento DECIMAL(10,2),
    total DECIMAL(10,2),
    estado ENUM('pendiente', 'listo', 'facturado', 'anulado') DEFAULT 'pendiente',
    FOREIGN KEY (cliente_id) REFERENCES `inva-clientes`(id) ON DELETE SET NULL,
    FOREIGN KEY (usuario_id) REFERENCES `inva-usuarios`(id) ON DELETE SET NULL,
    INDEX idx_numero_pedido (numero_pedido),
    INDEX idx_fecha_pedido (fecha),
    INDEX idx_estado_pedido (estado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de Detalle Pedidos
CREATE TABLE IF NOT EXISTS `inva-detalle_pedidos` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    descuento DECIMAL(10,2) DEFAULT 0,
    isv_aplica BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (pedido_id) REFERENCES `inva-pedidos`(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES `inva-productos`(id) ON DELETE RESTRICT,
    INDEX idx_pedido_id (pedido_id),
    INDEX idx_producto_id_pedido (producto_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de Facturas Contado
CREATE TABLE IF NOT EXISTS `inva-facturas_contado` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_factura VARCHAR(50) UNIQUE NOT NULL,
    cliente_id INT,
    usuario_id INT,
    rtn VARCHAR(20),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    subtotal DECIMAL(10,2),
    isv DECIMAL(10,2),
    descuento DECIMAL(10,2),
    total DECIMAL(10,2),
    pago DECIMAL(10,2),
    cambio DECIMAL(10,2),
    estado ENUM('contado', 'credito', 'pagada', 'anulada') DEFAULT 'contado',
    pdf_filename VARCHAR(255),
    FOREIGN KEY (cliente_id) REFERENCES `inva-clientes`(id) ON DELETE SET NULL,
    FOREIGN KEY (usuario_id) REFERENCES `inva-usuarios`(id) ON DELETE SET NULL,
    INDEX idx_numero_factura_contado (numero_factura),
    INDEX idx_fecha_contado (fecha)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de Facturas Credito
CREATE TABLE IF NOT EXISTS `inva-facturas_credito` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_factura VARCHAR(50) UNIQUE NOT NULL,
    cliente_id INT,
    usuario_id INT,
    rtn VARCHAR(20),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    subtotal DECIMAL(10,2),
    isv DECIMAL(10,2),
    descuento DECIMAL(10,2),
    total DECIMAL(10,2),
    pago_inicial DECIMAL(10,2),
    saldo DECIMAL(10,2),
    estado ENUM('pendiente', 'pagada', 'anulada') DEFAULT 'pendiente',
    pdf_filename VARCHAR(255),
    FOREIGN KEY (cliente_id) REFERENCES `inva-clientes`(id) ON DELETE SET NULL,
    FOREIGN KEY (usuario_id) REFERENCES `inva-usuarios`(id) ON DELETE SET NULL,
    INDEX idx_numero_factura_credito (numero_factura),
    INDEX idx_fecha_credito (fecha)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de Detalle de Facturas
CREATE TABLE IF NOT EXISTS `inva-detalle_facturas` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    factura_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (factura_id) REFERENCES `inva-facturas`(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES `inva-productos`(id) ON DELETE RESTRICT,
    INDEX idx_factura_id (factura_id),
    INDEX idx_producto_id (producto_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de Detalle Facturas Contado
CREATE TABLE IF NOT EXISTS `inva-detalle_facturas_contado` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    factura_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    descuento DECIMAL(10,2) DEFAULT 0,
    isv_aplica BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (factura_id) REFERENCES `inva-facturas_contado`(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES `inva-productos`(id) ON DELETE RESTRICT,
    INDEX idx_factura_id_contado (factura_id),
    INDEX idx_producto_id_contado (producto_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de Abonos de Facturas
CREATE TABLE IF NOT EXISTS `inva-abonos_facturas` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    factura_id INT NOT NULL,
    usuario_id INT,
    monto DECIMAL(10,2) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (factura_id) REFERENCES `inva-facturas_contado`(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES `inva-usuarios`(id) ON DELETE SET NULL,
    INDEX idx_abono_factura_id (factura_id),
    INDEX idx_abono_fecha (fecha)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de Detalle Facturas Credito
CREATE TABLE IF NOT EXISTS `inva-detalle_facturas_credito` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    factura_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    descuento DECIMAL(10,2) DEFAULT 0,
    isv_aplica BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (factura_id) REFERENCES `inva-facturas_credito`(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES `inva-productos`(id) ON DELETE RESTRICT,
    INDEX idx_factura_id_credito (factura_id),
    INDEX idx_producto_id_credito (producto_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertar usuario administrador por defecto
-- Contraseña: invagro2024 (hash generado con Werkzeug)
INSERT INTO `inva-usuarios` (username, password, nombre_completo, email, rol, activo)
VALUES (
    'admin',
    'scrypt:32768:8:1$893aolVQOYC4AhAr$fb106a8be348e6c7285209a4f1c99c0ce0da8914233c8cb04ce95726c261d686670558059b7c4060d5983d9671665d10b3b757eb0b911ae18a15f91e1efd7450',
    'Administrador Invagro',
    'admin@invagro.com',
    'admin',
    TRUE
) ON DUPLICATE KEY UPDATE username=username;

-- Insertar productos de ejemplo
INSERT INTO `inva-productos` (codigo, nombre, categoria, precio, stock, descripcion, activo)
VALUES
    ('SHMP001', 'Shampoo Antipulgas Premium', 'shampoo', 45.00, 50, 'Shampoo antipulgas de alta calidad para perros', TRUE),
    ('SHMP002', 'Shampoo Hipoalergénico', 'shampoo', 38.00, 30, 'Shampoo especial para pieles sensibles', TRUE),
    ('SHMP003', 'Shampoo Acondicionador 2 en 1', 'shampoo', 42.00, 40, 'Limpia y acondiciona el pelaje', TRUE),
    ('VET001', 'Vitaminas Caninas', 'veterinario', 65.00, 40, 'Suplemento vitamínico completo', TRUE),
    ('VET002', 'Desparasitante Interno', 'veterinario', 55.00, 60, 'Desparasitante de amplio espectro', TRUE),
    ('VET003', 'Antipulgas Tópico', 'veterinario', 48.00, 35, 'Tratamiento antipulgas de larga duración', TRUE),
    ('VET004', 'Suplemento Articular', 'veterinario', 72.00, 25, 'Para salud de articulaciones y huesos', TRUE)
ON DUPLICATE KEY UPDATE codigo=codigo;

-- Insertar categorias base
INSERT INTO `inva-categorias` (nombre, activo)
VALUES
    ('Veterinario', TRUE),
    ('Shampoo', TRUE)
ON DUPLICATE KEY UPDATE nombre=nombre;

-- Insertar clientes de ejemplo
INSERT INTO `inva-clientes` (nombre, ruc_dni, direccion, telefono, email)
VALUES
    ('Veterinaria San Francisco', '20123456789', 'Av. Principal 123, Lima', '01-2345678', 'ventas@vetsanfrancisco.com'),
    ('Pet Shop Los Cachorros', '20987654321', 'Jr. Los Perros 456, Lima', '01-8765432', 'info@loscachorros.com'),
    ('Juan Pérez García', '12345678', 'Calle Las Flores 789, Lima', '987654321', 'juan.perez@email.com'),
    ('Clínica Veterinaria El Arca', '20555666777', 'Av. Los Animales 321, Lima', '01-5556667', 'contacto@elarca.com'),
    ('María González López', '87654321', 'Jr. Las Mascotas 654, Lima', '912345678', 'maria.gonzalez@email.com')
ON DUPLICATE KEY UPDATE ruc_dni=ruc_dni;

-- Verificar las tablas creadas
SELECT 'Tablas creadas exitosamente' AS mensaje;
SELECT COUNT(*) AS total_usuarios FROM `inva-usuarios`;
SELECT COUNT(*) AS total_productos FROM `inva-productos`;
SELECT COUNT(*) AS total_clientes FROM `inva-clientes`;
