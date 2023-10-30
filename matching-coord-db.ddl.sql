CREATE EXTENSION "uuid-ossp";

CREATE TYPE item_type AS ENUM ('message', 'job_post', 'applicant');

CREATE TABLE IF NOT EXISTS items_to_match (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    item_to_match TEXT NOT NULL,
    item_type item_type NOT NULL,
    processed BOOLEAN NOT NULL
);
