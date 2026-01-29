-- 1. USUARIOS (Base del sistema)
CREATE TABLE Usuarios (
    Id INT PRIMARY KEY IDENTITY(1,1),
    Nombre NVARCHAR(100) NOT NULL,
    Email NVARCHAR(100) NOT NULL UNIQUE, 
    Rol NVARCHAR(20) CHECK (Rol IN ('Admin', 'JP', 'Tecnico')), 
    Activo BIT DEFAULT 1,

    -- CONFIGURACIÓN DE CONTRATO (Límites teóricos)
    TipoContrato NVARCHAR(20) DEFAULT '40H', 
    HorasDiariasVerano DECIMAL(4,2) DEFAULT 7.00, 
    HorasInvierno_L_J DECIMAL(4,2) DEFAULT 8.50, 
    HorasInvierno_Viernes DECIMAL(4,2) DEFAULT 6.50
);

-- 2. CLIENTES
CREATE TABLE Clientes (
    Id INT PRIMARY KEY IDENTITY(1,1),
    Nombre NVARCHAR(100) NOT NULL,
    Codigo NVARCHAR(50),
    Estado BIT DEFAULT 1
);

-- 3. PROYECTOS
CREATE TABLE Proyectos (
    Id INT PRIMARY KEY IDENTITY(1,1),
    ClienteId INT FOREIGN KEY REFERENCES Clientes(Id),
    Nombre NVARCHAR(100) NOT NULL,
    Codigo NVARCHAR(50),
    Tipo NVARCHAR(20) DEFAULT 'Proyecto', -- Servicio o Proyecto
    JefeProyectoId INT FOREIGN KEY REFERENCES Usuarios(Id), -- El JP asignado
    Estado BIT DEFAULT 1
);

-- 4. CALENDARIO FESTIVOS (NUEVA: Para control de días no laborables globales)
CREATE TABLE CalendarioFestivos (
    Id INT PRIMARY KEY IDENTITY(1,1),
    Fecha DATE NOT NULL UNIQUE, -- Evita duplicar el mismo día
    NombreFestivo NVARCHAR(100) NOT NULL,
);

-- 5. AUSENCIAS Y VACACIONES (Para control de días no laborables personales)
CREATE TABLE Ausencias (
    Id INT PRIMARY KEY IDENTITY(1,1),
    UsuarioId INT FOREIGN KEY REFERENCES Usuarios(Id),
    FechaInicio DATE NOT NULL,
    FechaFin DATE NOT NULL,
    Tipo NVARCHAR(20) CHECK (Tipo IN ('Vacaciones', 'Baja', 'AsuntosPropios')) DEFAULT 'Vacaciones',
    Estado NVARCHAR(20) CHECK (Estado IN ('Solicitado', 'Aprobado', 'Rechazado')) DEFAULT 'Solicitado',
    Comentario NVARCHAR(255) NULL,
    CONSTRAINT CK_Ausencias_Fechas CHECK (FechaFin >= FechaInicio)
);

-- 6. ASIGNACIONES (Define qué usuarios pueden imputar en qué proyecto y cuándo.)

CREATE TABLE Asignaciones (
    Id INT PRIMARY KEY IDENTITY(1,1),
    ProyectoId INT FOREIGN KEY REFERENCES Proyectos(Id),
    UsuarioId INT FOREIGN KEY REFERENCES Usuarios(Id),
    FechaInicio DATE NOT NULL,
    FechaFin DATE NULL, -- NULL indica asignación indefinida
    PorcentajeDedicacion DECIMAL(5,2) DEFAULT 100.00,
    Activo BIT DEFAULT 1
);

-- 7. CIERRES MENSUALES (Bloqueo de imputaciones pasadas)
CREATE TABLE CierresMensuales (
    Id INT PRIMARY KEY IDENTITY(1,1),
    Anio INT NOT NULL,
    Mes INT NOT NULL CHECK (Mes BETWEEN 1 AND 12),
    EstaCerrado BIT DEFAULT 0, -- 1 = Bloqueado, 0 = Abierto
    FechaCierre DATETIME DEFAULT GETDATE(),
    Comentarios NVARCHAR(200)
);
-- Índice único para evitar cerrar dos veces el mismo mes/año
CREATE UNIQUE INDEX IX_Cierres_Anio_Mes ON CierresMensuales(Anio, Mes);

-- 8. IMPUTACIONES / TIMELOG
CREATE TABLE Imputaciones (
    Id BIGINT PRIMARY KEY IDENTITY(1,1),
    UsuarioId INT FOREIGN KEY REFERENCES Usuarios(Id),
    ProyectoId INT FOREIGN KEY REFERENCES Proyectos(Id),
    Fecha DATE NOT NULL,
    Horas DECIMAL(4, 2) NOT NULL,
    Notas NVARCHAR(MAX),
    JustificacionExceso NVARCHAR(255) NULL,   -- Campo para justificar si se supera el límite diario calculado
    EsFestivo BIT DEFAULT 0,     
    EsNoFacturable BIT DEFAULT 0, 
    Estado NVARCHAR(20) DEFAULT 'Borrador'
);

-- Índices para rendimiento
CREATE INDEX IX_Imputaciones_Usuario_Fecha ON Imputaciones(UsuarioId, Fecha); -- Sirve para consultas por usuario y fecha con la finalidad de validar límites diarios