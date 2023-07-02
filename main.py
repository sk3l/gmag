#!/usr/bin/env python3
""" gmail-cli - GMail Command L"""

from __future__ import print_function

# import base64
import json
import os
import os.path

from google.auth.transport.requests import Request  # type: ignore
from google.oauth2.credentials import Credentials  # type: ignore
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
from googleapiclient.discovery import build  # type: ignore

# from email.mime.text import MIMEText


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://mail.google.com/"]

creds = None

if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file("gmag-auth-creds.json", SCOPES)
        creds = flow.run_local_server(bind_addr="0.0.0.0", port=8080)
    # Save the credentials for the next run
    with open("token.json", "w", encoding="UTF-8") as token:
        token.write(creds.to_json())


google_api_client = build("gmail", "v1", credentials=creds)


class Message:
    """GMail email message"""

    CONTENT_MINIMAL = "minimal"
    CONTENT_METADATA = "metadata"
    CONTENT_FULL = "full"

    def __init__(self, api_conn, msg_id, content_type=CONTENT_METADATA):
        self.api_conn_ = api_conn
        self.content_type_ = content_type
        self.message_id_ = msg_id
        self.content_ = None
        self.load_message(self.content_type_)

    def load_message(self, content_type):
        self.content_ = (
            self.api_conn_.users()
            .messages()
            .get(id=self.message_id_, userId="me", format=content_type)
            .execute()
        )

    def delete(self):
        pass

    def discard(self):
        return (
            self.api_conn_.users()
            .messages()
            .trash(userId="me", id=self.message_id_)
            .execute()
        )

    def content(self):
        return self.content_


class Label:
    """GMail email label"""

    def __init__(self, api_conn, name):
        self.api_conn_ = api_conn
        self.name_ = name
        self.messages_ = None

    def load_messages(self):
        query = f"label:{self.name_}"

        result = (
            self.api_conn_.users()
            .messages()
            .list(userId="skelton.michael@gmail.com", q=query)
            .execute()
        )
        self.messages_ = []
        if "messages" in result:
            for message in result.get("messages", None):
                if message:
                    self.messages_.append(Message(self.api_conn_, message.get("id", 0)))

        while "nextPageToken" in result:
            page_token = result["nextPageToken"]
            result = (
                self.api_conn_.users()
                .messages()
                .list(userId="me", q=query, pageToken=page_token)
                .execute()
            )
            if "messages" in result:
                for message in result.get("messages", None):
                    if message:
                        self.messages_.append(
                            Message(self.api_conn_, message.get("id", 0))
                        )

    def discard_messages(self):
        for message in self.messages():
            headers = message.content()["payload"]["headers"]
            subject = next(
                header["value"] for header in headers if header["name"] == "Subject"
            )
            from_addr = next(
                header["value"] for header in headers if header["name"] == "From"
            )
            print(f"Discarding message , subject={subject}, from={from_addr}")
            message.discard()

    def messages(self):
        return self.messages_


if __name__ == "__main__":
    # print("Searching messages in label:Home")
    label = Label(google_api_client, "bills-retail")
    label.load_messages()
    print(json.dumps(label.messages()))
    # label.discard_messages()
