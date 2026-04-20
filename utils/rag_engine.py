import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

class RAGAgent:
    def __init__(self, model_name="llama-3.3-70b-versatile"):
        self.llm = ChatGroq(
            temperature=0,
            model_name=model_name,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.persist_directory = os.getenv("CHROMA_DB_PATH", "chroma_db")

    def process_file(self, file_path):
        if file_path.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        elif file_path.endswith('.docx'):
            loader = UnstructuredWordDocumentLoader(file_path)
        else:
            loader = TextLoader(file_path)
            
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)
        
        vectorstore = Chroma.from_documents(
            documents=texts, 
            embedding=self.embeddings, 
            persist_directory=self.persist_directory
        )
        # Chroma in recent versions persists automatically, but we can call persist() if needed in older ones
        # vectorstore.persist()
        return vectorstore

    def ask_question(self, query, vectorstore):
        # Manual RAG implementation
        docs = vectorstore.similarity_search(query, k=4)
        context = "\n\n".join([doc.page_content for doc in docs])
        
        prompt = f"""
        You are an AI Tutor. Use the provided study notes (Context) to answer the student's question.
        If the answer is not in the context, say that you don't know based on the provided notes, but try to answer from your general knowledge if relevant.
        
        Context:
        {context}
        
        Question:
        {query}
        
        Answer:
        """
        response = self.llm.invoke(prompt)
        return response.content
