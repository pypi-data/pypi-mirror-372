import psycopg
from flask import current_app
from fs.path import dirname
import logging
from geovisio import utils
import geovisio.utils.filesystems


log = logging.getLogger("geovisio.cli.cleanup")


def cleanup(sequences=[], full=False, database=False, cache=False, permanentPics=False):
    """Cleans up various data or files of GeoVisio

    Parameters
    ----------
    sequences : list
            List of sequences IDs to clean-up. If none is given, all sequences are cleaned up.
    full : bool
            For full cleaning (deletes DB entries and derivates files including blur masks)
    database : bool
            For removing database entries without deleting derivates files
    cache : bool
            For removing derivates files
    permanentPics : bool
            For removing original picture file
    """

    if full:
        database = True
        cache = True
        permanentPics = True

    if database is False and cache is False and permanentPics is False:
        return True

    allSequences = len(sequences) == 0

    with psycopg.connect(current_app.config["DB_URL"], autocommit=True) as conn:
        fses = current_app.config["FILESYSTEMS"]
        if allSequences:
            pics = [str(p[0]) for p in conn.execute("SELECT id FROM pictures").fetchall()]
        else:
            # Find pictures in sequences to cleanup
            pics = [
                str(p[0])
                for p in conn.execute(
                    """
				WITH pic2rm AS (
					SELECT DISTINCT pic_id FROM sequences_pictures WHERE seq_id = ANY(%(seq)s)
				)
				SELECT * FROM pic2rm
				EXCEPT
				SELECT DISTINCT pic_id FROM sequences_pictures WHERE pic_id IN (SELECT * FROM pic2rm) AND seq_id != ANY(%(seq)s)
			""",
                    {"seq": sequences},
                ).fetchall()
            ]

        if database:
            log.info("Cleaning up database...")
            if allSequences:
                conn.execute("DELETE FROM job_queue")
                conn.execute("DELETE FROM sequences_pictures")
                conn.execute("DELETE FROM sequences")
                conn.execute("DELETE FROM pictures")
            else:
                conn.execute("DELETE FROM job_queue WHERE picture_id = ANY(%s)", [pics])
                conn.execute("DELETE FROM sequences_pictures WHERE seq_id = ANY(%s)", [sequences])
                conn.execute("DELETE FROM sequences WHERE id = ANY(%s)", [sequences])
                conn.execute("DELETE FROM pictures WHERE id = ANY(%s)", [pics])

            conn.close()

        if permanentPics:
            log.info("Cleaning up original files...")
            if allSequences:
                geovisio.utils.filesystems.removeFsTreeEvenNotFound(fses.permanent, "/")
            else:
                for picId in pics:
                    geovisio.utils.filesystems.removeFsTreeEvenNotFound(fses.permanent, dirname(utils.pictures.getHDPicturePath(picId)))

        if cache:
            log.info("Cleaning up derivates files...")
            if allSequences:
                geovisio.utils.filesystems.removeFsTreeEvenNotFound(fses.derivates, "/")
            else:
                for picId in pics:
                    picPath = utils.pictures.getPictureFolderPath(picId)
                    # Many paths are not used anymore in GeoVisio >= 2.0.0
                    # But are kept for retrocompatibility
                    geovisio.utils.filesystems.removeFsEvenNotFound(fses.derivates, picPath + "/blurred.webp")
                    geovisio.utils.filesystems.removeFsEvenNotFound(fses.derivates, picPath + "/thumb.webp")
                    geovisio.utils.filesystems.removeFsEvenNotFound(fses.derivates, picPath + "/sd.webp")
                    geovisio.utils.filesystems.removeFsTreeEvenNotFound(fses.derivates, picPath + "/tiles")
                    geovisio.utils.filesystems.removeFsEvenNotFound(fses.derivates, picPath + "/blurred.jpg")
                    geovisio.utils.filesystems.removeFsEvenNotFound(fses.derivates, picPath + "/thumb.jpg")
                    geovisio.utils.filesystems.removeFsEvenNotFound(fses.derivates, picPath + "/sd.jpg")
                    geovisio.utils.filesystems.removeFsEvenNotFound(fses.derivates, picPath + "/progressive.jpg")
                    geovisio.utils.filesystems.removeFsEvenNotFound(fses.derivates, picPath + "/blur_mask.png")

                    if fses.derivates.isdir(picPath) and fses.derivates.isempty(picPath):
                        fses.derivates.removedir(picPath)

        # Remove empty group of pictures folders
        if cache or permanentPics:
            for fs in [fses.tmp, fses.derivates, fses.permanent]:
                for picDir in fs.walk.dirs(search="depth"):
                    if fs.isempty(picDir):
                        fs.removedir(picDir)

    log.info("Cleanup done")
    return True
