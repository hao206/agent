"""
LLM Factory Module for Local Qwen2.5 & Provider Management.
Khởi tạo LLM Chat Models cho hệ thống Construction AI Foundation.
"""
import os
import logging
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
from langchain_core.language_models import BaseChatModel

logger = logging.getLogger(__name__)


def get_local_qwen() -> BaseChatModel:
    """
    Khởi tạo Qwen2.5 Local qua Ollama.
    - temperature=0.1: Giữ tính Deterministic cho dự toán BOQ & reasoning.
    - format="json": Ép Qwen2.5 trả về JSON mode native, tránh text trác.
    - num_ctx=32768: Đủ dài cho context TCVN & BOQ takeoff.
    """
    model_name = os.getenv("LOCAL_MODEL", "qwen2.5:32b-instruct-q4_K_M")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    try:
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=model_name,
            temperature=0.1,
            num_ctx=32768,
            format="json",
            base_url=base_url,
        )
    except ImportError:
        logger.warning(
            "langchain-ollama module not found. Falling back to ChatOpenAI baseline."
        )
        from langchain_openai import ChatOpenAI

        api_key = os.getenv("OPENAI_API_KEY", "dummy-api-key-for-init")
        return ChatOpenAI(model="gpt-4o-mini", temperature=0.1, api_key=api_key)
