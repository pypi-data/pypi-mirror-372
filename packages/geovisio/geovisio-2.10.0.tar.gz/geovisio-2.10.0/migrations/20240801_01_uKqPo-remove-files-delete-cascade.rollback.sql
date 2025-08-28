-- remove_files_delete_cascade
-- depends: 20240730_02_aRymN-rejection-status

-- when we delete a picture (like if it's a soft duplicate), we want to keep track that the file was sent
ALTER TABLE files
	DROP CONSTRAINT files_picture_id_fkey ,
	ADD CONSTRAINT files_picture_id_fkey FOREIGN KEY (picture_id) REFERENCES pictures(id);


ALTER TABLE files
	ALTER COLUMN size SET NOT NULL,
	ALTER COLUMN file_type SET NOT NULL,
	ALTER COLUMN content_md5 SET NOT NULL;
