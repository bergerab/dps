CREATE TABLE datasets(
    dataset_id INT GENERATED ALWAYS AS IDENTITY,
    name       CHAR(200) NOT NULL,
    PRIMARY KEY(dataset_id)
);

CREATE TABLE signals(
    signal_id  INT GENERATED ALWAYS AS IDENTITY,
    dataset_id INT NOT NULL,
    name       CHAR(200) NOT NULL,
    PRIMARY KEY(signal_id),
    FOREIGN KEY (dataset_id) REFERENCES datasets(dataset_id)
);

CREATE TABLE signal_data(
    signal_id  INT NOT NULL,
    value      DOUBLE PRECISION NOT NULL,
    time       TIMESTAMPTZ NOT NULL,
    FOREIGN KEY (signal_id) REFERENCES signals(signal_id)
);

SELECT create_hypertable('signal_data', 'time');
