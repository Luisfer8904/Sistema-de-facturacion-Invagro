# 📊 Instrucciones para Crear Base de Datos Local MySQL

## Opción 1: Usando MySQL Workbench (Recomendado - Visual)

### Paso 1: Conectar a tu servidor MySQL local
1. Abre **MySQL Workbench**
2. Haz clic en tu conexión local (generalmente `Local instance MySQL`)
3. Ingresa tu contraseña de root

### Paso 2: Crear la base de datos (si no existe)
```sql
CREATE DATABASE IF NOT EXISTS dbapp 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;
```

### Paso 3: Ejecutar el script SQL
1. En MySQL Workbench, ve a **File → Open SQL Script**
2. Navega a: `scripts/create_tables_mysql.sql`
3. Haz clic en el botón **Execute** (⚡ rayo) o presiona `Ctrl+Shift+Enter`
4. Verifica que todas las tablas se crearon correctamente

### Paso 4: Verificar las tablas
```sql
USE dbapp;
SHOW TABLES;

-- Deberías ver:
-- inva-clientes
-- inva-detalle_facturas
-- inva-facturas
-- inva-productos
-- inva-usuarios
```

---

## Opción 2: Usando Terminal/Línea de Comandos

### Paso 1: Conectar a MySQL
```bash
mysql -u root -p
```
Ingresa tu contraseña cuando te la pida.

### Paso 2: Crear la base de datos (si no existe)
```sql
CREATE DATABASE IF NOT EXISTS dbapp 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

EXIT;
```

### Paso 3: Ejecutar el script SQL
```bash
mysql -u root -p dbapp < scripts/create_tables_mysql.sql
```

### Paso 4: Verificar
```bash
mysql -u root -p dbapp -e "SHOW TABLES;"
```

---

## Opción 3: Copiar y Pegar en MySQL Workbench

### Paso 1: Abrir el archivo SQL
1. Abre el archivo `scripts/create_tables_mysql.sql` en un editor de texto
2. Copia todo el contenido

### Paso 2: Ejecutar en MySQL Workbench
1. Abre MySQL Workbench y conéctate
2. Abre una nueva pestaña de Query (Ctrl+T)
3. Pega el contenido del archivo SQL
4. Ejecuta todo el script (Ctrl+Shift+Enter)

---

## 📋 Datos Creados Automáticamente

### Usuario Administrador
- **Usuario:** admin
- **Contraseña:** invagro2024
- **Rol:** admin
- **Email:** admin@invagro.com

### Productos de Ejemplo (7 productos)
1. **SHMP001** - Shampoo Antipulgas Premium - S/. 45.00
2. **SHMP002** - Shampoo Hipoalergénico - S/. 38.00
3. **SHMP003** - Shampoo Acondicionador 2 en 1 - S/. 42.00
4. **VET001** - Vitaminas Caninas - S/. 65.00
5. **VET002** - Desparasitante Interno - S/. 55.00
6. **VET003** - Antipulgas Tópico - S/. 48.00
7. **VET004** - Suplemento Articular - S/. 72.00

### Clientes de Ejemplo (5 clientes)
1. Veterinaria San Francisco
2. Pet Shop Los Cachorros
3. Juan Pérez García
4. Clínica Veterinaria El Arca
5. María González López

---

## 🔧 Configurar la Aplicación para Usar MySQL Local

### Paso 1: Editar el archivo `.env`
```bash
nano .env
```

### Paso 2: Configurar las credenciales de MySQL local
```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production

# Database Configuration (MySQL LOCAL)
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu-password-mysql-local
DB_NAME=dbapp

# Application Configuration
APP_NAME=Invagro - Sistema de Facturación
APP_HOST=0.0.0.0
APP_PORT=5000
```

### Paso 3: Ejecutar la aplicación
```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar aplicación con MySQL local
python app.py
```

---

## ✅ Verificación Final

### Verificar que las tablas tienen datos:
```sql
USE dbapp;

-- Verificar usuarios
SELECT * FROM `inva-usuarios`;

-- Verificar productos
SELECT * FROM `inva-productos`;

-- Verificar clientes
SELECT * FROM `inva-clientes`;

-- Contar registros
SELECT 
    (SELECT COUNT(*) FROM `inva-usuarios`) AS usuarios,
    (SELECT COUNT(*) FROM `inva-productos`) AS productos,
    (SELECT COUNT(*) FROM `inva-clientes`) AS clientes;
```

Deberías ver:
- **1 usuario** (admin)
- **7 productos**
- **5 clientes**

---

## 🚨 Solución de Problemas

### Error: "Access denied for user"
```bash
# Verificar que MySQL está corriendo
sudo systemctl status mysql  # Linux
brew services list  # macOS

# Reiniciar MySQL si es necesario
sudo systemctl restart mysql  # Linux
brew services restart mysql  # macOS
```

### Error: "Database does not exist"
```sql
-- Crear la base de datos manualmente
CREATE DATABASE dbapp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Error: "Table already exists"
```sql
-- Eliminar tablas existentes (¡CUIDADO! Esto borra todos los datos)
DROP DATABASE dbapp;
CREATE DATABASE dbapp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- Luego ejecutar el script nuevamente
```

---

## 📞 Siguiente Paso

Una vez creadas las tablas, puedes:

1. **Ejecutar la aplicación localmente:**
   ```bash
   python app.py
   ```

2. **Acceder a:** http://localhost:5000

3. **Login con:**
   - Usuario: `admin`
   - Contraseña: `invagro2024`

---

## 💡 Nota Importante

Si prefieres seguir usando **SQLite** para desarrollo local (más simple), puedes continuar usando:
```bash
python run_local.py
```

Esto usa una base de datos SQLite local (`invagro_local.db`) sin necesidad de configurar MySQL.
