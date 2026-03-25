import os
from typing import List, Dict, Optional, Any, cast
from ..core.config import config  # pyre-ignore[21]


def get_jira_stories(project_key: Optional[str] = None, max_results: int = 20) -> List[Dict]:
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
        server = cast(str, config.JIRA_SERVER)
        email = cast(str, config.JIRA_EMAIL)
        token = cast(str, config.JIRA_API_TOKEN)
        jira = JIRA(
            server=server,
            basic_auth=(email, token)
        )
        key = project_key or config.JIRA_PROJECT_KEY or "DEMO"
        jql = f'project = {key} AND issuetype in ("Story", "User Story") ORDER BY created DESC'
        issues = cast(List[Any], jira.search_issues(jql, maxResults=max_results))

        stories = []
        for issue in issues:
            issue_obj = cast(Any, issue)
            fields = getattr(issue_obj, "fields", None)
            stories.append({
                "id": getattr(issue_obj, "key", ""),
                "title": getattr(fields, "summary", ""),
                "description": getattr(fields, "description", None) or getattr(fields, "summary", ""),
                "acceptance_criteria": getattr(fields, "customfield_10016", None) or "",
                "story_type": "feature",
                "priority": str(getattr(fields, "priority", None)) if getattr(fields, "priority", None) else "medium"
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
        server = cast(str, config.JIRA_SERVER)
        email = cast(str, config.JIRA_EMAIL)
        token = cast(str, config.JIRA_API_TOKEN)
        jira = JIRA(
            server=server,
            basic_auth=(email, token)
        )
        issue = cast(Any, jira.issue(story_id))
        fields = getattr(issue, "fields", None)
        return {
            "id": getattr(issue, "key", ""),
            "title": getattr(fields, "summary", ""),
            "description": getattr(fields, "description", None) or getattr(fields, "summary", ""),
            "acceptance_criteria": getattr(fields, "customfield_10016", None) or "",
            "story_type": "feature",
            "priority": str(getattr(fields, "priority", None)) if getattr(fields, "priority", None) else "medium"
        }
    except Exception as e:
        print(f"[Jira Client] Failed to fetch story {story_id}: {e}")
        return mock_story(story_id)
