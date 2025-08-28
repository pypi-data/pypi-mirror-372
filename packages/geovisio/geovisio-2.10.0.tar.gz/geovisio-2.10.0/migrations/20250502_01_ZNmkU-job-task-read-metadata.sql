-- job_task_read_metadata
-- depends: 20250424_01_RBGXC-semantics-indexes

 
ALTER TYPE job_type ADD VALUE 'read_metadata';

DROP VIEW pictures_to_process;  -- drop the old pictures to process view 