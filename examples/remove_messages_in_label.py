from sys import argv, exit

from pygmail.types import Account

if __name__ == "__main__":
    account = Account.from_environment(load_labels=True)

    label_name = argv[1]
    if not label_name:
        print("Usage: remove_messages_in_label.py <label>")
        exit(1)

    label = account.get_label_by_name(label_name)
    if not label:
        print(f"Label {label_name} not found")
        exit(1)

    label.load_messages()
    print(f"Discarding {len(label.messages())} in label {label_name}")

    label.discard_messages()
