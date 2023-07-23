#!/usr/bin/env python3
""" pygmail - Python GMail API"""

from __future__ import print_function

# import base64h
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

    @classmethod
    def from_environment(cls, load_labels=False, creds_path=os.path.curdir):
        """Read account name from environment variable"""
        account_name = os.environ.get("GMAIL_ACCOUNT", None)
        account = None
        if account_name:
            account = Account(account_name, load_labels, creds_path)
        return account

    def __init__(self, user_id, load_labels=False, creds_path=os.path.curdir):
        self.api_conn_ = None
        self.user_id_ = user_id
        self.labels_by_name_ = {}  # Map of all account Labels, keyed by name
        self.labels_by_id_ = {}  # Map of all account Labels, keyed by ID
        self.labels_ = []  # All Label objects in the account
        self.creds_path_ = creds_path  # Location to look for OAuth tokens ets

        # Initialize our API connection
        self.auth_and_connect()

        profile = self.api_conn_.users().getProfile(userId=self.user_id_).execute()

        self.email_address_ = profile.get("emailAddress", None)
        self.messages_count_ = profile.get("messagesTotal", None)
        self.threads_conts_ = profile.get("threadsTotal", None)
        self.history_id_ = profile.get("historyId", None)

        if load_labels:
            self.load_labels()

    def auth_and_connect(self):
        """Execute Google OAuth flow to obtain API connection"""
        creds = None

        token_file = os.path.join(self.creds_path_, "token.json")
        auth_creds_file = os.path.join(self.creds_path_, "gmail-cli-auth-creds.json")

        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, Account._SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    auth_creds_file, Account._SCOPES
                )
                creds = flow.run_local_server(bind_addr="0.0.0.0", port=8080)
        # Save the credentials for the next run
        # TO DO - cache in memory
        with open(token_file, "w", encoding="UTF-8") as token:
            token.write(creds.to_json())

        self.api_conn_ = build("gmail", "v1", credentials=creds)

    def load_labels(self):
        """Retrieve a the list of  all Labels under the GMail account"""
        result = self.api_conn_.users().labels().list(userId=self.user_id()).execute()

        for item in result["labels"]:
            identifier = item["id"]
            name = item["name"]
            label = Label(self, identifier, name)

            self.labels_.append(label)
            self.labels_by_id_[identifier] = label
            self.labels_by_name_[name] = label

    def user_id(self):
        """GMail account user ID"""
        return self.user_id_

    def email_address(self):
        """Return account email address"""
        return self.email_address_

    def messages_count(self):
        """Return account's total messsage count"""
        return self.messages_count_

    def threads_count(self):
        """Return account's total threads count"""
        return self.threads_conts_

    def history_id(self):
        """Return account's history ID"""
        return self.history_id_

    def get_label_heirarchy(self):
        """Load the label heirarchy for the account"""
        if not self.labels_:
            self.load_labels()

        # Organize all labels by level
        levels = []
        for label in self.labels_:
            level = len(label.name().split("/"))
            while len(levels) < level:
                levels.append({})
            levels[level - 1][label.short_name()] = label

        # Traverse the labels by level, and add child labels
        # to their parent label
        for i in range(1, len(levels)):
            for _, val in levels[i].items():
                path = val.name().split("/")
                parent_name = path[len(path) - 2]
                parent = levels[i - 1].get(parent_name, None)
                if parent:
                    parent.child_labels_.append(val)

        return list(levels[0].values())

    def get_all_labels(self):
        """Return flattened list of all the Account's Label"""
        return self.labels_

    def get_label_by_name(self, name):
        """Return a Label by name lookup"""
        return self.labels_by_name_.get(name, None)

    def get_label_by_id(self, label_id):
        """Return a Label by id lookup"""
        return self.labels_by_id_.get(label_id, None)


MESSAGE_CONTENT_ID_ONLY = "id_only"
MESSAGE_CONTENT_MINIMAL = "minimal"
MESSAGE_CONTENT_METADATA = "metadata"
MESSAGE_CONTENT_FULL = "full"


class Label:
    """GMail email label"""

    @classmethod
    def delete(cls, account, label_id):
        result = (
            account.api_conn_.users()
            .labels()
            .delete(userId="me", id=label_id)
            .execute()
        )
        return result


    def __init__(self, account, label_id, name, lazy_load=True):
        self.account_ = account
        self.label_id_ = label_id
        self.name_ = name
        self.messages_ = None
        self.child_labels_ = []

        if not lazy_load:
            self.load_messages()

    def load_messages(self, reload=False, contents=MESSAGE_CONTENT_MINIMAL):
        """Load all messages *at top level only* for the message"""
        if self.messages_ and not reload:
            return

        query = f"label:{self.name_}"

        result = (
            self.account_.api_conn_.users()
            .messages()
            .list(userId=self.account_.user_id(), q=query)
            .execute()
        )
        self.messages_ = []
        if "messages" in result:
            for message in result.get("messages", None):
                if message:
                    self.messages_.append(
                        Message(self.account_.api_conn_, message.get("id", 0), content_type=contents)
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
                            Message(self.account_.api_conn_, message.get("id", 0), content_type=contents)
                        )

    def discard_messages(self):
        """Send all messages *at top level only* to the trash folder"""
        for message in self.messages():
            print(f"Discarding message , ID={message.message_id()}")
            message.discard()

    def label_id(self):
        """Return Google internal ID for the label"""
        return self.label_id_

    def name(self):
        """Return text name for the label"""
        return self.name_

    def short_name(self):
        """Return the brief Label name, e.g. Foo/Bar/Bat returns Bat"""
        return self.name_.split("/")[-1]

    def messages(self):
        """Return list of messages under the label"""
        return self.messages_

    def child_labels(self):
        """Return list of child labels under the label"""
        return self.child_labels_


class Message:
    """GMail email message"""

    def __init__(self, api_conn, msg_id, content_type=MESSAGE_CONTENT_MINIMAL):
        self.api_conn_ = api_conn
        self.message_id_ = msg_id
        self.content_type_ = MESSAGE_CONTENT_ID_ONLY
        self.content_ = None
        self.load_message(content_type)

    def load_message(self, content_type):
        """Fetch details about message from GMail server"""
        if self.content_type_ != content_type:
            if content_type == MESSAGE_CONTENT_ID_ONLY:
                self.clear()
            else:
                self.content_ = (
                    self.api_conn_.users()
                    .messages()
                    .get(id=self.message_id_, userId="me", format=content_type)
                    .execute()
                )
            self.content_type_ = content_type

    def clear(self):
        """Remove content from the Message"""
        self.content_type_ = MESSAGE_CONTENT_ID_ONLY
        self.content_ = None

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

    def message_id(self):
        """Show the message ID"""
        return self.message_id_

    def content_type(self):
        """Show the content type"""
        return self.content_type_

    def content(self):
        """Show the content, body and metadata, of the message"""
        return self.content_
