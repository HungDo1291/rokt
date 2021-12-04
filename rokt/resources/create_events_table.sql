CREATE TABLE events(
filename VARCHAR(100),
datetime DATETIME,
email VARCHAR(100),
session_id VARCHAR(100));

CREATE UNIQUE INDEX search_index on events (filename, datetime);