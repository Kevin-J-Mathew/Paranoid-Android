import os
from typing import List, Dict, Optional
from ..core.config import config


def get_jira_stories(project_key: str = None, max_results: int = 20) -> List[Dict]:
    """
    Fetch user stories from Jira using the REST API v3.
    Falls back to mock data if Jira credentials are not configured.
    """
    from .mock_data import get_mock_stories

    if not config.JIRA_SERVER or not config.JIRA_EMAIL or not config.JIRA_API_TOKEN:
        print("[Jira Client] No Jira credentials configured. Using mock data.")
        return get_mock_stories()

    try:
        from jira import JIRA
        jira = JIRA(
            server=config.JIRA_SERVER,
            basic_auth=(config.JIRA_EMAIL, config.JIRA_API_TOKEN)
        )
        key = project_key or config.JIRA_PROJECT_KEY
        jql = f'project = {key} AND issuetype in ("Story", "User Story") ORDER BY created DESC'
        issues = jira.search_issues(jql, maxResults=max_results)

        stories = []
        for issue in issues:
            stories.append({
                "id": issue.key,
                "title": issue.fields.summary,
                "description": issue.fields.description or issue.fields.summary,
                "acceptance_criteria": getattr(issue.fields, "customfield_10016", None) or "",
                "story_type": "feature",
                "priority": str(issue.fields.priority) if issue.fields.priority else "medium"
            })
        return stories

    except Exception as e:
        print(f"[Jira Client] Failed to connect to Jira: {e}. Falling back to mock data.")
        return get_mock_stories()


def get_story_by_id(story_id: str) -> Optional[Dict]:
    """Fetch a single Jira story by ID."""
    from .mock_data import get_story_by_id as mock_story

    if not config.JIRA_SERVER:
        return mock_story(story_id)

    try:
        from jira import JIRA
        jira = JIRA(
            server=config.JIRA_SERVER,
            basic_auth=(config.JIRA_EMAIL, config.JIRA_API_TOKEN)
        )
        issue = jira.issue(story_id)
        return {
            "id": issue.key,
            "title": issue.fields.summary,
            "description": issue.fields.description or issue.fields.summary,
            "acceptance_criteria": getattr(issue.fields, "customfield_10016", None) or "",
            "story_type": "feature",
            "priority": str(issue.fields.priority) if issue.fields.priority else "medium"
        }
    except Exception as e:
        print(f"[Jira Client] Failed to fetch story {story_id}: {e}")
        return mock_story(story_id)
