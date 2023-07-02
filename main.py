#!/usr/bin/env python3
""" gmag - GMail Aggregator """

from __future__ import print_function

import base64
import json
import os
import os.path
from email.mime.text import MIMEText

from google.auth.transport.requests import Request  # type: ignore
from google.oauth2.credentials import Credentials  # type: ignore
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
from googleapiclient.discovery import build  # type: ignore

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
    with open("token.json", "w") as token:
        token.write(creds.to_json())


service = build("gmail", "v1", credentials=creds)


def search_messages(svc, query):
    """search_messages"""
    result = (
        svc.users()
        .messages()
        .list(userId="skelton.michael@gmail.com", q=query)
        .execute()
    )
    messages = []
    if "messages" in result:
        messages.extend(result["messages"])
    while "nextPageToken" in result:
        page_token = result["nextPageToken"]
        result = (
            svc.users()
            .messages()
            .list(userId="me", q=query, pageToken=page_token)
            .execute()
        )
        if "messages" in result:
            messages.extend(result["messages"])
    return messages


if __name__ == "__main__":
    # print("Searching messages in label:Home")
    msgs = search_messages(service, "label:Home")

    # print(msgs)
    for msg in msgs:
        message = (
            service.users()
            .messages()
            .get(id=msg["id"], userId="me", format="metadata")
            .execute()
        )
        print(json.dumps(message))
