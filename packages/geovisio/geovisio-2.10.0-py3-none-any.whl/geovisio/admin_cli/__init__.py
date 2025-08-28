from flask import Blueprint
from flask import cli
from flask.cli import with_appcontext
import click
import logging
from . import default_account_tokens, reorder_sequences, sequence_heading, cleanup, db, user

bp = Blueprint("cli", __name__)

bp.register_blueprint(default_account_tokens.bp, cli_group="default-account-tokens")
bp.register_blueprint(user.bp, cli_group=None)
bp.register_blueprint(db.bp, cli_group="db")


@bp.cli.command("set-sequences-heading")
@click.option("--value", show_default=True, default=0, help="Heading value relative to movement path (in degrees)")
@click.option("--overwrite", is_flag=True, show_default=True, default=False, help="Overwrite existing heading values in database")
@click.argument("sequencesIds", nargs=-1)
@with_appcontext
def set_sequences_heading(sequencesids, value, overwrite):
    """Changes pictures heading metadata.
    This uses the sequence movement path to compute new heading value.
    """
    sequence_heading.setSequencesHeadings(sequencesids, value, overwrite)


@bp.cli.group("sequences")
def sequences():
    """Commands to handle operations on sequences"""
    pass


@sequences.command("reorder")
@click.argument("sequence_ids", nargs=-1)
@with_appcontext
def reorder(sequence_ids):
    """Reorders sequences by ascending timestamp.
    If no sequence ID is given, all sequences will be updated"""
    all = len(sequence_ids) == 0
    reorder_sequences.reorder_sequences(all, sequence_ids)


@bp.cli.command("cleanup")
@click.option("--full", is_flag=True, show_default=True, default=False, help="For full cleanup (DB, cache, original pictures)")
@click.option("--database", is_flag=True, show_default=True, default=False, help="Deletes database entries")
@click.option("--cache", is_flag=True, show_default=True, default=False, help="Deletes cached derivates files (except blur masks)")
@click.option("--permanent-pictures", is_flag=True, show_default=True, default=False, help="Deletes only original pictures")
@click.argument("sequencesIds", nargs=-1)
@with_appcontext
def cleanup_cmd(sequencesids, full, database, cache, permanent_pictures):
    """Cleans up GeoVisio files and database."""
    if full is False and database is False and cache is False and permanent_pictures is False:
        full = True
    cleanup.cleanup(sequencesids, full, database, cache, permanent_pictures)


# Deprecated functions


@bp.cli.command("process-sequences")
@with_appcontext
def process_sequences():
    """Deprecated entry point, use https://gitlab.com/panoramax/clients/cli to upload a sequence instead"""
    logging.error("This function has been deprecated, use https://gitlab.com/panoramax/clients/cli to upload a sequence instead.")
    logging.error(
        "To upload a sequence with this tool, install it with `pip install geovisio_cli`, then run:\ngeovisio upload --path <directory> --api-url <api-url>"
    )


@bp.cli.command("redo-sequences")
@click.argument("sequences", nargs=-1)
@with_appcontext
def redo_sequences(sequences):
    """Re-processes already imported sequences.
    This updates database and derivates according to changes in original picture files.
    """
    logging.error("This function has been removed, if you need it back, feel free to open an issue")
