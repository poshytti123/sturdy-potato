CREATE TABLE IF NOT EXISTS migration(
    id INTEGER PRIMARY KEY AUTOINCREMENT
);
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS airports (
    code TEXT NOT NULL PRIMARY KEY ,
    name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS flights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_airport TEXT,
    to_airport TEXT,
    departure DATETIME,
    arrival DATETIME,
    available_tickets INTEGER,
    CONSTRAINT from_airport_fk FOREIGN KEY (from_airport)  REFERENCES airports (code),
    CONSTRAINT to_airport_fk FOREIGN KEY (to_airport)  REFERENCES airports (code)
);
CREATE TABLE IF NOT EXISTS booking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    flight_id INTEGER,
    booking_status INTEGER,
    CONSTRAINT flight_fk FOREIGN KEY (flight_id)  REFERENCES flights (id),
    CONSTRAINT user_fk FOREIGN KEY (user_id)  REFERENCES users (id)
);

INSERT INTO airports (code, name) VALUES ("SVX", "Yekaterinburg");
INSERT INTO airports (code,name) VALUES ("IST", "Istanbul");


INSERT INTO flights (from_airport, to_airport, departure, arrival, available_tickets)
VALUES ( "SVX", "IST", "2024-06-14 20:34", "2024-06-14 22:34", 10);
INSERT INTO flights (from_airport, to_airport, departure, arrival, available_tickets)
VALUES ( "SVX", "IST", "2024-06-14 21:34", "2024-06-14 22:34", 10);
INSERT INTO flights (from_airport, to_airport, departure, arrival, available_tickets)
VALUES ( "SVX", "IST", "2024-06-15 06:34", "2024-06-15 22:34", 10);
INSERT INTO flights (from_airport, to_airport, departure, arrival, available_tickets)
VALUES ( "SVX", "IST", "2024-06-16 20:34", "2024-06-16 22:34", 10);
INSERT INTO migration (id) VALUES (1);