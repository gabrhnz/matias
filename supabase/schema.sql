-- MatiLab: cuentas y progreso.
-- Ejecuta este script en el editor SQL de Supabase.
-- La app usa la service role solo en el servidor. El navegador no habla con Supabase.
-- El ingreso es un código al correo, por Supabase Auth.
-- En Authentication → Email Templates → Magic Link, deja el código visible:
--   Tu código de MatiLab es {{ .Token }}

create table if not exists public.students (
  id uuid primary key,
  display_name text not null default 'Estudiante',
  grade smallint not null default 4 check (grade between 3 and 6),
  email text,
  guardian_name text,
  school text,
  streak integer not null default 0,
  last_active date,
  created_at timestamptz not null default now()
);

alter table public.students add column if not exists email text;
alter table public.students add column if not exists guardian_name text;
alter table public.students add column if not exists school text;
alter table public.students add column if not exists streak integer not null default 0;
alter table public.students add column if not exists last_active date;

create unique index if not exists students_email_unique on public.students (email);

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
