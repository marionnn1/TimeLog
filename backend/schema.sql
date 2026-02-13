PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS Logs;
DROP TABLE IF EXISTS Ausencias;
DROP TABLE IF EXISTS Imputaciones;
DROP TABLE IF EXISTS CierreMes;
DROP TABLE IF EXISTS Asignaciones;
DROP TABLE IF EXISTS Proyectos;
DROP TABLE IF EXISTS Clientes;
DROP TABLE IF EXISTS Usuarios;

-- 1. USUARIOS 
CREATE TABLE Usuarios (
    Id INTEGER PRIMARY KEY AUTOINCREMENT, 
    OidAzure TEXT UNIQUE,                 
    Nombre TEXT NOT NULL, 
    Email TEXT NOT NULL UNIQUE,           
    Rol TEXT CHECK (Rol IN ('Admin', 'JP', 'Tecnico')), 
    Sede TEXT, 
    Activo INTEGER DEFAULT 1,             
    
    TipoContrato TEXT DEFAULT '40H', 
    HorasDiariasVerano REAL DEFAULT 7.00,        
    HorasInvierno_L_J REAL DEFAULT 8.50, 
    HorasInvierno_Viernes REAL DEFAULT 6.50
);

-- 2. CLIENTES
CREATE TABLE Clientes (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre TEXT NOT NULL,
    Codigo TEXT,
    Estado INTEGER DEFAULT 1
);

-- 3. PROYECTOS
CREATE TABLE Proyectos (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    ClienteId INTEGER,
    Nombre TEXT NOT NULL,
    Codigo TEXT,
    Tipo TEXT DEFAULT 'Proyecto', 
    JefeProyectoId INTEGER, 
    Estado TEXT DEFAULT 'Activo',
    FOREIGN KEY(ClienteId) REFERENCES Clientes(Id),
    FOREIGN KEY(JefeProyectoId) REFERENCES Usuarios(Id)
);

-- 4. ASIGNACIONES 
CREATE TABLE Asignaciones (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    ProyectoId INTEGER NOT NULL,
    UsuarioId INTEGER NOT NULL,
    FechaAsignacion TEXT DEFAULT CURRENT_TIMESTAMP, 
    
    FOREIGN KEY (ProyectoId) REFERENCES Proyectos(Id),
    FOREIGN KEY (UsuarioId) REFERENCES Usuarios(Id),
    CONSTRAINT UQ_Proyecto_Usuario UNIQUE (ProyectoId, UsuarioId) 
);

-- 5. CIERRE MENSUAL 
CREATE TABLE CierreMes (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Anio INTEGER NOT NULL,
    Mes INTEGER NOT NULL,
    EstaCerrado INTEGER DEFAULT 1, 
    FechaCierre TEXT DEFAULT CURRENT_TIMESTAMP,
    CerradoPorUsuarioId INTEGER,
    
    FOREIGN KEY (CerradoPorUsuarioId) REFERENCES Usuarios(Id),
    CONSTRAINT UQ_Cierre_Anio_Mes UNIQUE (Anio, Mes)
);

-- 6. IMPUTACIONES 
CREATE TABLE Imputaciones (
    Id INTEGER PRIMARY KEY AUTOINCREMENT, 
    UsuarioId INTEGER,
    ProyectoId INTEGER,
    Fecha TEXT NOT NULL,                  
    Horas REAL NOT NULL,
    Comentario TEXT,
    Estado TEXT DEFAULT 'Borrador', 
    
    ValidadoPorUsuarioId INTEGER,
    FechaValidacion TEXT,

    FOREIGN KEY (UsuarioId) REFERENCES Usuarios(Id),
    FOREIGN KEY (ProyectoId) REFERENCES Proyectos(Id),
    FOREIGN KEY (ValidadoPorUsuarioId) REFERENCES Usuarios(Id)
);

-- 7. AUSENCIAS
CREATE TABLE Ausencias (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    UsuarioId INTEGER,
    Fecha TEXT NOT NULL,
    Tipo TEXT, 
    Comentario TEXT,
    FOREIGN KEY (UsuarioId) REFERENCES Usuarios(Id)
);

-- 8. LOGS
CREATE TABLE Logs (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Fecha TEXT DEFAULT CURRENT_TIMESTAMP,
    ActorId INTEGER,
    Accion TEXT NOT NULL, 
    Detalle TEXT,
    Gravedad TEXT DEFAULT 'info',
    FOREIGN KEY (ActorId) REFERENCES Usuarios(Id)
);

-- =============================================
-- DATOS DE PRUEBA (Actualizados a la nueva estructura)
-- =============================================

