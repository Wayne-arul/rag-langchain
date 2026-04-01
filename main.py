import streamlit as st
import requests
import hashlib
import openai

# Set your OpenAI API key
openai.api_key = ''  # Replace with your actual OpenAI API key

# Your existing functions

def fetch_webpage_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None

def calculate_hash(content):
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def query_openai_api(raw_html):
    prompt = f"""
    Study the HTML content and fill in the following details:

    1. Product Name
    2. Product Version
    3. OEM Name
    4. Severity Level (Critical/High)
    5. Vulnerability
    6. Mitigation Strategy
    7. Published Date
    8. Unique ID (CVE)

    Just give the above content only.

    HTML Content:
    {raw_html}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an AI assisting with extracting key information from vulnerability data."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content']

# Streamlit interface
st.title("OEM Vulnerability Scraper")
st.write("Enter the URL of the OEM page to scrape for vulnerabilities:")

# User input for the URL
url = st.text_input("URL", "")

if st.button("Scrape Vulnerabilities"):
    if url:
        content = fetch_webpage_content(url)

        if content:
            current_hash = calculate_hash(content)

            # Use session state to manage previous hash value
            if 'previous_hash' not in st.session_state:
                st.session_state['previous_hash'] = ""

            if current_hash != st.session_state['previous_hash']:
                st.write("Change detected in the webpage content.")
                extracted_info = query_openai_api(content)
                st.write("Extracted Information:")
                st.text_area("Vulnerability Information", extracted_info, height=300)
                st.session_state['previous_hash'] = current_hash
            else:
                st.write("No changes detected in the webpage content.")
        else:
            st.error("Failed to fetch the webpage content.")
    else:
        st.error("Please enter a valid URL.")
