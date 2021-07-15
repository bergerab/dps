CREATE TABLE datasets(
    dataset_id INT GENERATED ALWAYS AS IDENTITY,
    name       VARCHAR(200),
    PRIMARY KEY (dataset_id)
);

CREATE TABLE signals(
    signal_id  INT GENERATED ALWAYS AS IDENTITY,
    dataset_id INT NOT NULL,
    name       VARCHAR(200) NOT NULL,
    PRIMARY KEY (signal_id),
    FOREIGN KEY (dataset_id) REFERENCES datasets(dataset_id)
);

CREATE TABLE signal_data(
    signal_id  INT NOT NULL,
    value      DOUBLE PRECISION NOT NULL,
    time       TIMESTAMPTZ NOT NULL,
    FOREIGN KEY (signal_id) REFERENCES signals(signal_id)
);

SELECT create_hypertable('signal_data', 'time');
CREATE INDEX idx_signal_id ON signal_data(signal_id);

CREATE INDEX ON signal_data (signal_id, time DESC);
CREATE INDEX ON signal_data (signal_id, time ASC);

-- Skipping the foreign key constraint on `signal_data`,
-- improved insert speed by ~40% (for 100,000 records).
-- The best solution is to keep the foreign key constraint, and before
-- a bulk insert, drop the constraint, and add it back after the bulk insert is done.
