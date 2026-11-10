[🇺🇸 English](#english) | [🇪🇸 Español](#español) | [🇧🇷 Português](#portugues)

<a name="español"></a>

# ESPAÑOL (ORIGINAL)

![FastAPI](https://img.shields.io/badge/FastAPI-0.128.3-000000?style=for-the-badge&logo=fastapi )
![Python](https://img.shields.io/badge/python-3.11.9-000000?style=for-the-badge&logo=Python&logoColor=)
![Pydantic](https://img.shields.io/badge/Pydantic-2.12.5-000000?style=for-the-badge&logo=pydantic)
![AbacatePay](https://img.shields.io/badge/AbacatePay-integrated-000000?style=for-the-badge)
![Jinja](https://img.shields.io/badge/Jinja2-3.1.6-000000?style=for-the-badge&logo=jinja)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-supported-000000?style=for-the-badge&logo=postgresql&logoColor=white)
![js](https://img.shields.io/badge/javascript-ES6+-000000?style=for-the-badge&logo=javascript)
![WebSocket](https://img.shields.io/badge/websocket-16.0-000000?style=for-the-badge&logo=websocket)
![Alembic](https://img.shields.io/badge/Alembic-1.18.0-000000?style=for-the-badge&logo=alembic)
![Html](https://img.shields.io/badge/html-000000?style=for-the-badge&logo=html5)
![Css](https://img.shields.io/badge/Css-000000?style=for-the-badge&logo=css)

![CloudFlare](https://img.shields.io/badge/CloudFlare-000000?style=for-the-badge&logo=Cloudflare)


# ProntoERP

ProntoERP es un ERP web para empresas de muebles y marcenarias. Organiza empresas y usuarios, inventario y salidas con códigos de barras, producción, clientes y contactos, finanzas, proyectos y seguimiento del trabajo. Incluye planificación semanal, registro y reportes de horas, notificaciones en tiempo real, suscripciones por módulos y enlaces públicos para compartir proyectos, cronogramas y avances. El backend está construido con FastAPI y PostgreSQL; las vistas se renderizan con Jinja2.

---

## 📸 Vista previa

![Home](https://i.imgur.com/Z89LSHn.png)

![Login](https://i.imgur.com/Z8B7FX5.png)

![Signup](https://i.imgur.com/SBVbcZB.png)

![Inventory](https://i.imgur.com/h0xzs4F.png)

![Verify Email](https://i.imgur.com/hvAY55S.png)

![Notifications](https://i.imgur.com/lZjmEA6.png)

![Plans](https://pub-d87bacf6dcc9454fb4443bece5f09d58.r2.dev/repo/Captura%20de%20tela%202026-05-19%20095911.png)

![Payment](https://pub-d87bacf6dcc9454fb4443bece5f09d58.r2.dev/repo/Captura%20de%20tela%202026-05-19%20100014.png)

![Project_View](https://pub-d87bacf6dcc9454fb4443bece5f09d58.r2.dev/repo/Captura%20de%20tela%202026-05-19%20102353.png)

![Project_Client](https://pub-d87bacf6dcc9454fb4443bece5f09d58.r2.dev/repo/Captura%20de%20tela%202026-05-19%20102518.png)

---

## 🧠 Descripción

Esta aplicación web está organizada en módulos que pueden habilitarse por empresa. Las rutas principales incluyen autenticación y creación de empresas; inventario con movimientos y códigos de barras; producción; contactos; ventas, cuentas por pagar y por cobrar e indicadores financieros; proyectos con archivos y comentarios; seguimiento de etapas, retrasos y muebles; cronogramas semanales compartibles; y registro de horas con filtros de reportes. Los clientes pueden consultar proyectos y avances mediante enlaces públicos. Las notificaciones se distribuyen por WebSocket. Las suscripciones y pagos se integran con AbacatePay; los archivos se guardan mediante almacenamiento compatible con S3/R2. No se encontró un agente de IA implementado en el código actual.


## ⚙️ Tecnologías usadas

### 🚀 Backend
- FastAPI
- Starlette
- Uvicorn

### 🗄 Base de Datos y ORM
- PostgreSQL (psycopg2-binary)
- SQLAlchemy
- Alembic

### 🔐 Autenticación y Seguridad
- JWT (python-jose)
- Passlib
- Bcrypt
- Cryptography
- RSA
- ECDSA

### 📧 Servicio de Email
- FastAPI-Mail
- aiosmtplib
- email-validator

### ☁️ Almacenamiento y Servicios Externos
- AWS S3 / Cloudflare R2 (boto3, botocore, s3transfer)

### ⚙️ Configuración y Entorno
- python-dotenv
- PyYAML
- pydantic-settings

### 📦 Validación y Serialización de Datos
- Pydantic
- annotated-types
- annotated-doc

### 🌐 HTTP y Networking
- Requests
- urllib3
- websockets
- dnspython

### 🧰 Templates y Utilidades
- Jinja2
- Mako
- python-dateutil
- regex
- uuid
- click
- colorama

### 📄 Validación de JSON y Schemas
- jsonschema
- jsonschema-specifications
- referencing
- rpds-py

### 💸 Pagos
- AbacatePay

### 🧪 Otras Dependencias Internas
- anyio
- attrs
- blinker
- cffi
- greenlet
- h11
- MarkupSafe
- python-multipart
- six
- typing_extensions
- typing-inspection
- tzdata

---

## 🏗️ Estructura del proyecto
```
erm/
├── admin/
│   ├── admin_router.py
│   └── admin_services.py
├── alembic/
│   ├── versions/
│   │   ├── 16203049f29e_no_recuerdo_el_cambio.py
│   │   ├── 1a13d62b285c_users_code.py
│   │   ├── 2d9220af34ba_barcode_inventory.py
│   │   ├── 2e685db8364c_module_router_para_cargar_modulos_.py
│   │   ├── 840effa772d3_module_icon.py
│   │   ├── a1f875ae8c5c_moduls_5.py
│   │   └── c38b54e0378a_icon_aside_url.py
│   ├── env.py
│   ├── README
│   └── script.py.mako
├── contacts/
│   ├── contacts_models.py
│   ├── contacts_route.py
│   ├── contacts_schema.py
│   └── contacts_services.py
├── core/
│   ├── config/
│   │   ├── __init__.backup.py
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── config_loader.py
│   │   └── parsers.py
│   ├── enum/
│   │   └── enum.py
│   ├── __init__.py
│   ├── barcode_service.py
│   ├── database.py
│   ├── dependencies.py
│   ├── email_service.py
│   ├── exceptions.py
│   ├── main.py
│   ├── security.py
│   └── templates_contex.py
├── cronograma/
│   ├── cronograma_models.py
│   ├── cronograma_router.py
│   ├── cronograma_schemas.py
│   └── cronograma_services.py
├── financery/
│   ├── financery_models.py
│   ├── financery_route.py
│   ├── financery_schema.py
│   ├── financery_services.py
│   └── payments_domain.py
├── frontend/
│   ├── static/
│   │   ├── contacts/
│   │   │   └── contacts.css
│   │   ├── cronograma/
│   │   │   ├── cronograma.css
│   │   │   └── share_cronograma.css
│   │   ├── financery/
│   │   │   └── financery_dashboard.css
│   │   ├── home/
│   │   │   └── menu.css
│   │   ├── inv/
│   │   │   └── dashboard.css
│   │   ├── js/
│   │   │   └── refresh_token.js
│   │   ├── production/
│   │   │   └── production.css
│   │   ├── project_tracking/
│   │   │   ├── dashboard.css
│   │   │   ├── detail.css
│   │   │   └── public.css
│   │   ├── projects/
│   │   │   ├── client_exp.css
│   │   │   ├── projects_add.css
│   │   │   ├── projects_dashboard.css
│   │   │   └── projects_detail.css
│   │   ├── time_tracking/
│   │   │   ├── time_tracking_add.css
│   │   │   ├── time_tracking_reports.css
│   │   │   └── time_tracking.css
│   │   ├── home.css
│   │   ├── login.css
│   │   ├── moduls.css
│   │   ├── plans.css
│   │   ├── signup.css
│   │   └── verify_email.css
│   └── templates/
│       ├── admin/
│       │   └── admin.html
│       ├── contacts/
│       │   └── contacts.html
│       ├── cronograma/
│       │   ├── cronograma.html
│       │   └── shared_schedule.html
│       ├── financery/
│       │   └── financery_dashboard.html
│       ├── home/
│       │   ├── barcode.html
│       │   ├── create-company.html
│       │   ├── forgot_password.html
│       │   ├── home.html
│       │   ├── index.html
│       │   ├── login.html
│       │   ├── signup.html
│       │   └── verify_email.html
│       ├── inv/
│       │   ├── barcode_output.html
│       │   └── dashboard.html
│       ├── payments/
│       │   ├── modules.html
│       │   ├── pay_fail.html
│       │   ├── pay_pending.html
│       │   └── pay_sucess.html
│       ├── plans/
│       │   └── plans.html
│       ├── production/
│       │   └── production.html
│       ├── project_tracking/
│       │   ├── dashboard.html
│       │   ├── detail.html
│       │   └── public.html
│       ├── projects/
│       │   ├── client_exp.html
│       │   ├── projects_add.html
│       │   ├── projects_dashboard.html
│       │   └── projects_details.html
│       ├── responses/
│       │   └── 404.html
│       ├── time_tracking/
│       │   ├── add.html
│       │   ├── dashboard.html
│       │   └── reports.html
│       ├── aside.html
│       ├── http-error-modal.html
│       ├── http-errors.json
│       ├── loading.html
│       ├── notification.html
│       └── pagination.html
├── inventory/
│   ├── __init__.py
│   ├── inventory_model.py
│   ├── inventory_route.py
│   ├── inventory_schema.py
│   └── inventory_service.py
├── moduls/
│   ├── dependencies.py
│   ├── moduls_models.py
│   ├── moduls_router.py
│   └── moduls_services.py
├── notification/
│   ├── notification_model.py
│   ├── notification_route.py
│   ├── notification_schema.py
│   ├── notification_services.py
│   └── ws_route.py
├── payments/
│   ├── payments_models.py
│   ├── payments_router.py
│   ├── payments_schema.py
│   ├── payments_services.py
│   ├── provider.py
│   ├── prueba.py
│   └── webhook.py
├── production/
│   ├── production_model.py
│   ├── production_route.py
│   └── production_schema.py
├── project_tracking/
│   ├── __init__.py
│   ├── project_tracking_model.py
│   ├── project_tracking_route.py
│   ├── project_tracking_schema.py
│   └── project_tracking_service.py
├── projects/
│   ├── coisa.py
│   ├── projects_model.py
│   ├── projects_route.py
│   ├── projects_schema.py
│   └── projects_services.py
├── time_tracking/
│   ├── __init__.py
│   ├── time_tracking_model.py
│   ├── time_tracking_route.py
│   ├── time_tracking_schema.py
│   ├── time_tracking_services.py
│   └── todo.txt
├── users/
│   ├── __init__.py
│   ├── users_model.py
│   ├── users_route.py
│   ├── users_schema.py
│   └── users_service.py
├── utilities/
│   ├── limiter/
│   │   └── limiter.py
│   └── storage/
│       └── storage_service.py
├── .dockerignore
├── .env.example
├── .gitignore
├── alembic.ini
├── config.yaml
├── Dockerfile
├── errors_tracking.md
├── README.md
└── requirements.txt
```

## 🚀 Instalación

1. Clona el repositorio y entra en la carpeta del proyecto.
2. Crea y activa un entorno virtual, e instala las dependencias:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
pip install -r requirements.txt
```

3. Copia `.env.example` como `.env` y rellena `.env` con los valores correspondientes, usando `.env.example` como guía, incluidos PostgreSQL, JWT, SMTP, almacenamiento S3/R2 y AbacatePay. El cargador de configuración necesita resolver todos los valores declarados en `config.yaml`. `config.yaml` lee esos valores del entorno.
4. Inicia la aplicación desde la raíz del repositorio:

```bash
uvicorn core.main:app --reload
```

Abre <http://127.0.0.1:8000>. Al iniciar, la aplicación crea las tablas declaradas por sus modelos; el proyecto también incluye historial de migraciones Alembic.

## 📌 Funcionalidades

✔️ Registro, autenticación, verificación de correo y gestión de empresas

✔️ Inventario, movimientos de stock y códigos de barras

✔️ Producción, contactos y proyectos con fotos, PDFs y comentarios

✔️ Panel financiero, ventas, pagos y cuentas por cobrar

✔️ Seguimiento de proyectos con etapas, retrasos, archivos y enlaces públicos

✔️ Cronogramas semanales compartibles

✔️ Registro de horas e informes

✔️ Notificaciones en tiempo real mediante WebSocket

✔️ Módulos por empresa y suscripciones con AbacatePay

ℹ️ El código actual no incluye un agente de IA.

## 🤝 Contribución

Todos son bienvenidos a ayudar y poner su granito de arena en este sistema y futuro SaaS

***Para hacerlo siga estos pasos:***

1. Haz un **fork** del repositorio  
2. Crea una nueva rama:*

```bash
#cambia y guarda
> git checkout -b feature/nueva-funcionalidad

#añade los cambios
> git add

#haz commit
> git commit -m 'nueva_funcionalidad'

#sube la rama
> git push origin feature/nueva-funcionalidad

#ve a GitHub y haz Pull Request
```

## 📏 Estándares del Proyecto

Este proyecto sigue una estructura modular estricta para mantener escalabilidad, orden y mantenibilidad.

---

## 🧱 Estructura modular obligatoria

Cada nueva funcionalidad debe crearse como un **módulo independiente**.

### 📌 Regla principal:
> Una carpeta por cada parte específica del sistema.

Ejemplo:
```
erm/
├── users/
├── inventory/
├── financery/
├── contacts/
└── new_module/
```

---

## 📁 Estructura obligatoria de cada módulo

Cada módulo debe seguir este patrón:
```
new_module/
├── %_model.py
├── %_service.py
├── %_route.py
└── %_schema.py
```

---

## 🧠 Reglas importantes

- ✔️ No mezclar lógica entre módulos
- ✔️ Cada módulo debe ser independiente
- ✔️ No importar lógica interna de otros módulos directamente
- ✔️ Toda comunicación debe pasar por servicios (`service.py`)
- ✔️ Los endpoints siempre van en `route.py`
- ✔️ Validaciones siempre en `schema.py`

---

## 🏷️ Convención de nombres

Se debe respetar el estilo ya existente:

- `users_model.py`
- `inventory_service.py`
- `contacts_route.py`

---

## 💬 Convención de commits

Se debe seguir el estándar:

### Tipos permitidos:

- `feat:` nueva funcionalidad
- `fix:` corrección de bugs
- `refactor:` mejoras de código sin cambiar lógica
- `docs:` cambios en documentación
- `test:` pruebas
- `chore:` mantenimiento general

### Ejemplos:

```bash
git commit -m "feat: add inventory stock validation"
git commit -m "fix: correct user authentication bug"
git commit -m "refactor: improve service layer structure"
```

#### #para pruebas, pueden eliminar las filas que guardan la informacion del email, pero si lo quieren llenar y ver todas las funcionalidades del sistema pueden acceder a esa informacion directamente desde su aplicacion de correo electronico

#### *Por favor, siempre crear rama desde main, desarrollar el modulo deseado siguiendo la estructura obligatoria, agradezco la comprensión de todos



<a name="english"></a>
#   ENGLISH

![FastAPI](https://img.shields.io/badge/FastAPI-0.128.3-000000?style=for-the-badge&logo=fastapi )
![Python](https://img.shields.io/badge/python-3.11.9-000000?style=for-the-badge&logo=Python&logoColor=)
![Pydantic](https://img.shields.io/badge/Pydantic-2.12.5-000000?style=for-the-badge&logo=pydantic)
![AbacatePay](https://img.shields.io/badge/AbacatePay-integrated-000000?style=for-the-badge)
![Jinja](https://img.shields.io/badge/Jinja2-3.1.6-000000?style=for-the-badge&logo=jinja)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-supported-000000?style=for-the-badge&logo=postgresql&logoColor=white)
![js](https://img.shields.io/badge/javascript-ES6+-000000?style=for-the-badge&logo=javascript)
![WebSocket](https://img.shields.io/badge/websocket-16.0-000000?style=for-the-badge&logo=websocket)
![Alembic](https://img.shields.io/badge/Alembic-1.18.0-000000?style=for-the-badge&logo=alembic)
![Html](https://img.shields.io/badge/html-000000?style=for-the-badge&logo=html5)
![Css](https://img.shields.io/badge/Css-000000?style=for-the-badge&logo=css)

![CloudFlare](https://img.shields.io/badge/CloudFlare-000000?style=for-the-badge&logo=Cloudflare)

# ProntoERP

ProntoERP is a web ERP for furniture businesses and carpentry shops. It organizes companies and users, inventory and barcode-based stock output, production, clients and contacts, finances, projects, and work tracking. It includes weekly planning, time entry and reports, real-time notifications, module-based subscriptions, and public links for sharing projects, schedules, and progress. The backend uses FastAPI and PostgreSQL, with pages rendered through Jinja2.

---

## 📸 Preview

![Home](https://i.imgur.com/Z89LSHn.png)

![Login](https://i.imgur.com/Z8B7FX5.png)

![Signup](https://i.imgur.com/SBVbcZB.png)

![Inventory](https://i.imgur.com/h0xzs4F.png)

![Verify Email](https://i.imgur.com/hvAY55S.png)

![Notifications](https://i.imgur.com/lZjmEA6.png)

![Plans](https://pub-d87bacf6dcc9454fb4443bece5f09d58.r2.dev/repo/Captura%20de%20tela%202026-05-19%20095911.png)

![Payment](https://pub-d87bacf6dcc9454fb4443bece5f09d58.r2.dev/repo/Captura%20de%20tela%202026-05-19%20100014.png)

![Project_View](https://pub-d87bacf6dcc9454fb4443bece5f09d58.r2.dev/repo/Captura%20de%20tela%202026-05-19%20102353.png)

![Project_Client](https://pub-d87bacf6dcc9454fb4443bece5f09d58.r2.dev/repo/Captura%20de%20tela%202026-05-19%20102518.png)

---

## 🧠 Description

This web application is organized into modules that can be enabled per company. Its main areas include authentication and company setup; inventory movements and barcodes; production; contacts; sales, payables, receivables, and financial indicators; projects with files and comments; stage, delay, and furniture tracking; shareable weekly schedules; and time entries with filtered reports. Clients can view projects and progress through public links. Notifications are delivered over WebSocket. Subscriptions and payments integrate with AbacatePay; files use S3/R2-compatible storage. No AI agent implementation was found in the current code.


## ⚙️ Technologies Used

### 🚀 Backend
- FastAPI
- Starlette
- Uvicorn

### 🗄 Database and ORM
- PostgreSQL (psycopg2-binary)
- SQLAlchemy
- Alembic

### 🔐 Authentication and Security
- JWT (python-jose)
- Passlib
- Bcrypt
- Cryptography
- RSA
- ECDSA

### 📧 Email Service
- FastAPI-Mail
- aiosmtplib
- email-validator

### ☁️ Storage and External Services
- AWS S3 / Cloudflare R2 (boto3, botocore, s3transfer)

### ⚙️ Configuration and Environment
- python-dotenv
- PyYAML
- pydantic-settings

### 📦 Data Validation and Serialization
- Pydantic
- annotated-types
- annotated-doc

### 🌐 HTTP and Networking
- Requests
- urllib3
- websockets
- dnspython

### 🧰 Templates and Utilities
- Jinja2
- Mako
- python-dateutil
- regex
- uuid
- click
- colorama

### 📄 JSON Validation and Schemas
- jsonschema
- jsonschema-specifications
- referencing
- rpds-py

### 💸 Payments
- AbacatePay

### 🧪 Other Internal Dependencies
- anyio
- attrs
- blinker
- cffi
- greenlet
- h11
- MarkupSafe
- python-multipart
- six
- typing_extensions
- typing-inspection
- tzdata
---

## 🏗️ Project Structure
```
erm/
├── admin/
│   ├── admin_router.py
│   └── admin_services.py
├── alembic/
│   ├── versions/
│   │   ├── 16203049f29e_no_recuerdo_el_cambio.py
│   │   ├── 1a13d62b285c_users_code.py
│   │   ├── 2d9220af34ba_barcode_inventory.py
│   │   ├── 2e685db8364c_module_router_para_cargar_modulos_.py
│   │   ├── 840effa772d3_module_icon.py
│   │   ├── a1f875ae8c5c_moduls_5.py
│   │   └── c38b54e0378a_icon_aside_url.py
│   ├── env.py
│   ├── README
│   └── script.py.mako
├── contacts/
│   ├── contacts_models.py
│   ├── contacts_route.py
│   ├── contacts_schema.py
│   └── contacts_services.py
├── core/
│   ├── config/
│   │   ├── __init__.backup.py
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── config_loader.py
│   │   └── parsers.py
│   ├── enum/
│   │   └── enum.py
│   ├── __init__.py
│   ├── barcode_service.py
│   ├── database.py
│   ├── dependencies.py
│   ├── email_service.py
│   ├── exceptions.py
│   ├── main.py
│   ├── security.py
│   └── templates_contex.py
├── cronograma/
│   ├── cronograma_models.py
│   ├── cronograma_router.py
│   ├── cronograma_schemas.py
│   └── cronograma_services.py
├── financery/
│   ├── financery_models.py
│   ├── financery_route.py
│   ├── financery_schema.py
│   ├── financery_services.py
│   └── payments_domain.py
├── frontend/
│   ├── static/
│   │   ├── contacts/
│   │   │   └── contacts.css
│   │   ├── cronograma/
│   │   │   ├── cronograma.css
│   │   │   └── share_cronograma.css
│   │   ├── financery/
│   │   │   └── financery_dashboard.css
│   │   ├── home/
│   │   │   └── menu.css
│   │   ├── inv/
│   │   │   └── dashboard.css
│   │   ├── js/
│   │   │   └── refresh_token.js
│   │   ├── production/
│   │   │   └── production.css
│   │   ├── project_tracking/
│   │   │   ├── dashboard.css
│   │   │   ├── detail.css
│   │   │   └── public.css
│   │   ├── projects/
│   │   │   ├── client_exp.css
│   │   │   ├── projects_add.css
│   │   │   ├── projects_dashboard.css
│   │   │   └── projects_detail.css
│   │   ├── time_tracking/
│   │   │   ├── time_tracking_add.css
│   │   │   ├── time_tracking_reports.css
│   │   │   └── time_tracking.css
│   │   ├── home.css
│   │   ├── login.css
│   │   ├── moduls.css
│   │   ├── plans.css
│   │   ├── signup.css
│   │   └── verify_email.css
│   └── templates/
│       ├── admin/
│       │   └── admin.html
│       ├── contacts/
│       │   └── contacts.html
│       ├── cronograma/
│       │   ├── cronograma.html
│       │   └── shared_schedule.html
│       ├── financery/
│       │   └── financery_dashboard.html
│       ├── home/
│       │   ├── barcode.html
│       │   ├── create-company.html
│       │   ├── forgot_password.html
│       │   ├── home.html
│       │   ├── index.html
│       │   ├── login.html
│       │   ├── signup.html
│       │   └── verify_email.html
│       ├── inv/
│       │   ├── barcode_output.html
│       │   └── dashboard.html
│       ├── payments/
│       │   ├── modules.html
│       │   ├── pay_fail.html
│       │   ├── pay_pending.html
│       │   └── pay_sucess.html
│       ├── plans/
│       │   └── plans.html
│       ├── production/
│       │   └── production.html
│       ├── project_tracking/
│       │   ├── dashboard.html
│       │   ├── detail.html
│       │   └── public.html
│       ├── projects/
│       │   ├── client_exp.html
│       │   ├── projects_add.html
│       │   ├── projects_dashboard.html
│       │   └── projects_details.html
│       ├── responses/
│       │   └── 404.html
│       ├── time_tracking/
│       │   ├── add.html
│       │   ├── dashboard.html
│       │   └── reports.html
│       ├── aside.html
│       ├── http-error-modal.html
│       ├── http-errors.json
│       ├── loading.html
│       ├── notification.html
│       └── pagination.html
├── inventory/
│   ├── __init__.py
│   ├── inventory_model.py
│   ├── inventory_route.py
│   ├── inventory_schema.py
│   └── inventory_service.py
├── moduls/
│   ├── dependencies.py
│   ├── moduls_models.py
│   ├── moduls_router.py
│   └── moduls_services.py
├── notification/
│   ├── notification_model.py
│   ├── notification_route.py
│   ├── notification_schema.py
│   ├── notification_services.py
│   └── ws_route.py
├── payments/
│   ├── payments_models.py
│   ├── payments_router.py
│   ├── payments_schema.py
│   ├── payments_services.py
│   ├── provider.py
│   ├── prueba.py
│   └── webhook.py
├── production/
│   ├── production_model.py
│   ├── production_route.py
│   └── production_schema.py
├── project_tracking/
│   ├── __init__.py
│   ├── project_tracking_model.py
│   ├── project_tracking_route.py
│   ├── project_tracking_schema.py
│   └── project_tracking_service.py
├── projects/
│   ├── coisa.py
│   ├── projects_model.py
│   ├── projects_route.py
│   ├── projects_schema.py
│   └── projects_services.py
├── time_tracking/
│   ├── __init__.py
│   ├── time_tracking_model.py
│   ├── time_tracking_route.py
│   ├── time_tracking_schema.py
│   ├── time_tracking_services.py
│   └── todo.txt
├── users/
│   ├── __init__.py
│   ├── users_model.py
│   ├── users_route.py
│   ├── users_schema.py
│   └── users_service.py
├── utilities/
│   ├── limiter/
│   │   └── limiter.py
│   └── storage/
│       └── storage_service.py
├── .dockerignore
├── .env.example
├── .gitignore
├── alembic.ini
├── config.yaml
├── Dockerfile
├── errors_tracking.md
├── README.md
└── requirements.txt
```

## 🚀 Installation

1. Clone the repository and enter the project directory.
2. Create and activate a virtual environment, then install dependencies:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and edit `.env` with the corresponding values, using `.env.example` as a guide, including PostgreSQL, JWT, SMTP, S3/R2 storage, and AbacatePay. The configuration loader must resolve every value declared in `config.yaml`. `config.yaml` reads these values from the environment.
4. Start the application from the repository root:

```bash
uvicorn core.main:app --reload
```

Open <http://127.0.0.1:8000>. On startup, the application creates tables declared by its models; the repository also includes Alembic migration history.

## 📌 Features

✔️ Signup, authentication, email verification, and company management

✔️ Inventory, stock movements, and barcodes

✔️ Production, contacts, and projects with photos, PDFs, and comments

✔️ Financial dashboard, sales, payments, and receivables

✔️ Project tracking with stages, delays, files, and public links

✔️ Shareable weekly schedules

✔️ Time entry and reports

✔️ Real-time WebSocket notifications

✔️ Company modules and AbacatePay subscriptions

ℹ️ The current code does not include an AI agent.

## 🤝 Contribution

Everyone is welcome to help and contribute to this system and future SaaS.

***To do so, follow these steps:***

1. **Fork** the repository  
2. Create a new branch:

```bash
# Switch and save
> git checkout -b feature/new-feature

# Add changes
> git add .

# Commit
> git commit -m 'new_feature'

# Push the branch
> git push origin feature/new-feature

# Go to GitHub and create a Pull Request
```

## 📏 Project Standards

This project follows a strict modular structure to maintain scalability, order, and maintainability.

---

## 🧱 Mandatory Modular Structure

Each new feature must be created as an **independent module**.

### 📌 Main Rule:
> One folder for each specific part of the system.

Example:
```
erm/
├── users/
├── inventory/
├── financery/
├── contacts/
└── new_module/
```

---

## 📁 Mandatory Structure for Each Module

Each module must follow this pattern:
```
new_module/
├── %_model.py
├── %_service.py
├── %_route.py
└── %_schema.py
```

---

## 🧠 Important Rules

- ✔️ Do not mix logic between modules
- ✔️ Each module must be independent
- ✔️ Do not import internal logic from other modules directly
- ✔️ All communication must go through services (`service.py`)
- ✔️ Endpoints always go in `route.py`
- ✔️ Validations always in `schema.py`

---

## 🏷️ Naming Convention

The existing style must be respected:

- `users_model.py`
- `inventory_service.py`
- `contacts_route.py`

For new modules:

- `model.py`
- `service.py`
- `route.py`
- `schema.py`

---

## 💬 Commit Convention

The standard must be followed:

### Allowed Types:

- `feat:` new feature
- `fix:` bug fix
- `refactor:` code improvements without changing logic
- `docs:` documentation changes
- `test:` tests
- `chore:` general maintenance

### Examples:

```bash
git commit -m "feat: add inventory stock validation"
git commit -m "fix: correct user authentication bug"
git commit -m "refactor: improve service layer structure"
```

#### # For testing, you can remove the rows that save email information, but if you want to fill them and see all system features, you can access that information directly from your email application.

#### * Please always create branches from main, develop the desired module following the mandatory structure, thank you for your understanding.

<a name="portugues"></a>

# PORTUGUÊS

![FastAPI](https://img.shields.io/badge/FastAPI-0.128.3-000000?style=for-the-badge&logo=fastapi )
![Python](https://img.shields.io/badge/python-3.11.9-000000?style=for-the-badge&logo=Python&logoColor=)
![Pydantic](https://img.shields.io/badge/Pydantic-2.12.5-000000?style=for-the-badge&logo=pydantic)
![AbacatePay](https://img.shields.io/badge/AbacatePay-integrated-000000?style=for-the-badge)
![Jinja](https://img.shields.io/badge/Jinja2-3.1.6-000000?style=for-the-badge&logo=jinja)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-supported-000000?style=for-the-badge&logo=postgresql&logoColor=white)
![js](https://img.shields.io/badge/javascript-ES6+-000000?style=for-the-badge&logo=javascript)
![WebSocket](https://img.shields.io/badge/websocket-16.0-000000?style=for-the-badge&logo=websocket)
![Alembic](https://img.shields.io/badge/Alembic-1.18.0-000000?style=for-the-badge&logo=alembic)
![Html](https://img.shields.io/badge/html-000000?style=for-the-badge&logo=html5)
![Css](https://img.shields.io/badge/Css-000000?style=for-the-badge&logo=css)

![Cloudflare](https://img.shields.io/badge/CloudFlare-000000?style=for-the-badge&logo=Cloudflare)

# ProntoERP

ProntoERP é um ERP web para empresas de móveis e marcenarias. Organiza empresas e usuários, estoque e baixas com código de barras, produção, clientes e contatos, finanças, projetos e acompanhamento do trabalho. Inclui planejamento semanal, registro e relatórios de horas, notificações em tempo real, assinaturas por módulos e links públicos para compartilhar projetos, cronogramas e progresso. O backend usa FastAPI e PostgreSQL; as páginas são renderizadas com Jinja2.

---

## 📸 Pré-visualização

![Home](https://i.imgur.com/Z89LSHn.png)

![Login](https://i.imgur.com/Z8B7FX5.png)

![Signup](https://i.imgur.com/SBVbcZB.png)

![Inventory](https://i.imgur.com/h0xzs4F.png)

![Verify Email](https://i.imgur.com/hvAY55S.png)

![Notifications](https://i.imgur.com/lZjmEA6.png)

![Plans](https://pub-d87bacf6dcc9454fb4443bece5f09d58.r2.dev/repo/Captura%20de%20tela%202026-05-19%20095911.png)

![Payment](https://pub-d87bacf6dcc9454fb4443bece5f09d58.r2.dev/repo/Captura%20de%20tela%202026-05-19%20100014.png)

![Project_View](https://pub-d87bacf6dcc9454fb4443bece5f09d58.r2.dev/repo/Captura%20de%20tela%202026-05-19%20102353.png)

![Project_Client](https://pub-d87bacf6dcc9454fb4443bece5f09d58.r2.dev/repo/Captura%20de%20tela%202026-05-19%20102518.png)

---

## 🧠 Descrição

Esta aplicação web é organizada em módulos que podem ser habilitados por empresa. As principais áreas incluem autenticação e cadastro de empresas; movimentações de estoque e códigos de barras; produção; contatos; vendas, contas a pagar e a receber e indicadores financeiros; projetos com arquivos e comentários; acompanhamento de etapas, atrasos e móveis; cronogramas semanais compartilháveis; e registros de horas com relatórios filtrados. Clientes podem consultar projetos e progresso por links públicos. As notificações são enviadas por WebSocket. As assinaturas e os pagamentos são integrados ao AbacatePay; os arquivos usam armazenamento compatível com S3/R2. Não foi encontrada implementação de agente de IA no código atual.


## ⚙️ Tecnologias Utilizadas

### 🚀 Backend
- FastAPI
- Starlette
- Uvicorn

### 🗄 Banco de Dados e ORM
- PostgreSQL (psycopg2-binary)
- SQLAlchemy
- Alembic

### 🔐 Autenticação e Segurança
- JWT (python-jose)
- Passlib
- Bcrypt
- Cryptography
- RSA
- ECDSA

### 📧 Serviço de E-mail
- FastAPI-Mail
- aiosmtplib
- email-validator

### ☁️ Armazenamento e Serviços Externos
- AWS S3 / Cloudflare R2 (boto3, botocore, s3transfer)

### ⚙️ Configuração e Ambiente
- python-dotenv
- PyYAML
- pydantic-settings

### 📦 Validação e Serialização de Dados
- Pydantic
- annotated-types
- annotated-doc

### 🌐 HTTP e Networking
- Requests
- urllib3
- websockets
- dnspython

### 🧰 Templates e Utilitários
- Jinja2
- Mako
- python-dateutil
- regex
- uuid
- click
- colorama

### 📄 Validação de JSON e Schemas
- jsonschema
- jsonschema-specifications
- referencing
- rpds-py

### 💸 Pagamentos
- AbacatePay

### 🧪 Outras Dependências Internas
- anyio
- attrs
- blinker
- cffi
- greenlet
- h11
- MarkupSafe
- python-multipart
- six
- typing_extensions
- typing-inspection
- tzdata

---

## 🏗️ Estrutura do Projeto
```
erm/
├── admin/
│   ├── admin_router.py
│   └── admin_services.py
├── alembic/
│   ├── versions/
│   │   ├── 16203049f29e_no_recuerdo_el_cambio.py
│   │   ├── 1a13d62b285c_users_code.py
│   │   ├── 2d9220af34ba_barcode_inventory.py
│   │   ├── 2e685db8364c_module_router_para_cargar_modulos_.py
│   │   ├── 840effa772d3_module_icon.py
│   │   ├── a1f875ae8c5c_moduls_5.py
│   │   └── c38b54e0378a_icon_aside_url.py
│   ├── env.py
│   ├── README
│   └── script.py.mako
├── contacts/
│   ├── contacts_models.py
│   ├── contacts_route.py
│   ├── contacts_schema.py
│   └── contacts_services.py
├── core/
│   ├── config/
│   │   ├── __init__.backup.py
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── config_loader.py
│   │   └── parsers.py
│   ├── enum/
│   │   └── enum.py
│   ├── __init__.py
│   ├── barcode_service.py
│   ├── database.py
│   ├── dependencies.py
│   ├── email_service.py
│   ├── exceptions.py
│   ├── main.py
│   ├── security.py
│   └── templates_contex.py
├── cronograma/
│   ├── cronograma_models.py
│   ├── cronograma_router.py
│   ├── cronograma_schemas.py
│   └── cronograma_services.py
├── financery/
│   ├── financery_models.py
│   ├── financery_route.py
│   ├── financery_schema.py
│   ├── financery_services.py
│   └── payments_domain.py
├── frontend/
│   ├── static/
│   │   ├── contacts/
│   │   │   └── contacts.css
│   │   ├── cronograma/
│   │   │   ├── cronograma.css
│   │   │   └── share_cronograma.css
│   │   ├── financery/
│   │   │   └── financery_dashboard.css
│   │   ├── home/
│   │   │   └── menu.css
│   │   ├── inv/
│   │   │   └── dashboard.css
│   │   ├── js/
│   │   │   └── refresh_token.js
│   │   ├── production/
│   │   │   └── production.css
│   │   ├── project_tracking/
│   │   │   ├── dashboard.css
│   │   │   ├── detail.css
│   │   │   └── public.css
│   │   ├── projects/
│   │   │   ├── client_exp.css
│   │   │   ├── projects_add.css
│   │   │   ├── projects_dashboard.css
│   │   │   └── projects_detail.css
│   │   ├── time_tracking/
│   │   │   ├── time_tracking_add.css
│   │   │   ├── time_tracking_reports.css
│   │   │   └── time_tracking.css
│   │   ├── home.css
│   │   ├── login.css
│   │   ├── moduls.css
│   │   ├── plans.css
│   │   ├── signup.css
│   │   └── verify_email.css
│   └── templates/
│       ├── admin/
│       │   └── admin.html
│       ├── contacts/
│       │   └── contacts.html
│       ├── cronograma/
│       │   ├── cronograma.html
│       │   └── shared_schedule.html
│       ├── financery/
│       │   └── financery_dashboard.html
│       ├── home/
│       │   ├── barcode.html
│       │   ├── create-company.html
│       │   ├── forgot_password.html
│       │   ├── home.html
│       │   ├── index.html
│       │   ├── login.html
│       │   ├── signup.html
│       │   └── verify_email.html
│       ├── inv/
│       │   ├── barcode_output.html
│       │   └── dashboard.html
│       ├── payments/
│       │   ├── modules.html
│       │   ├── pay_fail.html
│       │   ├── pay_pending.html
│       │   └── pay_sucess.html
│       ├── plans/
│       │   └── plans.html
│       ├── production/
│       │   └── production.html
│       ├── project_tracking/
│       │   ├── dashboard.html
│       │   ├── detail.html
│       │   └── public.html
│       ├── projects/
│       │   ├── client_exp.html
│       │   ├── projects_add.html
│       │   ├── projects_dashboard.html
│       │   └── projects_details.html
│       ├── responses/
│       │   └── 404.html
│       ├── time_tracking/
│       │   ├── add.html
│       │   ├── dashboard.html
│       │   └── reports.html
│       ├── aside.html
│       ├── http-error-modal.html
│       ├── http-errors.json
│       ├── loading.html
│       ├── notification.html
│       └── pagination.html
├── inventory/
│   ├── __init__.py
│   ├── inventory_model.py
│   ├── inventory_route.py
│   ├── inventory_schema.py
│   └── inventory_service.py
├── moduls/
│   ├── dependencies.py
│   ├── moduls_models.py
│   ├── moduls_router.py
│   └── moduls_services.py
├── notification/
│   ├── notification_model.py
│   ├── notification_route.py
│   ├── notification_schema.py
│   ├── notification_services.py
│   └── ws_route.py
├── payments/
│   ├── payments_models.py
│   ├── payments_router.py
│   ├── payments_schema.py
│   ├── payments_services.py
│   ├── provider.py
│   ├── prueba.py
│   └── webhook.py
├── production/
│   ├── production_model.py
│   ├── production_route.py
│   └── production_schema.py
├── project_tracking/
│   ├── __init__.py
│   ├── project_tracking_model.py
│   ├── project_tracking_route.py
│   ├── project_tracking_schema.py
│   └── project_tracking_service.py
├── projects/
│   ├── coisa.py
│   ├── projects_model.py
│   ├── projects_route.py
│   ├── projects_schema.py
│   └── projects_services.py
├── time_tracking/
│   ├── __init__.py
│   ├── time_tracking_model.py
│   ├── time_tracking_route.py
│   ├── time_tracking_schema.py
│   ├── time_tracking_services.py
│   └── todo.txt
├── users/
│   ├── __init__.py
│   ├── users_model.py
│   ├── users_route.py
│   ├── users_schema.py
│   └── users_service.py
├── utilities/
│   ├── limiter/
│   │   └── limiter.py
│   └── storage/
│       └── storage_service.py
├── .dockerignore
├── .env.example
├── .gitignore
├── alembic.ini
├── config.yaml
├── Dockerfile
├── errors_tracking.md
├── README.md
└── requirements.txt
```

## 🚀 Instalação

1. Clone o repositório e acesse a pasta do projeto.
2. Crie e ative um ambiente virtual e instale as dependências:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
pip install -r requirements.txt
```

3. Copie `.env.example` para `.env` e preencha `.env` usando `.env.example` como referência, incluindo PostgreSQL, JWT, SMTP, armazenamento S3/R2 e AbacatePay. O carregador de configuração precisa resolver todos os valores declarados em `config.yaml`. O `config.yaml` lê esses valores do ambiente.
4. Inicie a aplicação na raiz do repositório:

```bash
uvicorn core.main:app --reload
```

Acesse <http://127.0.0.1:8000>. Na inicialização, a aplicação cria as tabelas declaradas pelos modelos; o projeto também inclui histórico de migrações Alembic.

## 📌 Funcionalidades

✔️ Cadastro, autenticação, verificação de e-mail e gestão de empresas

✔️ Estoque, movimentações e códigos de barras

✔️ Produção, contatos e projetos com fotos, PDFs e comentários

✔️ Painel financeiro, vendas, pagamentos e contas a receber

✔️ Acompanhamento de projetos com etapas, atrasos, arquivos e links públicos

✔️ Cronogramas semanais compartilháveis

✔️ Registro de horas e relatórios

✔️ Notificações em tempo real por WebSocket

✔️ Módulos por empresa e assinaturas com AbacatePay

ℹ️ O código atual não inclui um agente de IA.

## 🤝 Contribuição

Todos são bem-vindos para contribuir com este sistema e com o futuro SaaS.

***Para contribuir, siga estes passos:***

1. Faça um **fork** do repositório
2. Crie uma nova branch:

```bash
# Crie e alterne para a branch
> git checkout -b feature/nova-funcionalidade

# Adicione as alterações
> git add .

# Faça o commit
> git commit -m 'nova_funcionalidade'

# Envie a branch
> git push origin feature/nova-funcionalidade

# Abra um Pull Request no GitHub
```

## 📏 Padrões do Projeto

Este projeto segue uma estrutura modular estrita para manter escalabilidade, ordem e manutenibilidade.

---

## 🧱 Estrutura modular obrigatória

Cada nova funcionalidade deve ser criada como um **módulo independente**.

### 📌 Regra Principal:
> Uma pasta para cada parte específica do sistema.

Exemplo:
```
erm/
├── users/
├── inventory/
├── financery/
├── contacts/
└── new_module/
```

---

## 📁 Estrutura obrigatória de cada módulo

Cada módulo deve seguir este padrão:
```
new_module/
├── %_model.py
├── %_service.py
├── %_route.py
└── %_schema.py
```

---

## 🧠 Regras importantes

- ✔️ Não misturar lógica entre módulos
- ✔️ Cada módulo deve ser independente
- ✔️ Não importar lógica interna de outros módulos diretamente
- ✔️ Toda comunicação deve passar por serviços (`service.py`)
- ✔️ Os endpoints sempre vão em `route.py`
- ✔️ Validações sempre em `schema.py`

---

## 🏷️ Convenção de nomes

O estilo já existente deve ser respeitado:

- `users_model.py`
- `inventory_service.py`
- `contacts_route.py`

Para novos módulos:

- `model.py`
- `service.py`
- `route.py`
- `schema.py`

---

## 💬 Convenção de commits

O padrão deve ser seguido:

### Tipos permitidos:

- `feat:` nova funcionalidade
- `fix:` correção de bugs
- `refactor:` melhorias de código sem alterar a lógica
- `docs:` mudanças na documentação
- `test:` testes
- `chore:` manutenção geral

### Exemplos:

```bash
git commit -m "feat: add inventory stock validation"
git commit -m "fix: correct user authentication bug"
git commit -m "refactor: improve service layer structure"
```

#### # Para testes, você pode remover as linhas que salvam as informações de e-mail, mas se quiser preenchê-las e ver todas as funcionalidades do sistema, pode acessar essas informações diretamente do seu aplicativo de e-mail.

#### * Por favor, siempre crie branches a partir da main, desenvolva o módulo desejado seguindo a estrutura obrigatória, agradeço a compreensão de todos.
