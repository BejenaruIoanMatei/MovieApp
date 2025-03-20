-- SQLite

CREATE TABLE movies (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    release_date TEXT,
    rating REAL
);

CREATE TABLE actors (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE movie_actors (
    movie_id INTEGER,
    actor_id INTEGER,
    PRIMARY KEY (movie_id, actor_id),
    FOREIGN KEY (movie_id) REFERENCES movies (id),
    FOREIGN KEY (actor_id) REFERENCES actors (id)
);
