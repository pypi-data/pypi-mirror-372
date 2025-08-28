from geovisio.utils.auth import Account, AccountRole


def test_Account_can_check_reports():
    a = Account(id="00000000-0000-0000-0000-0000000000", name="Toto", oauth_provider="test", oauth_id="test", role=AccountRole.user)
    assert not a.can_check_reports()

    a.role = AccountRole.admin
    assert a.can_check_reports()


def test_account_serialization():
    """The role should not be persisted in the account"""
    a = Account(
        id="00000000-0000-0000-0000-0000000000",
        name="Toto",
        oauth_provider="test",
        oauth_id="test",
        role=AccountRole.admin,
        tos_accepted=True,
    )
    assert a.model_dump() == {
        "id": "00000000-0000-0000-0000-0000000000",
        "name": "Toto",
        "oauth_provider": "test",
        "oauth_id": "test",
        "tos_accepted": True,
    }


def test_account_lazy_role_loading(app, dburl, defaultAccountID, camilleAccountID):
    """The role should not be lazy loaded since it's not stored in the cookie"""

    with app.app_context():
        camille = Account(id=str(camilleAccountID), name="Toto", oauth_provider="test", oauth_id="test")
        assert camille.role == AccountRole.user

        default_account = Account(id=str(defaultAccountID), name="Toto", oauth_provider="test", oauth_id="test")
        assert default_account.role == AccountRole.admin
