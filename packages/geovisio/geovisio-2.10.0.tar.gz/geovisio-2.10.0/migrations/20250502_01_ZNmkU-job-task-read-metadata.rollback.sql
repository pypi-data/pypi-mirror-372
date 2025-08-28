-- job_task_read_metadata
-- depends: 20250424_01_RBGXC-semantics-indexes

delete from job_history where job_task = 'read_metadata';

CREATE TYPE job_type_new AS ENUM (
	'prepare', -- picture needs to be prepared to be published
	'delete', -- picture needs to be deleted
	'dispatch', -- upload set needs to be dispatched into several collections
	'finalize' -- finalize a collection
);
 
alter table job_queue ALTER COLUMN task TYPE job_type_new USING task::text::job_type_new;
alter table job_history ALTER COLUMN job_task DROP DEFAULT;
alter table job_history ALTER COLUMN job_task TYPE job_type_new USING job_task::text::job_type_new;
alter table job_history ALTER COLUMN job_task SET DEFAULT 'prepare';


DROP TYPE job_type;
ALTER TYPE job_type_new RENAME TO job_type;

CREATE VIEW pictures_to_process AS (
    SELECT picture_id, ts, task, nb_errors FROM job_queue WHERE task IN ('prepare', 'delete')
);