CREATE TABLE IF NOT EXISTS Session (
    Id CHAR(64) PRIMARY KEY NOT NULL,
    DateTime VARCHAR(32) NOT NULL,
    Name TEXT NOT NULL,
    Cfg TEXT NULL
);

CREATE TABLE IF NOT EXISTS Analyzer (
    Id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    SessionId CHAR(64) NOT NULL,
    Content TEXT NOT NULL,
    Cfg TEXT NULL,
    FOREIGN KEY(SessionId) REFERENCES Session(id)
);

CREATE TABLE IF NOT EXISTS Input (
    Id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    SessionId CHAR(64) NOT NULL,
    Content TEXT NOT NULL,
    Cfg TEXT NULL,
    FOREIGN KEY(SessionId) REFERENCES Session(id)
);

CREATE TABLE IF NOT EXISTS Output (
    Id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    SessionId CHAR(64) NOT NULL,
    Content TEXT,
    Cfg TEXT NULL,
    FOREIGN KEY(SessionId) REFERENCES Session(id)
);

CREATE TABLE IF NOT EXISTS Translation (
    Id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    SessionId CHAR(64) NOT NULL,
    Content TEXT,
    Cfg TEXT NULL,
    FOREIGN KEY(SessionId) REFERENCES Session(id)
);