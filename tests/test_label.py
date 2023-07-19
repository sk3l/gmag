from pygmail.types import Account, Label


def test_label():
    account = Account("YOUR_ACCOUNT@gmail.com", load_labels=True)
    assert account.get_all_labels()

    label = account.get_label_by_name("Offers")
    assert label

    label.load_messages()
    assert label.messages()
