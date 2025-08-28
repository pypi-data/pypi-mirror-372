-- semantics_indexes
-- depends: 20250331_01_kRKjo-store-detections-id

CREATE INDEX pictures_semantics_keyval_idx ON pictures_semantics(key text_pattern_ops, value text_pattern_ops);
CREATE INDEX sequences_semantics_keyval_idx ON sequences_semantics(key text_pattern_ops, value text_pattern_ops);
CREATE INDEX annotations_semantics_keyval_idx ON annotations_semantics(key text_pattern_ops, value text_pattern_ops);
