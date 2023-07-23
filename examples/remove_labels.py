from sys import argv, exit

from pygmail.types import Account, Label

if __name__ == "__main__":
    account = Account.from_environment(load_labels=True)

    label_file = argv[1]
    if not label_file:
        print("Usage: remove_labels.py <input_file>")
        exit(1)

    label_names = None
    with open(argv[1]) as fh:
        label_names = fh.readlines()

    if not label_names:
        print("Label file is empty!")
        exit(1)

    for label_name in label_names:
        label = account.get_label_by_name(label_name.strip())
        if not label:
            print(f"Couldn't locate label {label_name} to delete")
            continue

        print(f"Deleting label, name={label.name()}, ID={label.label_id()}")
        try:
            result = Label.delete(account, label.label_id())
            print(result)
        except Exception as e:
            print(e)
