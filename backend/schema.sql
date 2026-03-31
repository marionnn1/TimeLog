CREATE TABLE Usuarios (
    Id INT PRIMARY KEY IDENTITY(1,1),
    OidAzure NVARCHAR(100) UNIQUE,    
    Nombre NVARCHAR(100) NOT NULL, 
    Rol NVARCHAR(20) CHECK (Rol IN ('Admin', 'JP', 'Tecnico')), 
    Sede NVARCHAR(50),             
    Activo BIT DEFAULT 1,
    TipoContrato NVARCHAR(20) DEFAULT '40H', 
    HorasDiariasVerano DECIMAL(4,2) DEFAULT 7.00, 
    HorasInvierno_L_J DECIMAL(4,2) DEFAULT 8.50, 
    HorasInvierno_Viernes DECIMAL(4,2) DEFAULT 6.50,
    FechaCreacion DATETIME DEFAULT GETDATE(),
    FechaDesactivacion DATETIME NULL,
    DesactivadoPorUsuarioId INT NULL,
    CONSTRAINT FK_Usuarios_DesactivadoPor FOREIGN KEY (DesactivadoPorUsuarioId) REFERENCES Usuarios(Id)
);

CREATE TABLE Clientes (
    Id INT PRIMARY KEY IDENTITY(1,1),
    Nombre NVARCHAR(100) NOT NULL,
    Codigo NVARCHAR(50),
    Estado BIT DEFAULT 1,
    FechaCreacion DATETIME DEFAULT GETDATE(),
    -- Soft delete estructurado
    FechaDesactivacion DATETIME NULL,
    DesactivadoPorUsuarioId INT NULL,
    CONSTRAINT FK_Clientes_DesactivadoPor FOREIGN KEY (DesactivadoPorUsuarioId) REFERENCES Usuarios(Id)
);

CREATE TABLE Proyectos (
    Id INT PRIMARY KEY IDENTITY(1,1),
    ClienteId INT FOREIGN KEY REFERENCES Clientes(Id),
    Nombre NVARCHAR(100) NOT NULL,
    Codigo NVARCHAR(50),
    Tipo NVARCHAR(20) DEFAULT 'Proyecto', 
    JefeProyectoId INT FOREIGN KEY REFERENCES Usuarios(Id), 
    Estado NVARCHAR(20) DEFAULT 'Activo',
    FechaInicio DATE NULL,
    FechaFin DATE NULL,
    FechaCreacion DATETIME DEFAULT GETDATE(),
    FechaDesactivacion DATETIME NULL,
    DesactivadoPorUsuarioId INT NULL,
    CONSTRAINT FK_Proyectos_DesactivadoPor FOREIGN KEY (DesactivadoPorUsuarioId) REFERENCES Usuarios(Id)
);

CREATE TABLE Asignaciones (
    Id INT PRIMARY KEY IDENTITY(1,1),
    ProyectoId INT NOT NULL,
    UsuarioId INT NOT NULL,
    FechaAsignacion DATETIME DEFAULT GETDATE(),
    Activo BIT DEFAULT 1,
    -- Soft delete estructurado
    FechaDesactivacion DATETIME NULL,
    DesactivadoPorUsuarioId INT NULL,
    CONSTRAINT FK_Asig_Proyecto FOREIGN KEY (ProyectoId) REFERENCES Proyectos(Id),
    CONSTRAINT FK_Asig_Usuario FOREIGN KEY (UsuarioId) REFERENCES Usuarios(Id),
    CONSTRAINT FK_Asig_DesactivadoPor FOREIGN KEY (DesactivadoPorUsuarioId) REFERENCES Usuarios(Id),
    CONSTRAINT UQ_Proyecto_Usuario UNIQUE (ProyectoId, UsuarioId)
);

CREATE TABLE CierreMes (
    Id INT PRIMARY KEY IDENTITY(1,1),
    Anio INT NOT NULL,
    Mes INT NOT NULL,
    EstaCerrado BIT DEFAULT 1, 
    FechaCierre DATETIME DEFAULT GETDATE(),
    CerradoPorUsuarioId INT FOREIGN KEY REFERENCES Usuarios(Id), 
    CONSTRAINT UQ_Cierre_Anio_Mes UNIQUE (Anio, Mes)
);

CREATE TABLE Imputaciones (
    Id BIGINT PRIMARY KEY IDENTITY(1,1),
    UsuarioId INT FOREIGN KEY REFERENCES Usuarios(Id),
    ProyectoId INT FOREIGN KEY REFERENCES Proyectos(Id),
    Fecha DATE NOT NULL,
    Horas DECIMAL(4, 2) NOT NULL,
    Comentario NVARCHAR(MAX),
    Estado NVARCHAR(20) DEFAULT 'Borrador', 
    ValidadoPorUsuarioId INT FOREIGN KEY REFERENCES Usuarios(Id),
    FechaValidacion DATETIME,
    FechaCreacion DATETIME DEFAULT GETDATE()
);

CREATE TABLE Ausencias (
    Id INT PRIMARY KEY IDENTITY(1,1),
    UsuarioId INT FOREIGN KEY REFERENCES Usuarios(Id),
    Fecha DATE NOT NULL,
    Tipo NVARCHAR(20), 
    Comentario NVARCHAR(255)
);


-- CREATE TABLE Ausencias (
--     Id INT PRIMARY KEY IDENTITY(1,1),
--     UsuarioId INT NOT NULL,
--     Fecha DATE NOT NULL,
--     Tipo NVARCHAR(20) NOT NULL CHECK (Tipo IN ('Vacaciones', 'Asuntos Propios', 'Festivo', 'Baja', 'Otros')),
--     Comentario NVARCHAR(255),
--     FechaCreacion DATETIME DEFAULT GETDATE(),
--     CONSTRAINT FK_Ausencias_Usuario FOREIGN KEY (UsuarioId) REFERENCES Usuarios(Id),
--     CONSTRAINT UQ_Usuario_Fecha_Ausencia UNIQUE (UsuarioId, Fecha)
-- );

-- CREATE TABLE DiasAnuales (
--     Id INT PRIMARY KEY IDENTITY(1,1),
--     UsuarioId INT NOT NULL,
--     Anio INT NOT NULL,
--     DiasVacacionesNuevas INT DEFAULT 22,
--     DiasVacacionesRemanentes INT DEFAULT 0,
--     DiasAsuntosPropiosTotales INT DEFAULT 2,
--     DiasFestivosTotales INT DEFAULT 14,
--     CONSTRAINT FK_DiasAnuales_Usuario FOREIGN KEY (UsuarioId) REFERENCES Usuarios(Id),
--     CONSTRAINT UQ_Usuario_Anio_DiasAnuales UNIQUE (UsuarioId, Anio)
-- )

CREATE TABLE Logs (
    Id BIGINT PRIMARY KEY IDENTITY(1,1),
    Fecha DATETIME DEFAULT GETDATE(),
    ActorId INT FOREIGN KEY REFERENCES Usuarios(Id),
    Accion NVARCHAR(50) NOT NULL, 
    Detalle NVARCHAR(255),
    Gravedad NVARCHAR(20) DEFAULT 'info'
);

CREATE TABLE Auditoria (
    Id INT PRIMARY KEY IDENTITY(1,1),
    Fecha DATETIME DEFAULT GETDATE(),
    ActorId INT NULL, 
    ActorNombre NVARCHAR(100) NOT NULL,
    Accion NVARCHAR(50) NOT NULL,
    Gravedad NVARCHAR(20) DEFAULT 'info',
    Detalle NVARCHAR(MAX) NOT NULL
);