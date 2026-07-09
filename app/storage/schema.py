"""Esquema de la base de datos SQLite.

Modelo relacional con trazabilidad completa de IA (RF-10/RNF-05). La tabla
`ia_trazas` guarda, por cada llamada a la IA: prompt exacto, respuesta cruda,
criterios, modelo, versión del prompt y fecha/hora. Así toda pregunta,
evaluación y resumen queda auditable.
"""

from __future__ import annotations

# DDL idempotente (CREATE IF NOT EXISTS). Las claves foráneas se activan por
# conexión (PRAGMA foreign_keys=ON en db.py). ON DELETE CASCADE mantiene la
# integridad si se borra una entrevista.
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS entrevistas (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    rol                TEXT    NOT NULL,
    tecnologia         TEXT    NOT NULL,
    nivel              TEXT    NOT NULL,
    idioma             TEXT    NOT NULL,
    cantidad_preguntas INTEGER NOT NULL,
    tipo               TEXT    NOT NULL,
    estado             TEXT    NOT NULL DEFAULT 'en_curso',  -- en_curso|completada
    creada_en          TEXT    NOT NULL,
    completada_en      TEXT
);

CREATE TABLE IF NOT EXISTS preguntas (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    entrevista_id INTEGER NOT NULL,
    orden         INTEGER NOT NULL,
    pregunta      TEXT    NOT NULL,
    dificultad    TEXT    NOT NULL,
    tema          TEXT    NOT NULL,
    criterios     TEXT    NOT NULL DEFAULT '[]',   -- JSON de lista de textos
    creada_en     TEXT    NOT NULL,
    FOREIGN KEY (entrevista_id) REFERENCES entrevistas(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS respuestas (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    pregunta_id INTEGER NOT NULL,
    texto       TEXT    NOT NULL,
    creada_en   TEXT    NOT NULL,
    FOREIGN KEY (pregunta_id) REFERENCES preguntas(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS evaluaciones (
    id                          INTEGER PRIMARY KEY AUTOINCREMENT,
    pregunta_id                 INTEGER NOT NULL,
    puntaje                     INTEGER NOT NULL,
    fortalezas                  TEXT    NOT NULL DEFAULT '[]',  -- JSON
    errores                     TEXT    NOT NULL DEFAULT '[]',  -- JSON
    omisiones                   TEXT    NOT NULL DEFAULT '[]',  -- JSON
    respuesta_mejorada          TEXT    NOT NULL,
    coherente_con_configuracion INTEGER NOT NULL,               -- 0|1
    creada_en                   TEXT    NOT NULL,
    FOREIGN KEY (pregunta_id) REFERENCES preguntas(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS resumenes (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    entrevista_id      INTEGER NOT NULL,
    nivel_estimado     TEXT    NOT NULL,
    puntaje_general    INTEGER NOT NULL,
    promedio_calculado REAL    NOT NULL,
    areas_fuertes      TEXT    NOT NULL DEFAULT '[]',  -- JSON
    areas_mejora       TEXT    NOT NULL DEFAULT '[]',  -- JSON
    plan_de_estudio    TEXT    NOT NULL DEFAULT '[]',  -- JSON
    creado_en          TEXT    NOT NULL,
    FOREIGN KEY (entrevista_id) REFERENCES entrevistas(id) ON DELETE CASCADE
);

-- Trazabilidad de IA (RF-10/RNF-05): auditoría de cada llamada.
CREATE TABLE IF NOT EXISTS ia_trazas (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    entrevista_id  INTEGER,
    pregunta_id    INTEGER,
    tipo_llamada   TEXT    NOT NULL,   -- pregunta|evaluacion|resumen
    system_prompt  TEXT    NOT NULL,
    user_prompt    TEXT    NOT NULL,
    respuesta_cruda TEXT   NOT NULL,
    modelo         TEXT    NOT NULL,
    criterios      TEXT    NOT NULL DEFAULT '[]',  -- JSON
    prompt_version TEXT,
    creada_en      TEXT    NOT NULL,
    FOREIGN KEY (entrevista_id) REFERENCES entrevistas(id) ON DELETE CASCADE,
    FOREIGN KEY (pregunta_id)   REFERENCES preguntas(id)  ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_preguntas_entrevista   ON preguntas(entrevista_id);
CREATE INDEX IF NOT EXISTS idx_evaluaciones_pregunta  ON evaluaciones(pregunta_id);
CREATE INDEX IF NOT EXISTS idx_trazas_entrevista      ON ia_trazas(entrevista_id);
"""
