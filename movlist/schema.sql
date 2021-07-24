-- Initialize the database.

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS movie;
DROP TABLE IF EXISTS genre;
DROP TABLE IF EXISTS bridge_movie_genre;
DROP TABLE IF EXISTS bridge_movie_user_rating;
DROP TABLE IF EXISTS movie_list;

CREATE TABLE user (
  id       INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT        NOT NULL
);

CREATE TABLE movie (
  id    INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL
);

CREATE TABLE genre (
  id   INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL
);

CREATE TABLE bridge_movie_genre (
  movie_id INTEGER NOT NULL REFERENCES movie(id),
  genre_id INTEGER NOT NULL REFERENCES genre(id)
);

CREATE TABLE bridge_movie_user_rating (
  movie_id INTEGER NOT NULL REFERENCES movie(id),
  user_id  INTEGER NOT NULL REFERENCES user(id),
  rating   INTEGER
);

CREATE TABLE movie_list (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  movie_id   INTEGER   NOT NULL,
  user_id    INTEGER   NOT NULL,
  avg_rating FLOAT              DEFAULT 0,
  date_added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (movie_id) REFERENCES movie(id),
  FOREIGN KEY (user_id)  REFERENCES user(id)
);
