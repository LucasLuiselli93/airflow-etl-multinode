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

INSERT INTO importaciones_maritimas (nro_booking, buque_nombre, contenedor_tipo, pais_origen, puerto_destino, peso_bruto_kg, valor_fob_usd, fecha_arribo_estimada, estado_despacho) VALUES
('BK-1001', 'MSC DIANA', '40HC', 'China', 'Buenos Aires', 18500.00, 45000.00, '2026-05-15', 'Pendiente'),
('BK-1002', 'MAERSK SEOUL', '20ST', 'Brasil', 'Buenos Aires', 12000.50, 15000.00, '2026-05-10', 'Liberado'),
('BK-1003', 'CMA CGM MARCO POLO', '40HC', 'Alemania', 'Buenos Aires', 22000.00, 89000.00, '2026-05-20', 'En Canal'),
('BK-1004', 'EVER GIVEN', '40HC', 'China', 'Buenos Aires', 19000.00, 55000.00, '2026-05-25', 'Pendiente'),
('BK-1005', 'HAPAG HAMBURG', '20ST', 'España', 'Buenos Aires', 8500.00, 12000.00, '2026-05-08', 'Liberado'),
('BK-1006', 'MSC DIANA', '40HC', 'China', 'Buenos Aires', 17800.00, 42000.00, '2026-05-15', 'Pendiente'),
('BK-1007', 'ONE INFINITY', '40HC', 'Japón', 'Buenos Aires', 21000.00, 110000.00, '2026-06-01', 'Pendiente'),
('BK-1008', 'MAERSK SEOUL', '20ST', 'Brasil', 'Buenos Aires', 11500.00, 14500.00, '2026-05-10', 'Liberado'),
('BK-1009', 'CMA CGM MARCO POLO', '40HC', 'Alemania', 'Buenos Aires', 23500.00, 95000.00, '2026-05-20', 'En Canal'),
('BK-1010', 'EVER GIVEN', '40HC', 'China', 'Buenos Aires', 20000.00, 60000.00, '2026-05-25', 'Pendiente');