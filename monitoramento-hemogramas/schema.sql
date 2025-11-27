PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS hemograma (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  paciente_id TEXT,
  municipio TEXT NOT NULL,
  data_coleta DATE NOT NULL,
  plaquetas INTEGER NOT NULL,
  faixa_etaria TEXT,
  sexo TEXT
);

CREATE TABLE IF NOT EXISTS alerts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  municipio TEXT NOT NULL,
  data_alerta DATE NOT NULL,
  tipo TEXT, -- 'limiar' | 'queda_relativa'
  valor REAL,
  descricao TEXT
);
