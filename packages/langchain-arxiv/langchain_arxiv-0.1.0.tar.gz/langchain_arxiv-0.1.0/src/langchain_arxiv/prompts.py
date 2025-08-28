from langchain_core.prompts import ChatPromptTemplate

arxiv_prompt = ChatPromptTemplate.from_template(
    """Answer the question based only on the context provided:
Context: {context}
Question: {question}"""
