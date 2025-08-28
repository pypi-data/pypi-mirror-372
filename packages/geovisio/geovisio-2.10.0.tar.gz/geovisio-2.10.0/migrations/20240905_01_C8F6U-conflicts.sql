-- conflicts
-- depends: 20240820_01_aB2ZK-exclusion-zones  20240904_01_gFjlV-files-rejection-msg

-- Add a file_duplicate error to the file_rejection_status enum

ALTER TYPE file_rejection_status ADD VALUE 'file_duplicate';
