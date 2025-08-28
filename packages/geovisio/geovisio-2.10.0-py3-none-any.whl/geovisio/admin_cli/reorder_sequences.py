import logging
from flask import current_app
import psycopg
from typing import List


def reorder_sequences(all: bool, sequence_ids: List[str]):
    """Reorder all sequences by timestamp"""
    logging.info(f"Reordering {'all ' if all else ''}sequences{f'({sequence_ids})' if  sequence_ids else ''}")
    params = {}
    if sequence_ids:
        params["seq_ids"] = [s for s in sequence_ids]
    filter_sequences_pictures = "" if all else "WHERE sp.seq_id = ANY(%(seq_ids)s)"
    filter_sequences = "" if all else "WHERE id = ANY(%(seq_ids)s)"
    with psycopg.connect(current_app.config["DB_URL"], options="-c statement_timeout=30000") as conn:
        with conn.cursor() as cursor:
            # To avoid conflicts on rank uniqness, first pass update all ranks with an offset
            cursor.execute(
                f"""
WITH ordered_pics AS (
    SELECT
        sp.seq_id as seq_id,
        MAX(sp.rank) OVER (PARTITION BY sp.seq_id) AS max_rank,
        p.id AS pic_id,
        RANK() OVER (
            PARTITION BY sp.seq_id
            ORDER BY p.ts, p.metadata->>'originalFileName'
        ) as new_rank,
        sp.rank as old_rank,
        p.ts, p.metadata->>'originalFileName' AS originalFileName
    FROM pictures p
    JOIN sequences_pictures sp ON sp.pic_id = p.id
    {filter_sequences_pictures}
)
UPDATE 
    sequences_pictures sp
SET
    rank = ordered_pics.new_rank + ordered_pics.max_rank
FROM ordered_pics
WHERE ordered_pics.seq_id = sp.seq_id AND ordered_pics.pic_id = sp.pic_id
;
                           """,
                params=params,
            )

            # Then we recompute all rank to remove the offset
            cursor.execute(
                f"""
WITH ordered_pics AS (
    SELECT
        sp.seq_id as seq_id,
        MIN(sp.rank) OVER (PARTITION BY sp.seq_id) AS min_rank,
        sp.rank AS rank,
        p.id AS pic_id
    FROM pictures p
    JOIN sequences_pictures sp ON sp.pic_id = p.id
    {filter_sequences_pictures}
)
UPDATE 
    sequences_pictures sp
SET
    rank = ordered_pics.rank - ordered_pics.min_rank + 1
FROM ordered_pics
WHERE ordered_pics.seq_id = sp.seq_id AND ordered_pics.pic_id = sp.pic_id
;
""",
                params=params,
            )
            # Then we update the sequences shapes
            cursor.execute(
                f"""
UPDATE
    sequences
SET
    geom = ST_MakeLine(
        ARRAY(
            SELECT
                p.geom
            FROM
                sequences_pictures sp
                JOIN pictures p ON sp.pic_id = p.id
            WHERE
                sp.seq_id = sequences.id
            ORDER BY
                sp.rank
            )
    )
{filter_sequences}
;
                           """,
                params=params,
            )
            conn.commit()
            logging.info("All sequences reordered")
