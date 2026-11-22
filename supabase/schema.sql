-- MatiLab: progreso del estudiante.
-- Ejecuta este script en el editor SQL de Supabase.
-- La app usa SUPABASE_SERVICE_ROLE_KEY solo en el servidor.
-- Esa clave omite RLS. El navegador no habla con Supabase.

create table if not exists public.students (
  id uuid primary key,
  display_name text not null default 'Estudiante',
  grade smallint not null default 4 check (grade between 3 and 6),
  created_at timestamptz not null default now()
);

create table if not exists public.lesson_progress (
  student_id uuid not null references public.students (id) on delete cascade,
  lesson_id text not null,
  solved text[] not null default '{}',
  correct text[] not null default '{}',
  completed boolean not null default false,
  updated_at timestamptz not null default now(),
  primary key (student_id, lesson_id)
);

alter table public.students enable row level security;
alter table public.lesson_progress enable row level security;
