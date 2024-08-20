import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import base64
import json
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


CONFIG_FILE = 'config.json'

if not os.path.exists(CONFIG_FILE):
    raise FileNotFoundError(f"Configuration file {CONFIG_FILE} not found. Please create it and include the necessary settings.")

with open(CONFIG_FILE) as config_file:
    config = json.load(config_file)

# Access configuration values
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
TOKEN_PATH = config.get('TOKEN_PATH')
CREDENTIALS_PATH = config.get('CREDENTIALS_PATH')
EXCEL_PATH = config.get('EXCEL_FILE')
EMAIL_FROM = config.get('EMAIL_FROM')
EMAIL_TO = config.get('EMAIL_TO')

def authenticate_gmail_api():
    """Authenticate and return a Gmail API service instance."""
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def send_email(subject, body):
    """Send an email using the Gmail API."""
    service = authenticate_gmail_api()
    message = MIMEText(body)
    message['to'] = EMAIL_TO
    message['from'] = EMAIL_FROM
    message['subject'] = subject
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    
    create_message = {'raw': encoded_message}
    send_message = service.users().messages().send(userId="me", body=create_message).execute()
    print(f'Message Id: {send_message["id"]}')

def fetch_item_price(url):
    """Fetch the item name and price from a product page."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    item_name = soup.find('h1').text.strip()
    price_tag = soup.find('span', class_='ssr-product-price__value')
    current_price = price_tag.text.strip().split(',')[0] if price_tag else None
    
    return item_name, int(current_price)

def save_prices_to_excel(data):
    """Save the price data to an Excel file."""
    df = pd.DataFrame(data)
    pivot_df = pd.pivot_table(df, index='date', columns='item', values='price', aggfunc='first')
    

    if os.path.exists(EXCEL_PATH):
        existing_df = pd.read_excel(EXCEL_PATH, index_col='date')
        combined_df = pd.concat([existing_df, pivot_df])
        combined_df = combined_df[~combined_df.index.duplicated(keep='last')]
        combined_df.to_excel(EXCEL_PATH)
        return combined_df
    else:
        pivot_df.to_excel(EXCEL_PATH)
        return pivot_df

def check_for_price_drops(df, current_date, urls):
    """Check for price drops and send email alerts if any are found."""
    for i,item in enumerate(df.columns):
        if len(df[item]) > 1:
            if df[item].iloc[-1] < df[item].iloc[-2]:
                price_drop = df[item].iloc[-2] - df[item].iloc[-1]
                subject = f"Price Drop Alert for {item}"
                body = f"The price for {item} has dropped by {price_drop} EUR.\n\
                         New Price: {df[item].iloc[-1]} EUR\n\
                         Date: {current_date}\n\
                         Link: {urls[i]}"
                send_email(subject, body)

def main():
    urls = [
        'https://jysk.si/jedilnica/jedilniski-stoli/jedilniski-stol-adslev-olivno-zelena-tkanina/barva-hrasta',
        'https://jysk.si/jedilnica/jedilniski-stoli/jedilniski-stol-adslev-bez-tkanina/barva-hrasta',
        'https://jysk.si/jedilnica/jedilniski-stoli/jedilniski-stol-adslev-antracit-siva-tkanina/crna'
    ]
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    data = []
    
    for url in urls:
        item_name, current_price = fetch_item_price(url)
        data.append({'date': current_date, 'item': item_name, 'price': current_price})
    
    df = save_prices_to_excel(data)
    check_for_price_drops(df, current_date,urls)

if __name__ == "__main__":
    main()
    print("Price check completed successfully.")
