BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "horarios_medicacion" (
	"id"	INTEGER NOT NULL,
	"usuario_id"	INTEGER NOT NULL,
	"medicamento_id"	INTEGER NOT NULL,
	"tipo_horario"	TEXT NOT NULL,
	"hora"	TEXT,
	"dias_semana"	TEXT,
	"intervalo_horas"	INTEGER,
	"hora_inicio"	TEXT,
	"activo"	INTEGER DEFAULT 1,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("medicamento_id") REFERENCES "medicamentos"("id"),
	FOREIGN KEY("usuario_id") REFERENCES "usuarios"("id")
);
CREATE TABLE IF NOT EXISTS "medicamentos" (
	"id"	INTEGER NOT NULL,
	"nombre"	TEXT NOT NULL,
	"slot_id"	INTEGER NOT NULL UNIQUE,
	"cantidad_actual"	INTEGER NOT NULL DEFAULT 0,
	"cantidad_maxima"	INTEGER NOT NULL,
	"descripcion"	TEXT,
	"activo"	INTEGER DEFAULT 1,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "notas" (
	"id"	INTEGER NOT NULL,
	"usuario_id"	INTEGER NOT NULL,
	"texto"	TEXT NOT NULL,
	"fecha_hora"	TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("usuario_id") REFERENCES "usuarios"("id")
);
CREATE TABLE IF NOT EXISTS "registros_dispensacion" (
	"id"	INTEGER NOT NULL,
	"usuario_id"	INTEGER NOT NULL,
	"medicamento_id"	INTEGER NOT NULL,
	"resultado"	TEXT NOT NULL,
	"verificado"	INTEGER,
	"fecha_hora"	TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("medicamento_id") REFERENCES "medicamentos"("id"),
	FOREIGN KEY("usuario_id") REFERENCES "usuarios"("id")
);
CREATE TABLE IF NOT EXISTS "signos_vitales" (
	"id"	INTEGER NOT NULL,
	"usuario_id"	INTEGER NOT NULL,
	"tipo_metrica"	TEXT NOT NULL,
	"valor"	REAL NOT NULL,
	"fecha_hora"	TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("usuario_id") REFERENCES "usuarios"("id")
);
CREATE TABLE IF NOT EXISTS "usuarios" (
	"id"	INTEGER NOT NULL,
	"nombre"	TEXT NOT NULL,
	"edad"	INTEGER,
	"genero"	TEXT,
	"chat_id"	TEXT,
	"carpeta_embeddings"	TEXT,
	"contexto_relevante"	TEXT,
	"fecha_registro"	TEXT DEFAULT (datetime('now', 'localtime')),
	"activo"	INTEGER DEFAULT 1,
	PRIMARY KEY("id" AUTOINCREMENT)
);
COMMIT;