INSERT INTO Usuarios (OidAzure, Nombre, Email, Rol, Sede, Activo) VALUES 
('oid-admin-001', 'Usuario Admin', 'admin@test.com', 'Admin', 'Madrid', 1),
('oid-tecnico-002', 'Usuario Tecnico', 'user@test.com', 'Tecnico', 'Barcelona', 1);

INSERT INTO Clientes (Nombre, Codigo) VALUES ('Cliente Demo', 'CL001');

INSERT INTO Proyectos (ClienteId, Nombre, Codigo, JefeProyectoId) VALUES (1, 'Proyecto TimeLog', 'PRJ001', 1);

INSERT INTO Asignaciones (ProyectoId, UsuarioId) VALUES (1, 2);


-- ==============================================================================
-- BLOQUE 2: CÓDIGO COMENTADO (Versión SQL Server / T-SQL)
-- Estructura idéntica, con sintaxis T-SQL y campo Email añadido
-- ==============================================================================

/*
-- 1. USUARIOS 
CREATE TABLE Usuarios (
    Id INT PRIMARY KEY IDENTITY(1,1),
    OidAzure NVARCHAR(100) UNIQUE,    
    Nombre NVARCHAR(100) NOT NULL, 
    Email NVARCHAR(100) NOT NULL UNIQUE, 
    Rol NVARCHAR(20) CHECK (Rol IN ('Admin', 'JP', 'Tecnico')), 
    Sede NVARCHAR(50),             
    Activo BIT DEFAULT 1,
    
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
    Tipo NVARCHAR(20) DEFAULT 'Proyecto', 
    JefeProyectoId INT FOREIGN KEY REFERENCES Usuarios(Id), 
    Estado NVARCHAR(20) DEFAULT 'Activo' 
);

-- 4. ASIGNACIONES 
CREATE TABLE Asignaciones (
    Id INT PRIMARY KEY IDENTITY(1,1),
    ProyectoId INT NOT NULL,
    UsuarioId INT NOT NULL,
    FechaAsignacion DATETIME DEFAULT GETDATE(),
    Activo BIT DEFAULT 1,
    
    CONSTRAINT FK_Asig_Proyecto FOREIGN KEY (ProyectoId) REFERENCES Proyectos(Id),
    CONSTRAINT FK_Asig_Usuario FOREIGN KEY (UsuarioId) REFERENCES Usuarios(Id),
    CONSTRAINT UQ_Proyecto_Usuario UNIQUE (ProyectoId, UsuarioId) 
);

-- 5. CIERRE MENSUAL 
CREATE TABLE CierreMes (
    Id INT PRIMARY KEY IDENTITY(1,1),
    Anio INT NOT NULL,
    Mes INT NOT NULL,
    EstaCerrado BIT DEFAULT 1, 
    FechaCierre DATETIME DEFAULT GETDATE(),
    CerradoPorUsuarioId INT FOREIGN KEY REFERENCES Usuarios(Id), 
    
    CONSTRAINT UQ_Cierre_Anio_Mes UNIQUE (Anio, Mes)
);

-- 6. IMPUTACIONES 
CREATE TABLE Imputaciones (
    Id BIGINT PRIMARY KEY IDENTITY(1,1),
    UsuarioId INT FOREIGN KEY REFERENCES Usuarios(Id),
    ProyectoId INT FOREIGN KEY REFERENCES Proyectos(Id),
    Fecha DATE NOT NULL,
    Horas DECIMAL(4, 2) NOT NULL,
    Comentario NVARCHAR(MAX),
    Estado NVARCHAR(20) DEFAULT 'Borrador', 
    
    ValidadoPorUsuarioId INT FOREIGN KEY REFERENCES Usuarios(Id),
    FechaValidacion DATETIME
);

-- 7. AUSENCIAS
CREATE TABLE Ausencias (
    Id INT PRIMARY KEY IDENTITY(1,1),
    UsuarioId INT FOREIGN KEY REFERENCES Usuarios(Id),
    Fecha DATE NOT NULL,
    Tipo NVARCHAR(20), 
    Comentario NVARCHAR(255)
);

-- 8. LOGS
CREATE TABLE Logs (
    Id BIGINT PRIMARY KEY IDENTITY(1,1),
    Fecha DATETIME DEFAULT GETDATE(),
    ActorId INT FOREIGN KEY REFERENCES Usuarios(Id),
    Accion NVARCHAR(50) NOT NULL, 
    Detalle NVARCHAR(255),
    Gravedad NVARCHAR(20) DEFAULT 'info'
);
*/