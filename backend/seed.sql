-- 1. Insertamos Usuarios con TODOS los campos
INSERT INTO Usuarios (OidAzure, Nombre, Rol, Sede, Activo, TipoContrato, HorasDiariasVerano, HorasInvierno_L_J, HorasInvierno_Viernes, FechaCreacion, FechaDesactivacion, DesactivadoPorUsuarioId) 
VALUES 
('usr-001-azure', 'Elena Navarro', 'JP', 'Madrid', 1, '40H', 7.00, 8.50, 6.50, GETDATE(), NULL, NULL),
('usr-002-azure', 'Miguel Poveda', 'Tecnico', 'Barcelona', 1, '40H', 7.00, 8.50, 6.50, GETDATE(), NULL, NULL),
('usr-003-azure', 'Sara Ruiz', 'Tecnico', 'Valencia', 0, 'MediaJornada', 4.00, 4.00, 4.00, '2025-01-10', GETDATE(), 1);
GO

-- 2. Insertamos Clientes (necesarios para los proyectos)
INSERT INTO Clientes (Nombre, Codigo, Estado, FechaCreacion, FechaDesactivacion, DesactivadoPorUsuarioId)
VALUES 
('Banco Central Hispano', 'CLI-BCH', 1, GETDATE(), NULL, NULL),
('Tech Solutions S.L.', 'CLI-TECH', 0, '2024-05-20', GETDATE(), 1);
GO

-- 3. Insertamos Proyectos (Usando la JP Elena Navarro, que tendrá el Id 2)
INSERT INTO Proyectos (ClienteId, Nombre, Codigo, Tipo, JefeProyectoId, Estado, FechaInicio, FechaFin, FechaCreacion, FechaDesactivacion, DesactivadoPorUsuarioId)
VALUES 
(1, 'Migración Cloud 2026', 'PRJ-CLOUD-01', 'Proyecto', 2, 'Activo', '2026-03-01', '2026-12-31', GETDATE(), NULL, NULL),
(2, 'Mantenimiento App', 'PRJ-MANT-02', 'Mantenimiento', 2, 'Cerrado', '2025-01-01', '2025-12-31', '2025-01-01', GETDATE(), 1);
GO