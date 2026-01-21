import nltk
from newspaper import Article
from sqlalchemy import select

from app.db import async_session
from app.models.sqlalchemy import TextSummary


async def generate_summary(summary_id: int, url: str) -> None:
    article = Article(url)
    article.download()
    article.parse()

    try:
        nltk.data.find("tokenizers/punkt_tab")
    except LookupError:
        nltk.download("punkt_tab")
    finally:
        article.nlp()

    summary = article.summary

    async with async_session() as session:
        result = await session.execute(
            select(TextSummary).filter(TextSummary.id == summary_id)
        )
        text_summary = result.scalar_one_or_none()
        if text_summary:
            text_summary.summary = summary
            await session.commit()