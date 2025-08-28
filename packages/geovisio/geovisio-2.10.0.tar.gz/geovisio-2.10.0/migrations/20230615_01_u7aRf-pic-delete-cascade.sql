-- pic_delete_cascade
-- depends: 20230511_01_TdpKo-tokens

-- Add on delete cascade to pic deletion

ALTER TABLE sequences_pictures 
	DROP CONSTRAINT sequences_pictures_pic_id_fkey , 
	ADD CONSTRAINT sequences_pictures_pic_id_fkey FOREIGN KEY (pic_id) REFERENCES pictures(id) ON DELETE CASCADE;

ALTER TABLE pictures_to_process 
	DROP CONSTRAINT picture_id_fk , 
	ADD CONSTRAINT picture_id_fk FOREIGN KEY (picture_id) REFERENCES pictures(id) ON DELETE CASCADE;
