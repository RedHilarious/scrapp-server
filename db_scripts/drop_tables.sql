DROP TRIGGER update_timestamp on app_user;
DROP TRIGGER update_timestamp on rule;
DROP TRIGGER update_timestamp on subscription;
DROP TRIGGER update_timestamp on result;
DROP TRIGGER update_timestamp on current_result;
DROP TRIGGER update_timestamp on action;
DROP TRIGGER update_timestamp on action_param;
DROP TRIGGER update_existing_position on action;
DROP FUNCTION update_timestamp();
DROP FUNCTION update_existing_position();

DROP TABLE current_result CASCADE;
DROP TABLE result CASCADE;
DROP TABLE subscription CASCADE;
DROP TABLE action_param CASCADE;
DROP TABLE action CASCADE;
DROP TABLE rule CASCADE;
DROP TABLE app_user CASCADE;

