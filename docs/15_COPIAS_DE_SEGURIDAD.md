# Manual del editor

## Documento 15 · Copias de seguridad

---

# Objetivo

Garantizar que el diario pueda recuperarse en cualquier momento.

El proyecto utiliza Git y GitHub, pero una copia de seguridad adicional proporciona tranquilidad ante cualquier incidencia.

---

# Qué debe conservarse

El proyecto completo.

Especialmente:

- content/
- layouts/
- static/
- config.toml
- docs/
- .git/

No es necesario copiar únicamente los textos. La estructura del proyecto también forma parte del diario.

---

# Cuándo realizar una copia

Conviene hacer una copia:

- antes de actualizar Hugo;
- antes de cambios importantes en la estructura;
- antes de reorganizar el proyecto;
- después de publicar una versión especialmente significativa.

---

# Dónde guardar las copias

Mantener al menos dos ubicaciones diferentes.

Por ejemplo:

- el repositorio de GitHub;
- una copia local en otro disco o dispositivo.

Si es posible, conservar también una copia externa.

---

# Recuperación

Si el proyecto deja de funcionar:

1. recuperar la última copia disponible;
2. comprobar el estado del repositorio;
3. verificar que Hugo genera el sitio correctamente;
4. revisar el funcionamiento de Netlify.

No realizar cambios adicionales hasta confirmar que el proyecto vuelve a estar estable.

---

# Reflexión

Las copias de seguridad no son una muestra de desconfianza.

Son una forma de cuidar el trabajo realizado.

El tiempo dedicado a escribir merece la misma protección que el tiempo dedicado a conservar.
