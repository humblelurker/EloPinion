


# 🏗️ Arquitectura del Backend de EloPinion

El backend de este proyecto está construido utilizando **Django** y sigue una **arquitectura monolítica modular**. Esto significa que todo el código del backend está contenido en un único proyecto Django, pero está organizado en módulos (apps) que encapsulan funcionalidades específicas. Además, se implementa una **separación en capas** para mantener la claridad y la escalabilidad del código.

---

## 📦 Estructura General

El proyecto se organiza bajo un único módulo `backend/`, dentro del cual se crean múltiples apps según las funcionalidades. Ejemplos:

- `api/`: Contiene la lógica de negocio y los endpoints principales.
- `auth/`: Maneja la autenticación y el registro de usuarios.
- `reviews/`: Gestiona productos y reseñas, incluyendo puntuaciones Elo.

---

## 🧱 Separación en Capas

Cada app sigue un diseño limpio y escalable mediante subcarpetas que representan distintas responsabilidades:

| Carpeta         | Propósito |
|-----------------|-----------|
| `views_hu/`     | Vistas específicas para cada Historia de Usuario (HU). |
| `urls_hu/`      | Rutas asociadas a vistas de HU. |
| `serializers/`  | Serialización de datos (JSON ↔️ Python). |
| `services/`     | Lógica de negocio (cálculos, métricas, etc). |
| `utils/`        | Utilidades generales (PDFs, gráficas, helpers). |
| `permissions/`  | Permisos personalizados. |

---

## 🧠 Capas de Abstracción

1. **Modelos (`models.py`)**  
   Representan las entidades principales (e.g. `Product`, `Review`). Incluyen validaciones básicas.

2. **Servicios (`services/`)**  
   Contienen lógica de negocio compleja, como el cálculo de métricas o puntuaciones.

3. **Vistas (`views.py` o `views_hu/`)**  
   Reciben solicitudes HTTP, validan y delegan al servicio correspondiente.

4. **Serializadores (`serializers/`)**  
   Manejan transformación de datos entre el frontend y backend.

---

## 🧭 Estándares de Desarrollo

- Todas las apps siguen una estructura común.
- `views_hu` y `urls_hu` agrupan por HU, facilitando el trabajo en equipo.
- Código fácil de navegar, extender y mantener.

---

## 🔗 Comunicación con el Frontend

- API RESTful conectada a un frontend en **React**.
- Se utiliza `django-cors-headers` para permitir solicitudes cross-origin durante desarrollo.

---

## ⚙️ Configuración Global

- Centralizada en `settings.py`.
- Define:
  - Conexión a base de datos.
  - Apps instaladas.
  - Configuración de CORS.
  - Middlewares y otros ajustes.

---

## 📁 Estructura por App (Ejemplo)

```
app/
├── models.py
├── views.py
├── urls.py
├── serializers/
├── services/
├── utils/
├── permissions/
├── views_hu/
└── urls_hu/
```

---

Esta arquitectura busca **maximizar la claridad, la cohesión y la separación de responsabilidades**, facilitando el trabajo en equipo y el crecimiento del proyecto a futuro.