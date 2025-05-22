# Changelog

## [0.1.0] - 2025-05-22

### Added
- Service layer `backend/reviews/services/review_services.py` con el algoritmo `update_elo_score` y documentación exhaustiva.
- Documentación detallada en `backend/reviews/models.py` (comentarios pedagógicos y guías de escalado).
- Enumeración `StatusChoices` y clase de utilidades `Settings` para parámetros globales.
- Migración inicial para crear las tablas `Product` y `Review`.

### Fixed
- Importación circular entre `models.py` y `review_services.py`.
- Error `choices` en el campo `status` de `Review`.
- Constraint que referenciaba campos inexistentes eliminado.
- Método `__str__` que usaba atributos inexistentes corregido.
- Problemas de importación en shell asegurando que la app esté en `INSTALLED_APPS`.

### Changed
- Lógica de puntuación Elo movida del modelo al servicio (principio de responsabilidad única).
- Moderación de reseñas actualizada para usar `StatusChoices`.
- Limpieza general del modelo `Review` y mejora de legibilidad.
