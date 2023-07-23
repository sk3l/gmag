from sys import argv, exit

from pygmail.types import Account, Label

if __name__ == "__main__":
    account = Account.from_environment(load_labels=True)

    label_name = argv[1]
    if not label_name:
        print("Usage: remove_label.py <label>")
        exit(1)

    label = account.get_label_by_name(argv[1])
    if not label:
        print("Couldn't locate label to delete")
        exit(1)

    result = Label.delete(account, label.label_id())
    print(result)
