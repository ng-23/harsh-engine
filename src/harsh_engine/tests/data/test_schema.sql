DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    join_time INTEGER NOT NULL,
    last_seen_time INTEGER NOT NULL
);
