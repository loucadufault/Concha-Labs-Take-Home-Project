DROP TABLE IF EXISTS user_info;
DROP TABLE IF EXISTS audio;

CREATE TABLE user_info (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  address TEXT NOT NULL,
  image_hosted_link TEXT
);
