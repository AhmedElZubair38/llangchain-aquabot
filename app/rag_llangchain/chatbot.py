from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
import gradio as gr
from langchain_deepseek import ChatDeepSeek


# import the .env file
from dotenv import load_dotenv
load_dotenv()

# configuration
DATA_PATH = r"data"
CHROMA_PATH = r"chroma_db"

embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")

# initiate the model
# llm = ChatOpenAI(temperature=0.5, model='gpt-3.5-turbo')
llm = ChatDeepSeek(
    model="deepseek-llm",
    api_base="http://172.27.240.1:11434/v1", verbose=True, temperature=0.1
)
# connect to the chromadb
vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings_model,
    persist_directory=CHROMA_PATH, 
)

# Set up the vectorstore to be the retriever
retriever = vector_store.as_retriever(search_kwargs={'k': 3})

def stream_response(message, history):
    
    # Retrieve the relevant chunks based on the question asked
    docs = retriever.invoke(message)

    knowledge = ""
    for doc in docs:
        knowledge += doc.page_content.strip() + "\n\n"

    knowledge += "End of knowledge."


    rag_prompt = f"""
    You are an AI assistant for Aquasprint Swimming Academy. You answer questions solely based on the provided information.
    Do not make assumptions, and do not use information beyond what has been provided.
    If the information required to answer the question is not present, you must say: "Sorry, I don't have that information."

    Question: {message}

    Conversation history: {history}

    Knowledge base: {knowledge}
    """


    # Stream the response (more detailed answers for complex queries)
    partial_message = ""
    for response in llm.stream(rag_prompt):
        partial_message += response.content
        yield partial_message



# initiate the Gradio app
chatbot = gr.ChatInterface(stream_response, textbox=gr.Textbox(placeholder="Send to the LLM...",
    container=False,
    autoscroll=True,
    scale=7),
)

# launch the Gradio app
chatbot.launch(share=True)