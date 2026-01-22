-- Create clients table
CREATE TABLE IF NOT EXISTS public.clients (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  razon_social text NOT NULL UNIQUE,
  correo text,
  nit text,
  telefono text,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  updated_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT clients_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.sucursal (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  etapa text,
  cliente_id bigint NOT NULL,
  sucursal text,
  ciudad text,
  direccion text,
  barrio text,
  correo text,
  nit text,
  telefono text,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  updated_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT sucursal_pkey PRIMARY KEY (id),
  CONSTRAINT sucursal_cliente_id_fkey FOREIGN KEY (cliente_id) REFERENCES public.clients(id) ON UPDATE CASCADE
);

-- Create pickup companies table (to associate vehicles with a company)
CREATE TABLE IF NOT EXISTS public.pickup_companies (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  company_name text NOT NULL UNIQUE,
  nit text,
  contact text,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  updated_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT pickup_companies_pkey PRIMARY KEY (id)
);

-- -- Create vehicles table (cars / plates) linked to a pickup company
-- CREATE TABLE IF NOT EXISTS public.vehicles (
--   id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
--   plate text NOT NULL UNIQUE,
--   company_id bigint NOT NULL,
--   created_at timestamp with time zone NOT NULL DEFAULT now(),
--   updated_at timestamp with time zone NOT NULL DEFAULT now(),
--   CONSTRAINT vehicles_pkey PRIMARY KEY (id),
--   CONSTRAINT vehicles_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.pickup_companies(id) ON UPDATE CASCADE
-- );

CREATE TABLE IF NOT EXISTS public.todays_route (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  username text NOT NULL,
  ciudad_today text NOT NULL,
  vehicle_plate text NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT todays_route_pkey PRIMARY KEY (id),
  CONSTRAINT todays_route_username_fkey FOREIGN KEY (username) REFERENCES public.users(username) ON UPDATE CASCADE
);

-- Create aforos table linking a client (razon_social -> client id) and a vehicle (plate -> vehicle id)
CREATE TABLE IF NOT EXISTS public.aforos (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  vehiculo_placa text,
  operario_name text,
  sucursal_id bigint NOT NULL,
  evidencia_fachada text,
  evidencia_residuos text,
  nombre_firma text,
  cedula_firma integer,
  firma text,
  observaciones text,
  latitude double precision,
  longitude double precision,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  updated_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT aforos_pkey PRIMARY KEY (id),
  CONSTRAINT aforos_sucursal_id_fkey FOREIGN KEY (sucursal_id) REFERENCES public.sucursal(id) ON UPDATE CASCADE,
  CONSTRAINT aforos_operario_name_fkey FOREIGN KEY (operario_name) REFERENCES public.users(username) ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS public.aforos_residues (
  residuo text,
  weight real,
  contenedor text,
  cantidad_contenedores integer,
  aforo_id bigint NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  updated_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT aforos_residues_aforo_id_fkey FOREIGN KEY (aforo_id) REFERENCES public.aforos(id) ON UPDATE CASCADE
);
-- Attach update triggers to keep `updated_at` current (uses existing function `update_updated_at_column`)
CREATE TRIGGER update_clients_updated_at
BEFORE UPDATE ON public.clients
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_sucursal_updated_at
BEFORE UPDATE ON public.sucursal
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_pickup_companies_updated_at
BEFORE UPDATE ON public.pickup_companies
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_aforos_residues_updated_at
BEFORE UPDATE ON public.aforos_residues
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();

-- CREATE TRIGGER update_vehicles_updated_at
-- BEFORE UPDATE ON public.vehicles
-- FOR EACH ROW
-- EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_aforos_updated_at
BEFORE UPDATE ON public.aforos
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();

-- Indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_clients_razon_social ON public.clients(razon_social);

-- Comments
COMMENT ON TABLE public.clients IS 'Stores client information (Razón social and contact/address data)';
-- COMMENT ON TABLE public.vehicles IS 'Vehicle records (plate numbers) linked to pickup companies';
COMMENT ON TABLE public.aforos IS 'Aforos records linked to clients and vehicle plates';