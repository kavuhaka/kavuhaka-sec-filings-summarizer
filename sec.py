import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai
import html2text
import os

# Set OpenAI API Key
openai.api_key = "your_openai_api_key_here"

# Helper Functions
def fetch_filing_urls(symbol, filing_type):
    base_url = "https://www.sec.gov/cgi-bin/browse-edgar"
    params = {
        "action": "getcompany",
        "CIK": symbol,
        "type": filing_type,
        "dateb": "",
        "owner": "exclude",
        "start": "0",
        "count": "10",
        "output": "atom"
    }
    response = requests.get(base_url, params=params)
    return response.text

def parse_filing_links(xml_data):
    soup = BeautifulSoup(xml_data, 'html.parser')
    links = [entry.find('link').get('href') for entry in soup.find_all('entry')]
    return links

def fetch_filing_content(url):
    response = requests.get(url)
    return response.text

def clean_html(html_content):
    # Convert HTML to text using html2text
    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = False
    return text_maker.handle(html_content)

def summarize_text(text):
    prompt = f"Please summarize the following text:\n\n{text}\n\nSummarize the key financial points and risks."
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=500
    )
    return response.choices[0].text.strip()

# Streamlit UI
def app():
    st.title("SEC Filing Summarizer")
    st.sidebar.header("Enter Stock Symbol")
    
    # User input
    symbol = st.sidebar.text_input("Stock Ticker", "AAPL").upper().strip()
    
    if symbol:
        st.subheader(f"Fetching Filings for {symbol}")
        
        # Fetch 10-K, 10-Q, and 8-K URLs
        st.write("Fetching 10-K, 10-Q, and 8-K filings...")
        filing_types = ["10-K", "10-Q", "8-K"]
        
        filings = {}
        for filing_type in filing_types:
            xml_data = fetch_filing_urls(symbol, filing_type)
            filing_links = parse_filing_links(xml_data)
            filings[filing_type] = filing_links
        
        for filing_type, links in filings.items():
            st.write(f"### Latest {filing_type} Filing")
            if links:
                # Fetch the most recent filing
                filing_url = links[0]
                filing_html = fetch_filing_content(filing_url)
                cleaned_text = clean_html(filing_html)
                
                # Summarize the text
                summary = summarize_text(cleaned_text)
                st.write("#### Summary:")
                st.write(summary)
            else:
                st.write(f"No {filing_type} filings found.")
    
    else:
        st.warning("Please enter a valid stock ticker.")

# Run the app
if __name__ == "__main__":
    app()
