from pygmail.types import Account, MESSAGE_CONTENT_MINIMAL

acct = Account.from_environment(load_labels=True)

label = acct.get_label_by_name("Finance/Fidelity")
label.load_messages(contents=MESSAGE_CONTENT_MINIMAL)

for message in label.messages():
    print(f"Message ID={message.message_id()}, Type={message.content_type()}, Content={message.content()}")
