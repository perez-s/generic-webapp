CREATE TYPE status_type AS ENUM (
    'Pendiente',
    'Programada',
    'Cancelada',
    'Completada'
);

CREATE TYPE residue_category AS ENUM (
    'Aceites usados',
    'Pilas',
    'Biosanitarios',
    'RAEE',
    'Pinturas',
    'Luminarias',
    'Otros peligrosos',
    'Sólidos con aceite',
    'Aerosoles',
    'Baterías',
    'Tóneres',
    'Baterías de ion litio'
);

CREATE TYPE activities_performed AS ENUM (
    'Recolección y transporte',
    'Tratamiento',
    'Disposición final',
    'Aprovechamiento'
);

CREATE TYPE category AS ENUM (
    'RESPEL',
    'RCD',
    'Ordinarios',
    'Madera'
);

CREATE TYPE measure_unit AS ENUM (
    'kg',
    'm3',
    'cajas'
);

CREATE TABLE if NOT exists public.residuo_corriente (
    id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
    residuo_name text NOT NULL UNIQUE,
    corriente_name text NULL,
    corriente_code text NULL,
    CONSTRAINT residuo_corriente_pkey PRIMARY KEY (id)
);

CREATE TABLE if NOT exists public.users (
    id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
    username text NOT NULL,
    CONSTRAINT users_pkey PRIMARY KEY (id)
);

CREATE TABLE if NOT exists public.providers (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  userid bigint NOT NULL,
  provider_name text NOT NULL,
  provider_nit bigint NOT NULL UNIQUE,
  provider_email text NOT NULL DEFAULT 'example@mail.com',
  provider_contact_phone bigint NOT NULL DEFAULT 1234567890,
  provider_contact text NOT NULL,
  provider_category residue_category[] NULL,
  provider_activity activities_performed[] NULL,
  lic_amb_path text,
  rut_path text NOT NULL,
  ccio_path text NOT NULL,
  other_docs_path text,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  updated_at timestamp with time zone NOT NULL DEFAULT now(),
  certificado_bancario_path text,
  provider_website text DEFAULT 'example.com',
  provider_is_active boolean NOT NULL DEFAULT true,
  CONSTRAINT providers_pkey PRIMARY KEY (id),
  CONSTRAINT providers_username_fkey FOREIGN KEY (userid) REFERENCES public.users(id) on update CASCADE
);

CREATE TABLE if NOT exists public.allies (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  ally_name text NOT NULL,
  lic_amb_path text NOT NULL,
  provider_id bigint NOT NULL,
  CONSTRAINT allies_pkey PRIMARY KEY (id),
  CONSTRAINT allies_provider_id_fkey FOREIGN KEY (provider_id) REFERENCES public.providers(id) on update CASCADE
);

CREATE TABLE if NOT exists public.requests (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  userid bigint not null,
  estimated_amount real not null,
  details text,
  admin_note text,
  created_at timestamp with time zone not null DEFAULT now(),
  updated_at timestamp with time zone not null DEFAULT now(),
  request_category residue_category[] not null,
  measure_type measure_unit not null,
  current_status status_type not null default 'Pendiente'::status_type,
  constraint requests_pkey primary key (id),
  constraint requests_username_fkey foreign KEY (userid) references users (id) on update CASCADE
);

CREATE TABLE if NOT exists public.pickup (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  userid bigint not null,
  providerid bigint not null,
  pickup_date date not null,
  cert_recoleccion_path text,
  created_at timestamp with time zone not null DEFAULT now(),
  updated_at timestamp with time zone not null DEFAULT now(),
  admin_note text,
  pickup_status status_type not null default 'Programada'::status_type,
  cert_transformacion_path text,
  otros_documentos_path text,
  constraint pickup_pkey primary key (id),
  constraint pickup_providerid_fkey foreign KEY (providerid) references providers (id) on update CASCADE,
  constraint pickup_userid_fkey foreign KEY (userid) references users (id) on update CASCADE
);

CREATE TABLE if NOT exists public.pickup_requests (
  pickup_id bigint not null,
  request_id bigint not null,
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  constraint pickup_requests_pkey primary key (id),
  constraint pickup_requests_pickup_id_fkey foreign KEY (pickup_id) references pickup (id) on update CASCADE,
  constraint pickup_requests_request_id_fkey foreign KEY (request_id) references requests (id) on update CASCADE
);

CREATE TABLE if NOT exists public.residues_collected (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  created_at timestamp with time zone not null default now(),
  updated_at timestamp with time zone not null default now(),
  residue_category text not null,
  pickup_id bigint not null,
  real_ammount real not null,
  measure_type measure_unit not null,
  category category not null default 'RESPEL'::category,
  constraint residues_collected_pkey primary key (id),
  constraint residues_collected_residue_category_fkey foreign KEY (residue_category) references residuo_corriente (residuo_name) on update CASCADE,
  constraint residues_collected_pickup_id_fkey foreign KEY (pickup_id) references pickup (id) on update CASCADE
)

