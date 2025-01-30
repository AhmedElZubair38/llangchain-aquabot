# from langchain_community.document_loaders import PyPDFDirectoryLoader, CSVLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_openai.embeddings import OpenAIEmbeddings
# from langchain_chroma import Chroma
# from uuid import uuid4
# import os
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Configuration
# DATA_PATH = r"/mnt/c/Users/USER/crewai-ollama/data"
# CHROMA_PATH = r"chroma_db"

# # Initialize the embeddings model
# embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")

# # Initialize the vector store
# vector_store = Chroma(
#     collection_name="example_collection",
#     embedding_function=embeddings_model,
#     persist_directory=CHROMA_PATH,
# )

# # Function to load PDFs and CSVs from the directory
# def load_documents(data_path):
#     documents = []

#     # Load PDF files
#     pdf_loader = PyPDFDirectoryLoader(data_path)
#     pdf_documents = pdf_loader.load()
#     documents.extend(pdf_documents)

#     # # Load CSV files
#     # for filename in os.listdir(data_path):
#     #     if filename.endswith(".csv"):
#     #         csv_loader = CSVLoader(file_path=os.path.join(data_path, filename), csv_args={"delimiter": ","})
#     #         csv_documents = csv_loader.load()
#     #         documents.extend(csv_documents)

#     return documents

# # Loading documents (PDFs and CSVs)
# raw_documents = load_documents(DATA_PATH)

# # Split the documents into chunks
# text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size=200,
#     chunk_overlap=50,
#     length_function=len,
#     is_separator_regex=False,
# )

# # Creating the chunks
# chunks = text_splitter.split_documents(raw_documents)

# # Create unique IDs for each chunk
# uuids = [str(uuid4()) for _ in range(len(chunks))]

# # Adding chunks to the vector store
# vector_store.add_documents(documents=chunks, ids=uuids)




from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_chroma import Chroma
from uuid import uuid4

# import the .env file
from dotenv import load_dotenv
load_dotenv()

# configuration
DATA_PATH = r"/mnt/c/Users/USER/crewai-ollama/data"
CHROMA_PATH = r"chroma_db"

# initiate the embeddings model
embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")

# initiate the vector store
vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings_model,
    persist_directory=CHROMA_PATH,
)

# loading the PDF document
loader = PyPDFDirectoryLoader(DATA_PATH)

raw_documents = loader.load()

# splitting the document
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=100,
    length_function=len,
    is_separator_regex=False,
)

# creating the chunks
chunks = text_splitter.split_documents(raw_documents)

# creating unique ID's
uuids = [str(uuid4()) for _ in range(len(chunks))]

# adding chunks to vector store
vector_store.add_documents(documents=chunks, ids=uuids)