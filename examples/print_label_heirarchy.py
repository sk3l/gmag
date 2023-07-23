from pygmail.types import Account


def print_labels(label):
    if not label:
        return
    print(label.name())
    for child in label.child_labels():
        print_labels(child)


acct = Account.from_environment()
labels = acct.get_label_heirarchy()

for lbl in labels:
    print_labels(lbl)
