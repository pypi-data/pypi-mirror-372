-- sequence_current_sort
-- depends: 20240115_01_FatLR-token-delete-cascade

CREATE TYPE sequence_sort AS ENUM (
	'+filedate',         -- Sort by ascending camera date
	'+filename',         -- Sort by ascending filename
	'+gpsdate',           -- Sort by ascending gps date
	'-filedate',         -- Sort by descending camera date
	'-filename',         -- Sort by descending filename
	'-gpsdate'           -- Sort by descending gps date
);

-- Add a column to persist the user defined sort
-- nullable since by default no sort is chosen
ALTER TABLE sequences ADD COLUMN current_sort sequence_sort;