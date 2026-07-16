from functools import lru_cache

from openai import AsyncOpenAI


@lru_cache(maxsize=1)
def get_async_client() -> AsyncOpenAI:
    """Return a shared AsyncOpenAI client. Picks up OPENAI_API_KEY from env.

    `load_dotenv()` is called in `app.main` lifespan before this is ever
    invoked, so the env var is guaranteed to be present.
    """
    return AsyncOpenAI()