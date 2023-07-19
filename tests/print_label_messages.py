from pygmail.types import Account, MESSAGE_CONTENT_MINIMAL

acct = Account("YOUR_ACCOUNT@gmail.com", load_labels=True)

label = acct.get_label_by_name("YOUR/LABEL")
label.load_messages(contents=MESSAGE_CONTENT_MINIMAL)

for message in label.messages():
    print(f"Message ID={message.message_id()}, Type={message.content_type()}, Content={message.content()}")
