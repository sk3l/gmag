from pygmail.types import Account


def test_account():
    account = Account("YOUR EMAIL GOES HERE")
    assert account.email_address() == "YOUR EMAIL GOES HERE"
