import requests
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.llms.openai import OpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import os
import warnings

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Set environment variables
os.environ["OPENAI_API_KEY"] = "sk-EZDUV2rBv23pRIaqL0EI10AiDTmmVtvcnbjgAasHnRT3BlbkFJfQGSSg0OIM6BC5Sm_3CEpNgRkFEUwowvE6DJaL5gcA"
os.environ["LANGCHAIN_API_KEY"] = "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"
LANGCHAIN_API_KEY = "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"
LANGCHAIN_TRACING_V2 = "true"

API_KEY = '55b1bc4558c219fad8f4fe0408eb2f32723ce1e7b067754468a44c1a4844a24e'  # Replace with your SerpAPI key

# Keywords to search for vulnerabilities
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
        'tbs': time_filter  # Time filter for recent results
    }
    response = requests.get('https://serpapi.com/search.json', params=params)
    data = response.json()
    urls = [result['link'] for result in data.get('organic_results', [])]
    return urls


# Storing links in a set to remove duplicates
all_links = set()

company = "cisco"  # Modify this as needed

# Get results for each keyword with the time filter for the past 24 hours
for keyword in keywords:
    results_24hrs = get_search_results(company + " " + keyword, 'qdr:d')  # Search for past day
    all_links.update(results_24hrs)

# Convert set back to a list for processing
unique_links = list(all_links)

# List to collect all documents from all URLs
all_documents = []

# Load and process each URL
for url in unique_links:
    try:
        print(f"Processing URL: {url}")

        # Load the HTML content from the URL
        loader = WebBaseLoader(url)
        documents = loader.load()

        # Append documents to the main list
        all_documents.extend(documents)

    except Exception as e:
        print(f"Failed to process {url}: {e}")

# Now we Split the combined text from all documents
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(all_documents)

# Create embeddings from the text
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(texts, embeddings)

# We are pulling the prompt from the hub
prompt = hub.pull("rlm/rag-prompt")


# Format the documents for the chain so that the retriver could easily query
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# Setting up LCEL RAG chain in replacement of retriever
qa_chain = (
        {
            "context": vectorstore.as_retriever() | format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | OpenAI()
        | StrOutputParser()
)

# After all URLs are processed, we now query the RAG chain
query = "What are the recent CVEs mentioned across all sources? Today's date is September 17, 2024."
result = qa_chain.invoke(query)

print("Final Result:")
print(result)
