<<<<<<< HEAD
# CineApp - Sistema de Administración de Sala de Cine

CineApp es una aplicación web desarrollada con Flask y Bootstrap 5 que permite administrar una sala de cine, gestionar reservas, tarjetas de descuento y pagos.

## Características Principales

- 🎬 Visualización de sala de cine con 220 sillas (filas A-K, números 1-20)
- 💺 Gestión de tipos de sillas (general y preferencial) con diferentes precios
- 🎫 Sistema de reservas (hasta 8 sillas por cliente)
- 💳 Tarjeta CINEMAS con descuentos y sistema de recarga
- 💰 Múltiples métodos de pago (efectivo y tarjeta CINEMAS)
- 📊 Reportes de caja y estado de sillas

## Requisitos Técnicos

- Python 3.8+
- Flask 2.3.3+
- Flask-SQLAlchemy 3.1.1+
- Flask-WTF 1.2.1+
- SQLite (base de datos)
- Bootstrap 5 (frontend)

## Instalación

1. Clona este repositorio:
```
git clone <url-del-repositorio>
cd cineapp
```

2. Crea un entorno virtual e instala las dependencias:
```
python -m venv venv
venv\Scripts\activate  # En Windows
source venv/bin/activate  # En macOS/Linux
pip install -r requirements.txt
```

3. Ejecuta la aplicación:
```
python run.py
```

4. Accede a la aplicación en tu navegador:
```
http://localhost:5000
```

## Estructura del Proyecto

```
cineapp/
│
├── app/
│   ├── __init__.py           # Inicialización de la aplicación Flask
│   ├── models.py             # Modelos de datos (SQLAlchemy)
│   ├── forms.py              # Formularios (Flask-WTF)
│   ├── routes/               # Rutas de la aplicación
│   │   ├── main.py           # Rutas principales
│   │   ├── tarjetas.py       # Gestión de tarjetas CINEMAS
│   │   ├── reservas.py       # Gestión de reservas
│   │   ├── pagos.py          # Gestión de pagos
│   ├── templates/            # Plantillas HTML (Jinja2)
│   │   ├── base.html         # Plantilla base
│   │   ├── index.html        # Página principal
│   │   ├── tarjetas/         # Plantillas para tarjetas
│   │   ├── reservas/         # Plantillas para reservas
│   │   ├── pagos/            # Plantillas para pagos
│   ├── static/               # Archivos estáticos
│       ├── css/              # Hojas de estilo
│       ├── js/               # JavaScript
│
├── run.py                    # Script para ejecutar la aplicación
├── requirements.txt          # Dependencias del proyecto
```

## Funcionalidades Implementadas

### Tarjetas CINEMAS
- Crear nueva tarjeta con saldo inicial (mínimo $70,000)
- Recargar tarjeta (montos de $50,000)
- Consultar saldo y estado de tarjeta

### Reservas
- Crear reserva seleccionando hasta 8 sillas
- Visualizar detalles de reserva
- Cancelar reserva

### Pagos
- Pagar reserva en efectivo
- Pagar reserva con tarjeta CINEMAS (10% de descuento)
- Anular pago y devolver saldo

### Administración
- Visualizar estado de todas las sillas
- Consultar dinero en caja

## Precios
- Sillas Generales (filas A-H): $8,000
- Sillas Preferenciales (filas I-K): $11,000

## Licencia
Este proyecto está bajo la Licencia MIT.
proyecto-11-cinemas
=======
# proyecto-11-cinemas-Grupo 3

### John Casallas
### James Sarmiento
### Filiph Suan

# Tecnología en construcción de software

>>>>>>> 4c44c3bf1e10b76be9851c593b3b10db0020c0c3
