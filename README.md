# MatiLab

Práctica de matemáticas para 3.º a 6.º grado. Cuatro módulos —aritmética, fracciones, geometría y razonamiento lógico— con 32 lecciones y 128 ejercicios. Cada lección explica una idea, muestra un ejemplo y corrige al instante.

La interfaz usa la estética de un curso visual: fondo cálido, títulos en serif, controles en pastilla, un verde para la acción principal e ilustraciones propias. El nombre, los dibujos y los problemas son de MatiLab.

## Cómo verla

Hace falta Python 3.12 o más nuevo. En esta máquina sirve `python3.13`.

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Abre http://127.0.0.1:8000.

Sin variables de entorno, el progreso queda en el navegador y, mientras el proceso vive, también en memoria. La práctica funciona igual.

## Repertorio

| Módulo | Qué practica |
| --- | --- |
| Aritmética | Llevadas, préstamo, tablas, multiplicación, división, residuo, orden de operaciones y problemas |
| Fracciones | Partes, lectura, equivalentes, comparación, suma, resta, fracción de una cantidad y mixtos |
| Geometría | Figuras, lados, perímetro, áreas, simetría, ángulos y volumen |
| Razonamiento lógico | Patrones, series, verdadero o falso, deducción, clasificar, caminos, edades y pensar al revés |

El filtro de grado muestra solo las lecciones de ese grado. El contenido está en `app/catalog.py`.

## Supabase

El ingreso es un código de 6 números al correo del representante. En el registro también van el nombre del estudiante, su grado y la institución. Ese grado abre sus lecciones; las de otros grados se ven bloqueadas hasta que el representante elige verlas.

1. Crea un proyecto en Supabase.
2. Ejecuta `supabase/schema.sql` en el editor SQL.
3. En Authentication → Email Templates → Magic Link, muestra el código: `Tu código de MatiLab es {{ .Token }}`.
4. Copia `.env.example` a `.env` y completa `SUPABASE_URL`, `SUPABASE_ANON_KEY` y `SUPABASE_SERVICE_ROLE_KEY`.
5. Arranca el servidor con esas variables. En Vercel se cargan en los ajustes del proyecto, no en el navegador.

Sin esas claves, MatiLab sigue funcionando: el código aparece en la pantalla de entrada y los datos viven en la memoria del proceso. La racha cuenta un día de Venezuela cuando el estudiante responde al menos una práctica.

La service role no debe publicarse. Las tablas tienen RLS activado y no hay políticas públicas: solo el servidor entra.

## Vercel

El proyecto es una app FastAPI. Vercel detecta `app/main.py`. Los archivos de `public/` se sirven como estáticos.

```bash
vercel
```

En el proyecto de Vercel agrega las variables de Supabase y vuelve a desplegar.

## Pruebas

```bash
pytest
```
