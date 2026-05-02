DROP TABLE IF EXISTS importaciones_maritimas;

CREATE TABLE importaciones_maritimas (
    id SERIAL PRIMARY KEY,
    nro_booking VARCHAR(20),
    buque_nombre VARCHAR(50),
    contenedor_tipo VARCHAR(10), -- 20ST, 40HC, etc.
    pais_origen VARCHAR(30),
    puerto_destino VARCHAR(30),
    peso_bruto_kg DECIMAL(10, 2),
    valor_fob_usd DECIMAL(12, 2),
    fecha_arribo_estimada DATE,
    estado_despacho VARCHAR(20) -- Pendiente, En Canal, Liberado
);

INSERT INTO importaciones_maritimas (
    nro_booking, buque_nombre, contenedor_tipo, pais_origen, 
    puerto_destino, peso_bruto_kg, valor_fob_usd, 
    fecha_arribo_estimada, estado_despacho
)
SELECT 
    'BK-' || (1000 + s.i) AS nro_booking,
    (ARRAY['MSC DIANA', 'MAERSK SEOUL', 'CMA CGM MARCO POLO', 'EVER GIVEN', 'HAPAG HAMBURG', 'ONE INFINITY'])[floor(random() * 6 + 1)] AS buque_nombre,
    (ARRAY['20ST', '40HC'])[floor(random() * 2 + 1)] AS contenedor_tipo,
    (ARRAY['China', 'Brasil', 'Alemania', 'España', 'Japón', 'USA'])[floor(random() * 6 + 1)] AS pais_origen,
    'Buenos Aires' AS puerto_destino,
    (random() * 25000 + 5000)::DECIMAL(10,2) AS peso_bruto_kg,
    (random() * 100000 + 10000)::DECIMAL(12,2) AS valor_fob_usd,
    '2026-05-01'::DATE + (random() * 90)::INT AS fecha_arribo_estimada,
    (ARRAY['Pendiente', 'En Canal', 'Liberado'])[floor(random() * 3 + 1)] AS estado_despacho
FROM generate_series(1, 500000) AS s(i);