# 🚀 Guía Rápida - Sistema de Facturación Invagro

## ✅ Estado Actual

¡Las tablas MySQL se crearon exitosamente en la base de datos `dbapp`! Ahora tienes dos opciones para ejecutar la aplicación:

---

## 📊 Opción 1: SQLite (Actual - Más Simple)

### ✅ Ya está corriendo
La aplicación ya está funcionando con SQLite en tu terminal.

**Acceso:**
- URL: http://127.0.0.1:5000
- Usuario: `admin`
- Contraseña: `invagro2024`

**Ventajas:**
- ✅ No requiere configuración adicional
- ✅ Base de datos en archivo local (`invagro_local.db`)
- ✅ Perfecto para desarrollo y pruebas
- ✅ Mismo esquema de tablas con prefijo "inva-"

**Mantener corriendo:**
```bash
# Ya está corriendo en tu terminal
# Solo accede a: http://127.0.0.1:5000
```

---

## 🗄️ Opción 2: MySQL Local (Producción-like)

### Paso 1: Detener SQLite
```bash
# En la terminal donde corre run_local.py
# Presiona: CTRL+C
```

### Paso 2: Ejecutar con MySQL
```bash
# Opción A: Script interactivo (te pedirá la contraseña)
python run_mysql_local.py

# Opción B: Configurar .env manualmente
# Edita el archivo .env con tus credenciales MySQL
# Luego ejecuta:
python app.py
```

**Ventajas:**
- ✅ Usa la misma base de datos que producción
- ✅ Tablas ya creadas con el script SQL
- ✅ Datos de ejemplo ya insertados
- ✅ Mejor para testing antes de deployment

---

## 📋 Resumen de lo que tienes

### ✅ Base de Datos MySQL `dbapp`
Tablas creadas (vistas en MySQL Workbench):
- ✅ `inva-usuarios` (1 usuario admin)
- ✅ `inva-productos` (7 productos)
- ✅ `inva-clientes` (5 clientes)
- ✅ `inva-facturas` (vacía, lista para usar)
- ✅ `inva-detalle_facturas` (vacía, lista para usar)

### ✅ Aplicación Funcionando
- ✅ Servidor corriendo en http://127.0.0.1:5000
- ✅ Login funcional
- ✅ Dashboard con estadísticas
- ✅ Base de datos SQLite con datos de prueba

---

## 🎯 Recomendación

### Para Desarrollo Rápido:
**Usa SQLite (actual)** - Ya está corriendo, solo accede y prueba.

### Para Testing Pre-Producción:
**Usa MySQL local** - Detén SQLite y ejecuta `python run_mysql_local.py`

### Para Producción:
**Usa AWS Lightsail** - Sigue la guía en `DEPLOYMENT_GUIDE.md`

---

## 🔄 Cambiar entre SQLite y MySQL

### De SQLite a MySQL:
```bash
# 1. Detener SQLite (CTRL+C en terminal)
# 2. Ejecutar con MySQL
python run_mysql_local.py
```

### De MySQL a SQLite:
```bash
# 1. Detener MySQL (CTRL+C en terminal)
# 2. Ejecutar con SQLite
python run_local.py
```

---

## 📊 Verificar Datos en MySQL

### Usando MySQL Workbench:
1. Conectar a `localhost`
2. Seleccionar base de datos `invagro`
3. Ver tablas en el panel izquierdo

### Usando Terminal:
```bash
mysql -u root -p dbapp

# Dentro de MySQL:
SHOW TABLES;
SELECT * FROM `inva-usuarios`;
SELECT * FROM `inva-productos`;
SELECT * FROM `inva-clientes`;
```

---

## 🎊 ¡Todo Listo!

Tu sistema está **100% funcional** con:
- ✅ Base de datos MySQL creada y poblada
- ✅ Aplicación corriendo con SQLite
- ✅ Scripts para cambiar entre bases de datos
- ✅ Documentación completa

**Próximo paso:** Prueba la aplicación en http://127.0.0.1:5000

---

## 📞 Archivos de Ayuda

- `README.md` - Documentación completa
- `DEPLOYMENT_GUIDE.md` - Deployment en AWS
- `INSTRUCCIONES_BD_LOCAL.md` - Detalles de MySQL local
- `TODO.md` - Lista de tareas completadas

---

## 💡 Comandos Útiles

```bash
# Ver qué está corriendo
ps aux | grep python

# Matar proceso si es necesario
pkill -f "python run_local.py"

# Ver logs en tiempo real
tail -f invagro_local.db  # SQLite
# o ver logs de MySQL en Workbench

# Backup de base de datos SQLite
cp invagro_local.db invagro_local.db.backup

# Backup de base de datos MySQL
mysqldump -u root -p dbapp > backup_dbapp.sql
