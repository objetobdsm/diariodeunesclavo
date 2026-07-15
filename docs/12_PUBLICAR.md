# Publicar el diario

Este documento describe el procedimiento para publicar una nueva versión del diario.

El proyecto utiliza Git para el control de versiones, GitHub como repositorio remoto y Netlify como plataforma de publicación. El flujo de trabajo consiste en preparar los cambios en la rama `develop`, revisarlos y, cuando estén listos, integrarlos en `main`.

---

## 1. Comprobar el estado del proyecto

Antes de comenzar, verificar que el árbol de trabajo está en el estado esperado.

```bash
git status
```

Consultar también la rama activa.

```bash
git branch
```

---

## 2. Guardar los cambios

Añadir los archivos modificados.

```bash
git add .
```

Crear un commit con un mensaje breve y descriptivo.

```bash
git commit -m "Describe brevemente el cambio"
```

Ejemplos:

```bash
git commit -m "Corrige la página Diario"
git commit -m "Mejora la tipografía"
git commit -m "Añade la página Biblioteca"
```

---

## 3. Integrar los cambios en la rama principal

Cambiar a la rama `main`.

```bash
git checkout main
```

Fusionar la rama de trabajo.

```bash
git merge develop
```

---

## 4. Publicar

Enviar la rama principal a GitHub.

```bash
git push origin main
```

Netlify detectará automáticamente los cambios y comenzará un nuevo despliegue.

---

## 5. Verificar la publicación

Esperar unos segundos hasta que Netlify complete el despliegue.

Comprobar que:

- la página principal carga correctamente;
- las entradas recientes aparecen;
- los enlaces principales funcionan;
- no hay errores visibles.

Si es necesario, realizar una recarga completa del navegador.

---

## Resolución de problemas

Consultar el estado del repositorio.

```bash
git status
```

Ver la rama actual.

```bash
git branch
```

Consultar los últimos commits.

```bash
git log --oneline -5
```

---

## Notas

Nunca trabajar directamente sobre `main`.

Todos los cambios deben realizarse en `develop` y publicarse únicamente cuando hayan sido revisados.

Antes de cada publicación conviene recorrer el sitio como si se fuera un lector más. Es la mejor manera de detectar pequeños errores que pasan desapercibidos durante el desarrollo.
