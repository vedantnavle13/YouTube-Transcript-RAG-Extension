import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from backend.app.config import GEMINI_API_KEY

# Determine absolute path to the local data directory
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))

class RAGEngine:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is not set in backend/.env. "
                "Please configure it to proceed."
            )
        
        # Use the stable embedding model from the notebook
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=GEMINI_API_KEY
        )
        
        # Use the gemini-2.5-flash model from the notebook
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=GEMINI_API_KEY
        )

    def _get_index_path(self, video_id: str) -> str:
        return os.path.join(DATA_DIR, video_id)

    def index_exists(self, video_id: str) -> bool:
        index_path = self._get_index_path(video_id)
        return os.path.exists(os.path.join(index_path, "index.faiss"))

    def create_index(self, video_id: str, transcript_text: str):
        # Splitter settings
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        docs = text_splitter.create_documents([transcript_text])
        
        # Build local FAISS index
        vector_store = FAISS.from_documents(docs, self.embeddings)
        
        # Save FAISS index locally
        index_path = self._get_index_path(video_id)
        os.makedirs(index_path, exist_ok=True)
        vector_store.save_local(index_path)

    def query(self, video_id: str, question: str) -> str:
        index_path = self._get_index_path(video_id)
        if not self.index_exists(video_id):
            raise Exception("Vector index does not exist for this video. Please index it first.")
        
        # Load local FAISS index
        vector_store = FAISS.load_local(
            index_path, 
            self.embeddings, 
            allow_dangerous_deserialization=True
        )
        
        # Setup retriever exactly as defined in the notebook (k=3)
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )
        
        # Setup prompt from the notebook
        prompt = PromptTemplate(
            template="""
      You are a helpful assistant.
      Answer ONLY from the provided transcript context.
      If the context is insufficient, just say you don't know.

      {context}
      Question: {question}
    """,
            input_variables=['context', 'question']
        )
        
        # Helper to format documents into a single block of context
        def format_docs(retrieved_docs):
            return "\n\n".join(doc.page_content for doc in retrieved_docs)
        
        # Build LCEL chain from the notebook
        parallel_chain = RunnableParallel({
            'context': retriever | RunnableLambda(format_docs),
            'question': RunnablePassthrough()
        })
        
        parser = StrOutputParser()
        main_chain = parallel_chain | prompt | self.llm | parser
        
        # Invoke the chain
        response = main_chain.invoke(question)
        return response
