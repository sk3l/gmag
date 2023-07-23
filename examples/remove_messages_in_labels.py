from sys import argv, exit

from pygmail.types import MESSAGE_CONTENT_ID_ONLY, Account

if __name__ == "__main__":
    account = Account.from_environment(load_labels=True)

    label_file = argv[1]
    if not label_file:
        print("Usage: remove_messages_in_labels.py <input_file>")
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
            print(f"Label {label_name} not found")
            continue

        print(f"Loading messages to delete for label {label_name}")
        label.load_messages(contents=MESSAGE_CONTENT_ID_ONLY)
        print(f"Discarding {len(label.messages())} in label {label_name}")

        label.discard_messages()
