# Mantenimiento del diario

## Objetivo

Este documento reúne las tareas habituales de mantenimiento del proyecto.

El objetivo no es añadir nuevas funcionalidades, sino conservar el diario estable, ordenado y fácil de mantener a lo largo del tiempo.

---

## Organización del proyecto

Mantener siempre la misma estructura de directorios.

No renombrar carpetas ni mover archivos sin un motivo claro.

Si el proyecto cambia de ubicación en el ordenador, comprobar después que:

- Git funciona correctamente.
- Hugo genera el sitio sin errores.
- El repositorio remoto sigue configurado.

---

## Actualizar Hugo

Antes de actualizar Hugo:

1. comprobar la versión instalada.

```bash
hugo version
```

2. leer los cambios de la nueva versión.

3. realizar una copia de seguridad del proyecto.

4. actualizar Hugo.

5. reconstruir el sitio.

```bash
hugo
```

6. comprobar que no aparecen errores.

No actualizar Hugo únicamente porque exista una versión nueva.

---

## Revisar enlaces

Periódicamente conviene comprobar que:

- el menú principal funciona;
- las páginas principales existen;
- los enlaces internos siguen siendo válidos;
- las imágenes se muestran correctamente.

---

## Revisar el sitio

Antes de publicar una nueva versión recorrer siempre el diario como si se fuera un lector.

Prestar atención a:

- títulos;
- fechas;
- tipografía;
- espaciado;
- navegación;
- textos.

Los pequeños errores suelen detectarse durante una lectura tranquila.

---

## Mantener la simplicidad

Evitar añadir nuevas funciones si no resuelven un problema real.

Cada elemento nuevo aumenta la complejidad del proyecto.

Siempre que exista una solución sencilla y otra más compleja que produzcan el mismo resultado, elegir la más sencilla.

---

## Reflexión

El mantenimiento consiste, sobre todo, en conservar.

Un proyecto bien mantenido no es el que acumula más funciones, sino el que continúa siendo comprensible después de muchos años.

La mejor mejora suele ser aquella que hace el diario un poco más claro sin llamar la atención sobre sí misma.
