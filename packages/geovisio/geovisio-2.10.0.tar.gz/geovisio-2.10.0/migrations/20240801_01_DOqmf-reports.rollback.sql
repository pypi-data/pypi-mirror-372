-- reports
-- depends: 20240723_01_ePGFe-upload-set-files

ALTER TABLE accounts DROP COLUMN role;
DROP TYPE account_role;

DROP TABLE reports CASCADE;
DROP FUNCTION report_update_ts_closed;
DROP FUNCTION report_auto_hide_picture;
DROP TYPE report_type;
DROP TYPE report_status;
