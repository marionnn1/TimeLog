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


-- . Clientes 
CREATE TABLE Clientes (
    Id INT PRIMARY KEY IDENTITY(1,1),
    Nombre NVARCHAR(100) NOT NULL,
    Codigo NVARCHAR(50),
    Estado BIT DEFAULT 1
);

-- Proyectos 
CREATE TABLE Proyectos (
    Id INT PRIMARY KEY IDENTITY(1,1),
    ClienteId INT FOREIGN KEY REFERENCES Clientes(Id),
    Nombre NVARCHAR(100) NOT NULL,
    Codigo NVARCHAR(50),
    Tipo NVARCHAR(20) DEFAULT 'Proyecto', -- Servicio o Proyecto
    JefeProyectoId INT FOREIGN KEY REFERENCES Usuarios(Id), -- El JP asignado
    Estado BIT DEFAULT 1
);

-- Imputaciones / TimeLog (Basado en PDF [cite: 58])
CREATE TABLE Imputaciones (
    Id BIGINT PRIMARY KEY IDENTITY(1,1),
    UsuarioId INT FOREIGN KEY REFERENCES Usuarios(Id),
    ProyectoId INT FOREIGN KEY REFERENCES Proyectos(Id),
    Fecha DATE NOT NULL,
    Horas DECIMAL(4, 2) NOT NULL,
    Notas NVARCHAR(MAX),
    JustificacionExceso NVARCHAR(255) NULL,  ---Campo para justificar si se supera el límite diario calculado
    EsFestivo BIT DEFAULT 0,      -- Requisito PDF 
    EsNoFacturable BIT DEFAULT 0, -- Requisito PDF 
    Estado NVARCHAR(20) DEFAULT 'Borrador'
);

--  Índices para rendimiento (Recomendado para Reporting [cite: 36])
CREATE INDEX IX_Imputaciones_Usuario_Fecha ON Imputaciones(UsuarioId, Fecha);