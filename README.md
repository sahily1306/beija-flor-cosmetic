# Contabilidad

Aplicación web de tienda y gestión contable desarrollada con Django. Usa SQLite por defecto para desarrollo local.

## Requisitos

- Python 3.12 o superior
- Git (opcional, para clonar el repositorio)

## Instalación en Windows (PowerShell)

```powershell
git clone <URL_DEL_REPOSITORIO>
cd contabilidad
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abre `http://127.0.0.1:8000/` para la tienda y `http://127.0.0.1:8000/admin/` para administrar productos y pedidos.

En macOS/Linux, activa el entorno con `source .venv/bin/activate` después de crearlo con `python3 -m venv .venv`.

## Configuración

El proyecto usa valores locales seguros para desarrollo. Antes de desplegarlo, configura estas variables en el proveedor de hosting y no publiques sus valores:

- `DJANGO_SECRET_KEY`: clave secreta aleatoria y privada.
- `DJANGO_DEBUG`: establece `False` en producción.
- `DJANGO_ALLOWED_HOSTS`: dominios permitidos separados por comas, por ejemplo `tienda.example.com`.
- `DJANGO_CSRF_TRUSTED_ORIGINS`: orígenes HTTPS separados por comas, por ejemplo `https://tienda.example.com`.

GitHub Releases publica y versiona el código, pero no aloja ni ejecuta el servidor. Para que la tienda esté disponible en Internet hace falta desplegarla en un proveedor de hosting. La base de datos SQLite local y los archivos ignorados por Git no forman parte de una Release; crea los productos desde el panel de administración después de iniciar el proyecto.

## Comprobaciones

```powershell
python manage.py check
python manage.py test
python manage.py makemigrations --check --dry-run
```

GitHub Actions ejecuta estas comprobaciones al hacer push o abrir un pull request.
