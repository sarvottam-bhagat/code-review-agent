from celery import Celery
from .agent import CodeReviewAgent
from .config import Settings
import logging
import traceback

settings = Settings()
celery_app = Celery('code_review',
                    broker=settings.CELERY_BROKER_URL,
                    backend=settings.CELERY_RESULT_BACKEND)

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def analyze_pr_task(self, repo_url: str, pr_number: int, github_token: str | None = None):
    try:
        logger.info(f"Starting PR analysis for {repo_url} PR #{pr_number}")
        agent = CodeReviewAgent(settings.GOOGLE_API_KEY)
        result = agent.analyze_pr(repo_url, pr_number, github_token)
        logger.info("PR analysis completed successfully")
        return result
    except Exception as e:
        error_msg = f"Error analyzing PR: {str(e)}\nTraceback: {traceback.format_exc()}"
        logger.error(error_msg)
        raise Exception(error_msg)
