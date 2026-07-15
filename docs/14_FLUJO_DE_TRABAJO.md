# Manual del editor

## Documento 14 · Flujo de trabajo

---

# Objetivo

Definir una forma de trabajar constante.

Seguir siempre el mismo procedimiento reduce errores, facilita el mantenimiento del proyecto y permite retomar el trabajo después de cualquier pausa.

---

# Flujo habitual

## 1. Crear o modificar contenido

Realizar todos los cambios en la rama `develop`.

Nunca trabajar directamente sobre `main`.

---

## 2. Probar el resultado

Ejecutar Hugo en local.

```bash
hugo server
```

Recorrer el sitio como si se fuera un lector.

Comprobar:

- navegación;
- páginas;
- enlaces;
- fechas;
- tipografía;
- legibilidad.

---

## 3. Revisar los cambios

Consultar el estado del repositorio.

```bash
git status
```

Revisar que únicamente aparecen los archivos previstos.

---

## 4. Guardar el trabajo

Añadir los cambios.

```bash
git add .
```

Crear un commit.

```bash
git commit -m "Descripción breve del cambio"
```

Los mensajes deben ser claros y describir el motivo del cambio.

---

## 5. Publicar

Cambiar a la rama principal.

```bash
git checkout main
```

Fusionar los cambios.

```bash
git merge develop
```

Enviar el proyecto a GitHub.

```bash
git push origin main
```

Netlify iniciará automáticamente el despliegue.

---

## 6. Comprobar la publicación

Esperar a que finalice el despliegue.

Recorrer nuevamente el sitio publicado.

No dar por terminada una sesión sin comprobar el resultado final.

---

# Principios

Trabajar despacio.

Hacer un cambio cada vez.

Comprobar siempre el resultado antes de continuar.

Cuando aparezca un problema, resolverlo antes de comenzar otra tarea.

La simplicidad tiene prioridad sobre la complejidad.

---

# Reflexión

Un buen flujo de trabajo no sirve únicamente para producir cambios.

Sirve, sobre todo, para conservar la tranquilidad.

Cuando cada paso tiene un orden conocido, desaparece la necesidad de improvisar y el proyecto puede crecer sin perder claridad.
