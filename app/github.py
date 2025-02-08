import requests
from typing import Dict, Optional, List
import base64
import logging

logger = logging.getLogger(__name__)

class GitHubClient:
    def __init__(self):
        self.base_url = "https://api.github.com"
    
    def _get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        else:
            logger.warning("No GitHub token provided. API rate limits will be restricted.")
        return headers

    def _parse_repo_url(self, repo_url: str) -> tuple[str, str]:
        # Remove .git if present
        repo_url = repo_url.rstrip(".git")
        # Split by github.com/
        parts = repo_url.split("github.com/")[-1].split("/")
        if len(parts) < 2:
            raise ValueError(f"Invalid GitHub repository URL: {repo_url}")
        return parts[0], parts[1]
    
    def get_pr_details(
        self, 
        repo_url: str, 
        pr_number: int, 
        token: Optional[str] = None
    ) -> Dict:
        try:
            headers = self._get_headers(token)
            owner, repo = self._parse_repo_url(repo_url)
            
            response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if response.status_code == 401:
                raise Exception("GitHub API authentication failed. Please provide a valid GitHub token.") from e
            elif response.status_code == 404:
                raise Exception(f"Pull request #{pr_number} not found in repository {repo_url}") from e
            else:
                raise Exception(f"GitHub API error: {str(e)}") from e
    
    def get_pr_files(
        self, 
        repo_url: str, 
        pr_number: int, 
        token: Optional[str] = None
    ) -> List[Dict]:
        try:
            headers = self._get_headers(token)
            owner, repo = self._parse_repo_url(repo_url)
            
            response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if response.status_code == 401:
                raise Exception("GitHub API authentication failed. Please provide a valid GitHub token.") from e
            elif response.status_code == 404:
                raise Exception(f"Pull request #{pr_number} not found in repository {repo_url}") from e
            else:
                raise Exception(f"GitHub API error: {str(e)}") from e

    def get_file_content(
        self, 
        repo_url: str, 
        file_path: str, 
        commit_sha: str,
        token: Optional[str] = None
    ) -> str:
        try:
            headers = self._get_headers(token)
            owner, repo = self._parse_repo_url(repo_url)
            
            response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/contents/{file_path}?ref={commit_sha}",
                headers=headers
            )
            response.raise_for_status()
            
            content = response.json()
            if "content" in content:
                return base64.b64decode(content["content"]).decode('utf-8')
            return ""
        except requests.exceptions.RequestException as e:
            if response.status_code == 401:
                raise Exception("GitHub API authentication failed. Please provide a valid GitHub token.") from e
            elif response.status_code == 404:
                raise Exception(f"File {file_path} not found in repository {repo_url} at commit {commit_sha}") from e
            else:
                raise Exception(f"GitHub API error: {str(e)}") from e