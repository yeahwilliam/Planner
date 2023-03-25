DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS planner;
DROP TABLE IF EXISTS planner_item;

CREATE TABLE user (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    forename TEXT NOT NULL,
    surname TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_date TIMESTAMP NOT NULL
);

CREATE TABLE planner (
    planner_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    planner_name TEXT NOT NULL,
    created_date TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

CREATE TABLE planner_item (
    planner_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    planner_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    due_date TIMESTAMP NOT NULL,
    is_done BOOLEAN NOT NULL,
    notes TEXT,
    FOREIGN KEY (planner_id) REFERENCES planner(planner_id)
);