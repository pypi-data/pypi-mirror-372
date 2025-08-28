"""Main module."""
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.retrievers.arxiv import ArxivRetriever
import requests
from pprint import pprint

# Clase utilizada para realizar una búsqueda de Arxiv
class LangchainArxiv:
    # Builder
    def __init__(self, llm):
        self.retriever = ArxivRetriever(
            load_max_docs=2,
            get_full_documents=True,
            load_all_available_meta=True
        )
        self.llm = llm

    # Hacer query en Arxiv
    def query_arxiv(self, query):
        retrieved_docs = self.retriever.invoke(query)
        return retrieved_docs

    # Descargar artículos obtenidos y guardarlos en un .zip
    def download_docs(self, docs):
        for doc in docs:
            arxiv_url = doc.metadata["Entry ID"]
            try:
                pdf_url = arxiv_url.replace("/abs/", "/pdf")
                filename = f"{pdf_url.split("/")[-1]}.pdf"
            except:
                print(f"Error: pdf with url {pdf_url} not found")
            try:
                response = requests.get(pdf_url, stream=True)
                response.raise_for_status()
                with open(filename, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Successfully downloaded {filename}")
            except requests.exceptions.RequestException as e:
                print(f"Error: Error during download {e}")

    def run(self, query):
        docs = self.query_arxiv(query)
        download_flag = self.download_docs(docs)

if __name__ == "__main__":
    from dotenv import load_dotenv, dotenv_values
    load_dotenv()
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2
    )
    arxiv_tool = LangchainArxiv(llm=llm)
    query = "Transformer architecture for LLMs"
    docs = arxiv_tool.query_arxiv(query)
    pprint(docs[0].metadata.keys())
    for doc in docs:
        pprint(doc.metadata["entry_id"])


