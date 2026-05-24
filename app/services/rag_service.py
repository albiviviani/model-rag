"""RAG orchestration for question answering using retrieval and an LLM."""

from langchain_ollama import ChatOllama
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_core.prompts import PromptTemplate

from app.services.settings import Settings


class RAGService:
    """Wrap RAG chain construction and question answering logic."""

    def __init__(self, settings: Settings, retriever) -> None:
        self.settings = settings
        self.retriever = retriever
        self.llm = ChatOllama(model=settings.llm_model, temperature=0)
        self.prompt = PromptTemplate.from_template(settings.prompt_template)
        self.chain = self._build_chain()

    def _build_chain(self):
        """Build the retrieval-augmented generation chain for answering queries."""
        combine_chain = create_stuff_documents_chain(self.llm, self.prompt)
        return create_retrieval_chain(self.retriever, combine_chain)

    def answer_question(self, question: str) -> str:
        """Answer a user question using the RAG chain and return the generated text."""
        if not question or not question.strip():
            raise ValueError("A non-empty question is required.")

        result = self.chain.invoke({"input": question})
        answer = result.get("answer") or result.get("output_text")
        if not answer:
            answer = str(result)

        return answer.strip()
