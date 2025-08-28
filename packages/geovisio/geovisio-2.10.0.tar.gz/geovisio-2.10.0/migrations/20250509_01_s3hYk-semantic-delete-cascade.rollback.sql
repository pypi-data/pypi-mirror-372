-- semantic_delete_cascade
-- depends: 20250424_01_RBGXC-semantics-indexes


ALTER TABLE pictures_semantics_history 
	DROP CONSTRAINT pictures_semantics_history_picture_id_fkey , 
	ADD CONSTRAINT pictures_semantics_history_picture_id_fkey FOREIGN KEY (picture_id) REFERENCES pictures(id);

ALTER TABLE sequences_semantics_history 
	DROP CONSTRAINT sequences_semantics_history_sequence_id_fkey , 
	ADD CONSTRAINT sequences_semantics_history_sequence_id_fkey FOREIGN KEY (sequence_id) REFERENCES sequences(id);
