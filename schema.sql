CREATE TABLE applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    company TEXT NOT NULL,
    role TEXT NOT NULL,
    link TEXT,
    location TEXT,
    date_applied DATE NOT NULL,
    status TEXT NOT NULL DEFAULT 'Applied',
    notes TEXT,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE sqlite_sequence(name,seq);
