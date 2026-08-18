# Protea Consultoría

Sitio web institucional para una consultora estratégica, construido con Django.

## Estructura

- `protea_consultoria/` — configuración del proyecto (settings, urls).
- `core/` — app con las vistas y el contenido de cada página.
- `templates/core/` — plantillas HTML (base + 5 páginas: inicio, servicios, enfoque, nosotros, contacto).
- `static/css/style.css` — sistema de diseño completo (paleta, tipografía, componentes).

## Cómo correrlo

```bash
python3 -m venv venv
source venv/bin/activate        # en Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Luego abre http://127.0.0.1:8000/ en el navegador.

## Páginas incluidas

- `/` — Inicio
- `/servicios/` — Servicios
- `/enfoque/` — Metodología (Raíz → Fuego → Floración)
- `/nosotros/` — Sobre la consultora
- `/contacto/` — Formulario de contacto (visual, sin backend de envío)
