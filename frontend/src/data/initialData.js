export const initialData = {
    currentUser: {
        id: 99,
        nombre: 'Mario León',
        email: 'mario.leon@inetum.com',
        rol: 'Administrador',
        iniciales: 'ML',
        sede: 'Madrid'
    },
    usuarios: [
        { id: 1, nombre: 'Laura Martínez', email: 'laura.m@inetum.com', rol: 'Técnico', sede: 'Madrid', departamento: 'Desarrollo' },
        { id: 2, nombre: 'Pedro López', email: 'pedro.l@inetum.com', rol: 'Jefe de Proyecto', sede: 'Barcelona', departamento: 'Gestión' },
        { id: 3, nombre: 'Carlos Ruiz', email: 'carlos.r@inetum.com', rol: 'Técnico', sede: 'Remoto', departamento: 'Sistemas' },
        { id: 4, nombre: 'Ana García', email: 'ana.garcia@inetum.com', rol: 'Administrador', sede: 'Madrid', departamento: 'IT Interno' },
        { id: 5, nombre: 'Daniel Civxiz', email: 'dani.c@inetum.com', rol: 'Técnico', sede: 'Sevilla', departamento: 'QA' }
    ],
    proyectos: [
        { id: 1, nombre: 'Auditoría Backend', cliente: 'Banco Santander', estado: 'Activo' },
        { id: 2, nombre: 'Migración Cloud', cliente: 'Mapfre', estado: 'Activo' },
        { id: 3, nombre: 'App Móvil v2', cliente: 'Inditex', estado: 'Cerrado' },
        { id: 4, nombre: 'Portal Empleado', cliente: 'Naturgy', estado: 'Activo' }
    ],
    logs: [
        { id: 1, fecha: '2026-02-03 09:15', actor: 'Ana García (Admin)', accion: 'CREATE_USER', detalle: 'Creó al usuario Mario León', gravedad: 'info' },
        { id: 2, fecha: '2026-02-03 08:30', actor: 'Sistema', accion: 'BACKUP_AUTO', detalle: 'Copia de seguridad diaria completada', gravedad: 'system' },
        { id: 3, fecha: '2026-02-02 11:30', actor: 'Pedro López (JP)', accion: 'REJECT_HOURS', detalle: 'Rechazó 40h de Daniel Civxiz', gravedad: 'warning' }
    ],
    tickets: [
        { id: 1, usuario: 'Daniel Civxiz', tipo: 'Acceso', asunto: 'No me aparece el proyecto Mapfre', descripcion: 'He entrado esta mañana y no veo el proyecto para imputar.', estado: 'pendiente', fecha: '2026-02-03 09:00' },
        { id: 2, usuario: 'Carlos Ruiz', tipo: 'Bug', asunto: 'Error 500 al guardar', descripcion: 'Al intentar guardar el viernes pasado me dio un pantallazo rojo.', estado: 'resuelto', fecha: '2026-02-01 10:30' },
        { id: 3, usuario: 'Laura Martínez', tipo: 'Duda', asunto: '¿Cómo pido vacaciones?', descripcion: 'No encuentro el botón para solicitar los días de Semana Santa.', estado: 'pendiente', fecha: '2026-02-03 11:15' }
    ],
    anuncio: {
        activo: true,
        mensaje: '⚠️ Mantenimiento programado: El viernes a las 18:00 la app estará inactiva 1 hora por actualización de servidores.',
        tipo: 'warning'
    },
    sedes: ['Madrid', 'Barcelona', 'Tarragona', 'Sevilla', 'Bilbao', 'Remoto']
}