#!/usr/bin/env python3
""" pygmail - Python GMail API"""

from __future__ import print_function

# import base64
import os
import os.path

from google.auth.transport.requests import Request  # type: ignore
from google.oauth2.credentials import Credentials  # type: ignore
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
from googleapiclient.discovery import build  # type: ignore


class Account:
    """Encapsulate Google GMail account"""

    # If modifying these scopes, delete the file token.json.
    _SCOPES = ["https://mail.google.com/"]

    def __init__(self, user_id):
        self.api_conn_ = None
        self.user_id_ = user_id
        self.labels_ = {}
        # Initialize our API connection
        self.auth_and_connect()

    def auth_and_connect(self):
        """Execute Google OAuth flow to obtain API connection"""
        creds = None

        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", Account._SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "gmail-cli-auth-creds.json", Account._SCOPES
                )
            creds = flow.run_local_server(bind_addr="0.0.0.0", port=8080)

        # Save the credentials for the next run
        # TO DO - cache in memory
        with open("token.json", "w", encoding="UTF-8") as token:
            token.write(creds.to_json())

        self.api_conn_ = build("gmail", "v1", credentials=creds)

    def user_id(self):
        """GMail account user ID"""
        return self.user_id_

    def load_labels(self):
        """Load all labels recursively for the account"""
        labels = Label.get_all_labels(self)

        # Get a hash of everyle label by their name.
        # The final string in the label in the "/" delimted heirarchy path
        label_map = {}
        for label in labels:
            label_map[label.name()] = label

        # Recurse through the account label tree and add them to the account
        for label in labels:
            levels = label.path().split("/")
            print(f"Loading label tree {levels}")

            root_label = None
            if levels[0] in self.labels_:
                root_label = self.labels_[levels[0]]
            else:
                root_label = label_map[levels[0]]
                self.labels_[levels[0]] = root_label

            # print(f"Loading sublabel tree for top level label {levels[0]}")
            next_label = root_label
            for level in levels[1:]:
                if level not in next_label.sublabels():
                    new_label = label_map[level]
                    next_label.sublabels()[level] = new_label
                    next_label = new_label


class Label:
    """GMail email label"""

    def __init__(self, account, label_id, lazy_load=True):
        self.account_ = account
        self.label_id_ = label_id
        self.content_ = (
            self.account_.api_conn_.users()
            .labels()
            .get(userId="skelton.michael@gmail.com", id=label_id)
            .execute()
        )
        self.path_ = self.content_["name"]
        self.name_ = self.path_.split("/")[-1]
        self.messages_ = None
        self.sublabels_ = {}

        if not lazy_load:
            self.load_messages()

    @classmethod
    def get_all_labels(cls, account):
        """Retrieve a list of all labels under the GMail account"""
        result = (
            account.api_conn_.users().labels().list(userId=account.user_id()).execute()
        )
        label_list = []
        for label in result["labels"]:
            label_list.append(Label(account, label["id"]))
        return label_list

    def load_messages(self):
        """Load all messages *at top level only* for the message"""
        query = f"label:{self.name_}"

        result = (
            self.account_.api_conn_.users()
            .messages()
            .list(userId="skelton.michael@gmail.com", q=query)
            .execute()
        )
        self.messages_ = []
        if "messages" in result:
            for message in result.get("messages", None):
                if message:
                    self.messages_.append(
                        Message(self.account_.api_conn_, message.get("id", 0))
                    )

        while "nextPageToken" in result:
            page_token = result["nextPageToken"]
            result = (
                self.account_.api_conn_.users()
                .messages()
                .list(userId="me", q=query, pageToken=page_token)
                .execute()
            )
            if "messages" in result:
                for message in result.get("messages", None):
                    if message:
                        self.messages_.append(
                            Message(self.account_.api_conn_, message.get("id", 0))
                        )

    def discard_messages(self):
        """Send all messages *at top level only* to the trash folder"""
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

    def label_id(self):
        """Return Google internal ID for the label"""
        return self.label_id_

    def name(self):
        """Return text name for the label"""
        return self.name_

    def messages(self):
        """Return list of messages under the label"""
        return self.messages_

    def path(self):
        """Return label's fully qualified path in the account label tree"""
        return self.path_

    def add_label(self, label):
        """Add a new sublabel to the label"""
        self.sublabels_[label.name()] = label

    def sublabels(self):
        """Return the set of sublabels under this label"""
        return self.sublabels_


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
        """Fetch details about message from GMail server"""
        self.content_ = (
            self.api_conn_.users()
            .messages()
            .get(id=self.message_id_, userId="me", format=content_type)
            .execute()
        )

    def delete(self):
        """Permanently delete the message"""

    def discard(self):
        """Send the message to the trash folder"""
        return (
            self.api_conn_.users()
            .messages()
            .trash(userId="me", id=self.message_id_)
            .execute()
        )

    def content(self):
        """Show the content, body and metadata, of the message"""
        return self.content_
