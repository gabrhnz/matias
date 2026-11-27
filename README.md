# MatiLab

Práctica de matemáticas para 3.º a 6.º grado. El niño elige un módulo, resuelve cuatro ejercicios y ve en el momento si acertó.

**Sitio:** [matiaslab.vercel.app](https://matiaslab.vercel.app)  
**Guion de la presentación:** [presentacion.md](presentacion.md)

Hecho en la Universidad Nacional de las Ciencias. Las bases de la escuela sostienen lo que después se estudia, y MatiLab pone esas bases a practicar.

## Equipo

| | |
| --- | --- |
| Gabriel | Desarrollo |
| María Belinda | Diseño y frontend |
| Carol | Contenido y pedagogía |
| Gure | Pruebas, errores y soluciones |

## Qué hay

Cuatro módulos, 32 lecciones y 128 ejercicios. Cada lección trae una idea corta, un ejemplo y una pista. La pista empuja sin dar la respuesta.

| Módulo | Qué practica |
| --- | --- |
| Aritmética | Sumas, restas, tablas, multiplicación, división y problemas |
| Fracciones | Partes de un entero, comparar, sumar, restar y números mixtos |
| Geometría | Figuras, perímetro, área, ángulos y volumen |
| Razonamiento lógico | Patrones, verdadero o falso, clasificar y deducir |

La cuenta la crea el representante: su nombre, su correo, y después el nombre del estudiante, el grado y la escuela. El estudiante practica las lecciones de su grado. Las demás se pueden ver como repaso, sin cambiar el grado de la cuenta.

Quien todavía no tiene cuenta responde tres preguntas y, al terminar, crea la cuenta.

## Cómo se aprueba

Cada ejercicio vale lo mismo. Uno bien de cuatro es 25 sobre 100. Tres bien son 75.

- Una lección se aprueba con **al menos 75 sobre 100**.
- Un módulo se aprueba cuando **cada lección de ese grado** llega a 75. No hay promedio.
- Si no llega, el botón es «Intentar otra vez». Repetir solo puede subir el puntaje guardado.
- El resultado no avanza solo: se queda en Correcto o Incorrecto hasta pulsar Seguir.

## Cómo funciona

La respuesta correcta no viaja al navegador. El niño envía lo que eligió y el servidor dice si está bien.

1. De los cuatro ejercicios, se empieza por uno normal. Dos errores seguidos bajan a uno más fácil. Tres aciertos seguidos cierran con uno más difícil.
2. El grado se cumple en el servidor. Escribir la dirección de una lección de otro grado no deja responderla, salvo que se pida el repaso.
3. El ingreso es un código de **8 dígitos** que Supabase envía al correo del representante.
4. La racha cuenta un día de Venezuela si el estudiante respondió al menos un ejercicio.

El detalle, y lo que explica cada quien, está en [presentacion.md](presentacion.md).

## Stack

| Pieza | Para qué |
| --- | --- |
| Python y FastAPI | El servidor, las páginas y la corrección |
| Jinja | El HTML |
| HTML, CSS y JavaScript | Lo que ve y pulsa el niño |
| Supabase | La cuenta, el código al correo y el progreso |
| Vercel | El sitio publicado. Se actualiza con la rama `cursor/matilab-plataforma` |
| pytest | Las pruebas del repertorio, el puntaje y el bloqueo por grado |

El navegador no habla con la base de datos. Solo habla con MatiLab.

## Cómo correrlo

Hace falta Python 3.12 o más nuevo.

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Abre http://127.0.0.1:8000.

Sin variables de entorno la práctica funciona igual: el código de entrada aparece en la pantalla y el progreso queda en memoria mientras el proceso vive.

Para cuentas y progreso de verdad:

1. Crea un proyecto en Supabase y ejecuta [`supabase/schema.sql`](supabase/schema.sql).
2. En Authentication → Email Templates → Magic Link, deja el código visible: `Tu código de MatiLab es {{ .Token }}`.
3. Copia [`.env.example`](.env.example) a `.env` y completa `SUPABASE_URL`, `SUPABASE_ANON_KEY` y `SUPABASE_SERVICE_ROLE_KEY`.

La service role no se publica. Las tablas tienen RLS activado y no hay políticas públicas: solo el servidor entra. En Vercel esas variables van en los ajustes del proyecto, no en el navegador.

## Pruebas

```bash
pytest
```
