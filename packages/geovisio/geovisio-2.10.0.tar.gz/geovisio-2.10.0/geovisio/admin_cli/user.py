from uuid import UUID
from attr import dataclass
import click
from flask import Blueprint, current_app
from flask.cli import with_appcontext
from geovisio.utils import db
from geovisio.utils.auth import AccountRole
from psycopg.rows import dict_row

bp = Blueprint("user", __name__)


@dataclass
class Account:
    id: UUID
    name: str


@bp.cli.command("user")
@click.argument("account_id_or_name")
@click.option("--set-role", required=True, help="Role you want to give to the account. Must be one of: admin or user")
@click.option("--create", is_flag=True, show_default=True, default=False, help="If provided, create the account if it does not exist")
@with_appcontext
def update_user(account_id_or_name, set_role=None, create=False):
    """
    Update some information about a user.
    To identify the account, either the account_id or the account_name must be provided.
    """
    with db.conn(current_app) as conn, conn.cursor(row_factory=dict_row) as cursor:

        account = get_account(cursor, account_id_or_name, create)

        if set_role is not None:
            update_role(cursor, account, set_role)


def get_account(cursor, account_id_or_name, create):
    account_id = None
    account_name = None
    try:
        account_id = UUID(account_id_or_name)
    except ValueError:
        account_name = account_id_or_name

    if account_id is not None:
        r = cursor.execute("SELECT id, name FROM accounts WHERE id = %s", [account_id]).fetchall()
    elif account_name is not None:
        r = cursor.execute("SELECT id, name FROM accounts WHERE name = %s", [account_name]).fetchall()
    else:
        raise click.ClickException("You must provide either an account_id or an account_name")

    if create and not r:
        if account_id is not None:
            raise click.ClickException("You cannot create an account with an account_id, a name must be provided")
        r = cursor.execute("INSERT INTO accounts (name) VALUES (%s) RETURNING id, name", [account_name]).fetchall()

    if not r:
        raise click.ClickException(f"Account {account_id_or_name} not found")
    if len(r) > 1:
        print(f"Several accounts found with name {account_id_or_name}")
        for i in r:
            print(f" * {i['id']}")
        raise click.ClickException(f"Please provide an account_id instead")

    return Account(id=r[0]["id"], name=r[0]["name"])


def update_role(cursor, account, role):
    try:
        role = AccountRole(role)
    except ValueError:
        raise click.ClickException(f"Role {role} is not valid. Must be one of: admin or user")

    print(f"Adding role {role.value} to account {account.name} ({account.id})")
    cursor.execute("UPDATE accounts SET role = %s WHERE id = %s", [role.value, account.id])
