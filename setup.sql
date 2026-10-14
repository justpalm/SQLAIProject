CREATE TABLE adress (
    address_id INTEGER PRIMARY KEY,
    street     VARCHAR(255) NOT NULL,
    state      VARCHAR(50) NOT NULL,
    city       VARCHAR(100) NOT NULL,
    zip_code   BIGINT NOT NULL
);

CREATE TABLE pantry (
    pantry_id  INTEGER PRIMARY KEY,
    address_id BIGINT NOT NULL,

    FOREIGN KEY (address_id)
        REFERENCES adress (address_id)
);

CREATE TABLE shelfs (
    shelf_id     INTEGER PRIMARY KEY,
    pantry_id    BIGINT NOT NULL,
    food_name    VARCHAR(255) NOT NULL,
    quantity     BIGINT NOT NULL CHECK (quantity >= 0),
    best_by_date DATE NULL,

    FOREIGN KEY (pantry_id)
        REFERENCES pantry (pantry_id)
);

CREATE TABLE cupboards (
    cupboard_id  INTEGER PRIMARY KEY,
    pantry_id    BIGINT NOT NULL,
    food_name    VARCHAR(255) NOT NULL,
    quantity     BIGINT NOT NULL CHECK (quantity >= 0),
    best_by_date DATE NULL,

    FOREIGN KEY (pantry_id)
        REFERENCES pantry (pantry_id)
);