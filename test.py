import requests

API_KEY = '55b1bc4558c219fad8f4fe0408eb2f32723ce1e7b067754468a44c1a4844a24e'  # Replace with your SerpAPI key

# List of vulnerability keywords to search for
keywords = [
    'vulnerability disclosure page',
    'security advisory page',
    'vulnerability bulletin',
    'vulnerability updates',
    'security flaw report',
    'vulnerability alert'
]


# Function to search using SerpAPI and collect URLs
def get_search_results(query, time_filter=''):
    params = {
        'q': query,
        'hl': 'en',
        'gl': 'us',
        'api_key': API_KEY,
        'tbs': time_filter  # Add the time filter parameter
    }
    response = requests.get('https://serpapi.com/search.json', params=params)
    data = response.json()
    urls = [result['link'] for result in data.get('organic_results', [])]
    return urls


# Storing links in a set to remove duplicates
all_links = set()  # Using set to avoid duplicates

company = "cisco"

# Get results for each keyword with the time filter for the past 24 hours
for keyword in keywords:
    # Search with time filter for the past 24 hours
    results_24hrs = get_search_results(company + " " + keyword, 'qdr:d')  # qdr:d filters to the past day
    all_links.update(results_24hrs)

# Converting set back to a list and printing the unique links
unique_links = list(all_links)
print("Unique Links:")
for link in unique_links:
    print(link)

with open("links.txt", "w") as file:
    for link in unique_links:
        file.write(f"{link}\n")