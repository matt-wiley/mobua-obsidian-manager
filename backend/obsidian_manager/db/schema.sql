CREATE TABLE IF NOT EXISTS records (
    id           TEXT PRIMARY KEY,
    folder_path  TEXT NOT NULL,
    file_path    TEXT NOT NULL,
    filename     TEXT NOT NULL,
    frontmatter  TEXT,
    sections     TEXT,
    content_hash TEXT,
    updated_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS links (
    source_id   TEXT NOT NULL,
    target_file TEXT NOT NULL,
    field_name  TEXT NOT NULL,
    FOREIGN KEY (source_id) REFERENCES records(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS col_widths (
    folder_path TEXT NOT NULL,
    field_name  TEXT NOT NULL,
    width       INTEGER NOT NULL,
    PRIMARY KEY (folder_path, field_name)
);

CREATE TABLE IF NOT EXISTS views (
    id          TEXT PRIMARY KEY,
    folder_path TEXT NOT NULL,
    name        TEXT NOT NULL,
    filters     TEXT NOT NULL DEFAULT '[]',
    sort        TEXT NOT NULL DEFAULT '[]',
    col_order   TEXT NOT NULL DEFAULT '[]',
    hidden_cols TEXT NOT NULL DEFAULT '[]',
    created_at  TEXT NOT NULL
);
