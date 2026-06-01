import os
import base64
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def clean_html(raw_html):
    """Strips out HTML code brackets so only text remains for the agent."""
    cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]+);')
    cleantext = re.sub(cleanr, '', raw_html)
    return " ".join(cleantext.split())

def extract_body_text(payload):
    """Recursively walks through an email payload to find the message body."""
    body = ""
    data = payload.get('body', {}).get('data', '')
    if data:
        decoded = base64.urlsafe_b64decode(data).decode('utf-8')
        if payload.get('mimeType') == 'text/html':
            return clean_html(decoded)
        return decoded

    parts = payload.get('parts', [])
    html_backup = ""
    for part in parts:
        part_data = part.get('body', {}).get('data', '')
        if part_data:
            decoded_part = base64.urlsafe_b64decode(part_data).decode('utf-8')
            if part['mimeType'] == 'text/plain':
                return decoded_part
            elif part['mimeType'] == 'text/html':
                html_backup = clean_html(decoded_part)
        if 'parts' in part:
            sub_body = extract_body_text(part)
            if sub_body:
                return sub_body
    return html_backup

def main():
    if not os.path.exists('token.json'):
        print("Missing token.json. Please re-run authentication.")
        return
        
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    try:
        service = build('gmail', 'v1', credentials=creds)
        
        # Removed the strict 'label:INBOX' filter to widen the net completely
        print("Checking account history and pulling a batch of 3 emails...")
        response = service.users().messages().list(userId='me', maxResults=3).execute()
        messages = response.get('messages', [])

        if not messages:
            print("No messages found in this entire Google account history.")
            return

        print(f"\nFound {len(messages)} messages. Starting sequential agent parsing loop...\n")

        for index, msg_item in enumerate(messages, start=1):
            msg_id = msg_item['id']
            message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
            
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '(No Subject)')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), '(Unknown Sender)')
            
            full_body = extract_body_text(message['payload'])

            print(f"================ BATCH EMAIL #{index} ================")
            print(f"From:    {sender}")
            print(f"Subject: {subject}")
            print("-----------------------------------------------------------")
            print("Extracted Content Preview:")
            print(full_body[:300] + ("..." if len(full_body) > 300 else ""))
            print("===========================================================\n")

    except Exception as error:
        print(f'An error occurred: {error}')

if __name__ == '__main__':
    main()
