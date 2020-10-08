--
-- sql/schema.base.sql
--

-- Users Table -----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
  id                    SERIAL        PRIMARY KEY,
  created_at            TIMESTAMP     WITH TIME ZONE DEFAULT CLOCK_TIMESTAMP(),
  last_modified         TIMESTAMP     WITH TIME ZONE DEFAULT CLOCK_TIMESTAMP(),
  deleted_at            TIMESTAMP     WITH TIME ZONE DEFAULT to_timestamp(0),
  email                 VARCHAR(128)  NOT NULL,
  password_hash         VARCHAR(256)  NOT NULL DEFAULT '',
  consecutive_failures  INTEGER       NOT NULL DEFAULT 0,
  lockout_ends          TIMESTAMP     WITH TIME ZONE DEFAULT to_timestamp(0),
  first_name            VARCHAR(128)  NOT NULL,
  last_name             VARCHAR(128)  NOT NULL,
  consecutive_resets    INTEGER       NOT NULL DEFAULT 0,
  reset_lockout_ends    TIMESTAMP     WITH TIME ZONE DEFAULT CLOCK_TIMESTAMP()
);

CREATE UNIQUE INDEX user_emails_index ON users(email);
CREATE INDEX users_deleted_at_index   ON users(deleted_at);

-- The Stank -------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_last_modified_func() RETURNS TRIGGER AS $$
BEGIN
  NEW.last_modified = CLOCK_TIMESTAMP();
  RETURN NEW;
END;
$$
language 'plpgsql';

CREATE TRIGGER row_update_on_users
  BEFORE UPDATE ON users
    FOR EACH ROW
      EXECUTE PROCEDURE update_last_modified_func();

-- On Delete Rules -------------------------------------------------------------
CREATE RULE update_deleted_at_on_delete AS ON DELETE TO users DO
  INSTEAD UPDATE users
    SET deleted_at = CLOCK_TIMESTAMP()
      WHERE id = old.id;


-- Convert to milliseconds since epoch -----------------------------------------
CREATE OR REPLACE FUNCTION to_ms_since_epoch(timestamp with time zone) RETURNS BIGINT
  AS 'select CAST(EXTRACT(EPOCH FROM $1 AT TIME ZONE ''UTC'') * 1000 as BIGINT);'
  LANGUAGE SQL
  IMMUTABLE;

CREATE OR REPLACE FUNCTION cast_to_date(text, date) returns date as $$
begin
    return cast($1 as date);
exception
    when OTHERS then
        return $2;
end;
$$ language plpgsql immutable;
