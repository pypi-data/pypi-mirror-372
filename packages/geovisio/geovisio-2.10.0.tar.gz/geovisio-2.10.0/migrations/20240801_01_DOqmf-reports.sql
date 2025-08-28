-- reports
-- depends: 20240723_01_ePGFe-upload-set-files

CREATE TYPE report_type AS ENUM (
	'blur_missing',			-- Blur misses some people/vehicles
	'blur_excess',			-- Blur on non-necessary features (traffic sign)
	'inappropriate',		-- Shows non street imagery related features
	'privacy',				-- Shows private areas without owner's consent
	'picture_low_quality',	-- Totally blurred/dark/... making it useless
	'mislocated',			-- Coordinates are wrong or of very low precision
	'copyright',			-- Infringes copyright laws (copied without author's consent)
	'other'					-- Any other issue
);

CREATE TYPE report_status AS ENUM (
	'open',				-- Nothing done yet
	'open_autofix',		-- Opened with automatic measures applied (picture hidden)
	'waiting',			-- On-going discussions or resolution
	'closed_solved',	-- Closed and issue solved
	'closed_ignored'	-- Closed and issue considered not receivable
);

CREATE TABLE reports(
	id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	issue report_type NOT NULL,
	status report_status NOT NULL DEFAULT 'open',

	-- report can be linked to a picture or a sequence
	picture_id UUID REFERENCES pictures(id) ON DELETE CASCADE,
	sequence_id UUID REFERENCES sequences(id) ON DELETE CASCADE,

	-- timestamps
	ts_opened TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
	ts_closed TIMESTAMPTZ,

	-- try to keep a mean of contact, either account or email (optional)
	reporter_account_id UUID REFERENCES accounts(id) ON DELETE SET NULL,
	reporter_email TEXT,

	-- keep track of who closed/solved
	resolver_account_id UUID REFERENCES accounts(id) ON DELETE SET NULL,

	-- comments
	reporter_comments TEXT,
	resolver_comments TEXT
);

-- Auto-update ts_closed on status change
CREATE OR REPLACE FUNCTION report_update_ts_closed()
RETURNS TRIGGER AS $$
BEGIN
	IF NEW.status IN ('closed_solved', 'closed_ignored') THEN
		NEW.ts_closed := CURRENT_TIMESTAMP;
	ELSE
		NEW.ts_closed := NULL;
		NEW.resolver_account_id := NULL;
	END IF;
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_report_update_ts_closed
BEFORE UPDATE ON reports
FOR EACH ROW
EXECUTE FUNCTION report_update_ts_closed();

-- Auto-hide picture
CREATE OR REPLACE FUNCTION report_auto_hide_picture()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'open' AND NEW.issue IN ('blur_missing', 'inappropriate', 'privacy', 'copyright') THEN
		IF NEW.picture_id is NOT NULL THEN
			UPDATE pictures
			SET status = 'hidden'
			WHERE id = NEW.picture_id;
			NEW.status = 'open_autofix';
		ELSIF NEW.sequence_id IS NOT NULL THEN
			UPDATE sequences
			SET status = 'hidden'
			WHERE id = NEW.sequence_id;
			NEW.status = 'open_autofix';
		END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_report_auto_hide_picture
BEFORE INSERT ON reports
FOR EACH ROW
EXECUTE FUNCTION report_auto_hide_picture();

-- Role for accounts
CREATE TYPE account_role AS ENUM (
	'user',		-- Classic account
	'admin'		-- Almighty account
);

ALTER TABLE accounts ADD COLUMN role account_role NOT NULL DEFAULT 'user';
UPDATE accounts SET role = 'admin' WHERE is_default;
