from langchain import hub
from langchain_community.document_loaders import UnstructuredHTMLLoader, WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.llms.openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import os
import warnings

# Suppress specific warnings. Oru deprecation error throw pannudhu, from langsmith
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)


os.environ["OPENAI_API_KEY"] = ""
os.environ["LANGCHAIN_API_KEY"] = ""
LANGCHAIN_API_KEY = ""
LANGCHAIN_TRACING_V2 = "true"

# Here we are Loading HTML data . Idhuve parse pannirum
loader = WebBaseLoader("https://www.rewterz.com/threat-advisory/multiple-cisco-ios-xr-software-vulnerabilities")
documents = loader.load()

# Now we Split the text
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(documents)

# Create embeddings
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(texts, embeddings)

# We are pulling the prompt from the hub
prompt = hub.pull("rlm/rag-prompt")

# Format the documents for the chain so that the retriver could easily query
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Setting up LCEL RAG chain in replacment of retriever
qa_chain = (
    {
        "context": vectorstore.as_retriever() | format_docs,
        "question": RunnablePassthrough(),
    }
    | prompt
    | OpenAI()
    | StrOutputParser()
)

# Here we are trying to query the RAG
query = "What is the recent CVE mentioned here? Today's date is September 17 ,2024"
result = qa_chain.invoke(query)

print(result)
