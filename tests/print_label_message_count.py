from pygmail.types import MESSAGE_CONTENT_ID_ONLY, Account

SKIP_LABELS = set(("CHAT", "IMPORTANT", "SENT", "TRASH", "UNREAD", "STARRED"))


def print_labels(label):
    if not label:
        return
    if label.name() in SKIP_LABELS:
        return

    label.load_messages(contents=MESSAGE_CONTENT_ID_ONLY)
    print(f"{label.name()} has {len(label.messages())} in it")
    for child in label.child_labels():
        print_labels(child)


acct = Account("YOUR_ACCOUNT@gmail.com")
labels = acct.get_label_heirarchy()

for lbl in labels:
    print_labels(lbl)
