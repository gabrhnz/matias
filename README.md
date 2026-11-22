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

1. Crea un proyecto en Supabase.
2. Ejecuta `supabase/schema.sql` en el editor SQL.
3. Copia `.env.example` a `.env` y completa `SUPABASE_URL` y `SUPABASE_SERVICE_ROLE_KEY`.
4. Arranca el servidor con esas variables. En Vercel se cargan en los ajustes del proyecto, no en el navegador.

La clave es la **service role**. No uses la clave anónima ni la publiques en el cliente. Las tablas tienen RLS activado y no hay políticas públicas: solo el servidor entra.

## Vercel

El proyecto es una app FastAPI. Vercel detecta `app/main.py`. Los archivos de `public/` se sirven como estáticos.

```bash
vercel
```

En el proyecto de Vercel agrega las dos variables de Supabase y vuelve a desplegar.

## Pruebas

```bash
pytest
```
