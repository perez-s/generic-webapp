CREATE TYPE aforo_residue_type AS ENUM (
    'Mezclado',
    'Orgánico',
    'Cartón',
    'Vidrio',
    'Tetra Pak',
    'PET',
    'Roturas'
);

CREATE TYPE aforo_container_type AS ENUM (
    'Bolsas',
    'Big Bags',
    'Tinas',
    'Pacas',
    'Cajas'
);