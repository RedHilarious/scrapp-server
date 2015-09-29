SET TIMEZONE = 'UTC';

-- create Tables
CREATE TABLE app_user (
  user_id SERIAL PRIMARY KEY,
  identity_token TEXT UNIQUE NOT NULL,
  gcm_token TEXT UNIQUE NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT (now() AT TIME ZONE ('utc')),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT (now() AT TIME ZONE ('utc'))
);

CREATE TABLE rule (
  rule_id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT (now() AT TIME ZONE ('utc')),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT (now() AT TIME ZONE ('utc'))
);

CREATE TABLE subscription (
  subscription_id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES app_user(user_id),
  rule_id INTEGER NOT NULL REFERENCES rule(rule_id),
  start_time TIMESTAMPTZ,
  interval INTEGER,
  created_at TIMESTAMPTZ NOT NULL DEFAULT (now() AT TIME ZONE ('utc')),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT (now() AT TIME ZONE ('utc')),
  deleted_at TIMESTAMPTZ DEFAULT NULL,
  UNIQUE (user_id, rule_id)
);

CREATE TABLE result (
  result_id SERIAL PRIMARY KEY,
  subscription_id INTEGER NOT NULL REFERENCES subscription(subscription_id),
  hash TEXT NOT NULL,
  last_modified TIMESTAMP NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT (now() AT TIME ZONE ('utc')),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT (now() AT TIME ZONE ('utc'))
);

CREATE TABLE current_result (
  rule_id INTEGER PRIMARY KEY REFERENCES rule(rule_id),
  hash TEXT NOT NULL,
  last_modified TIMESTAMP NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT (now() AT TIME ZONE ('utc')),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT (now() AT TIME ZONE ('utc'))
);

CREATE TABLE action (
  action_id SERIAL PRIMARY KEY,
  title TEXT,
  rule_id INTEGER NOT NULL REFERENCES rule(rule_id),
  position INTEGER NOT NULL,
  method TEXT NOT NULL,
  url TEXT,
  parse_expression TEXT,
  parse_type TEXT,
  parse_expression_display TEXT,
  parse_type_display TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT (now() AT TIME ZONE ('utc')),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT (now() AT TIME ZONE ('utc'))
);

CREATE TABLE action_param (
  action_param_id SERIAL PRIMARY KEY,
  action_id INTEGER NOT NULL REFERENCES action(action_id),
  title TEXT,
  key TEXT NOT NULL,
  value TEXT,
  type TEXT NOT NULL,
  required BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT (now() AT TIME ZONE ('utc')),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT (now() AT TIME ZONE ('utc'))
);

-- function to increment existing position of an action
CREATE OR REPLACE FUNCTION update_existing_position()
  RETURNS TRIGGER AS $$
    -- given a column "position", if an item is given a position,
    -- already occupied by another row, bump that other row forward
    BEGIN
      UPDATE action
        SET position = position + 1
        WHERE position = new.position AND rule_id = new.rule_id;
        RETURN NEW;
    END;
$$ LANGUAGE plpgsql;

-- function to set current timestamp for updated_at column
CREATE OR REPLACE FUNCTION update_timestamp()
  RETURNS TRIGGER AS $$
  BEGIN
    NEW.updated_at = now() AT TIME ZONE ('utc');
    RETURN NEW;
  END;
$$ LANGUAGE plpgsql;

-- trigger update_existing_position() for action
CREATE TRIGGER update_existing_position BEFORE INSERT OR UPDATE ON action
  FOR EACH ROW EXECUTE PROCEDURE update_existing_position();

-- trigger update_timestamp() for app_user
CREATE TRIGGER update_timestamp BEFORE UPDATE ON app_user
  FOR EACH ROW EXECUTE PROCEDURE update_timestamp();

-- trigger update_timestamp() for rule
CREATE TRIGGER update_timestamp BEFORE UPDATE ON rule
  FOR EACH ROW EXECUTE PROCEDURE update_timestamp();

-- trigger update_timestamp() for subscription
CREATE TRIGGER update_timestamp BEFORE UPDATE ON subscription
  FOR EACH ROW EXECUTE PROCEDURE update_timestamp();

-- trigger update_timestamp() for result
CREATE TRIGGER update_timestamp BEFORE UPDATE ON result
  FOR EACH ROW EXECUTE PROCEDURE update_timestamp();

-- trigger update_timestamp() for current_result
CREATE TRIGGER update_timestamp BEFORE UPDATE ON current_result
  FOR EACH ROW EXECUTE PROCEDURE update_timestamp();

-- trigger update_timestamp() for action
CREATE TRIGGER update_timestamp BEFORE UPDATE ON action
  FOR EACH ROW EXECUTE PROCEDURE update_timestamp();

-- trigger update_timestamp() for action_param
CREATE TRIGGER update_timestamp BEFORE UPDATE ON action_param
  FOR EACH ROW EXECUTE PROCEDURE update_timestamp();