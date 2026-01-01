from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core.exceptions import ResourceExhausted, InternalServerError
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError
import time

# Custom retry strategy
def log_retry(retry_state):
    print(f"Rate limit hit. Retrying in {retry_state.next_action.sleep} seconds...")

@retry(
    retry=retry_if_exception_type((ResourceExhausted, InternalServerError, ChatGoogleGenerativeAIError)),
    stop=stop_after_attempt(10), # Try more times for free tier
    wait=wait_exponential(multiplier=5, min=10, max=120), # Robust wait time
    before_sleep=log_retry
)
def invoke_with_retry(llm, prompt, **kwargs):
    """
    Invokes the LLM with robust retry logic for 429 errors.
    """
    return llm.invoke(prompt, **kwargs)
