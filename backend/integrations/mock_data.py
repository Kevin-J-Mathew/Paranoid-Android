from typing import List, Dict

MOCK_JIRA_STORIES = [
    {
        "id": "DEMO-001",
        "title": "Add Todo Item Feature",
        "description": (
            "As a user, I want to add a new todo item by typing in the input field and pressing Enter, "
            "so that I can track my tasks. The input should be cleared after adding. "
            "The new item should appear in the list immediately."
        ),
        "acceptance_criteria": (
            "GIVEN I am on the todo app\n"
            "WHEN I type a task and press Enter\n"
            "THEN the task appears in the todo list AND the input field is cleared\n"
            "AND the todo count increases by 1"
        ),
        "story_type": "feature",
        "priority": "high"
    },
    {
        "id": "DEMO-002",
        "title": "Complete and Filter Todo Items",
        "description": (
            "As a user, I want to mark todo items as complete by clicking their checkbox, "
            "and filter the list to show All/Active/Completed items, "
            "so I can manage my task completion workflow."
        ),
        "acceptance_criteria": (
            "GIVEN there are todos in the list\n"
            "WHEN I click a todo's checkbox\n"
            "THEN it is marked as completed with strikethrough text\n"
            "AND I can filter to see only Active or Completed todos\n"
            "AND the count of active items updates correctly"
        ),
        "story_type": "feature",
        "priority": "high"
    },
    {
        "id": "DEMO-003",
        "title": "Delete and Clear Completed Todos",
        "description": (
            "As a user, I want to delete individual todo items by hovering over them and clicking the X button, "
            "and also bulk-clear all completed todos using the 'Clear completed' button."
        ),
        "acceptance_criteria": (
            "GIVEN I have todos in the list\n"
            "WHEN I hover over a todo and click the X button\n"
            "THEN the todo is removed from the list\n"
            "WHEN I click 'Clear completed'\n"
            "THEN all completed todos are removed at once"
        ),
        "story_type": "feature",
        "priority": "medium"
    },
    {
        "id": "DEMO-004",
        "title": "Edit Todo Items Inline",
        "description": (
            "As a user, I want to edit an existing todo item by double-clicking on it, "
            "so I can correct typos or update task descriptions without deleting and re-adding."
        ),
        "acceptance_criteria": (
            "GIVEN a todo exists in the list\n"
            "WHEN I double-click on the todo text\n"
            "THEN an edit input appears with the current text\n"
            "WHEN I change the text and press Enter\n"
            "THEN the todo is updated with the new text\n"
            "WHEN I press Escape\n"
            "THEN changes are discarded"
        ),
        "story_type": "feature",
        "priority": "medium"
    },
    {
        "id": "DEMO-005",
        "title": "Handle Empty Input and Duplicate Todos",
        "description": (
            "As a system, I need to handle edge cases in todo creation: "
            "empty input should not create a todo, whitespace-only input should be rejected, "
            "and very long todo text should be handled gracefully."
        ),
        "acceptance_criteria": (
            "GIVEN the todo input is empty\n"
            "WHEN I press Enter\n"
            "THEN no new todo is created\n"
            "GIVEN the input contains only spaces\n"
            "WHEN I press Enter\n"
            "THEN no new todo is created"
        ),
        "story_type": "regression",
        "priority": "high"
    }
]

HISTORICAL_BUGS = [
    {
        "id": "BUG-101",
        "title": "Todo not added when Enter pressed rapidly twice",
        "description": "When user presses Enter twice quickly, duplicate todos are created",
        "affected_area": "todo_creation",
        "severity": "medium"
    },
    {
        "id": "BUG-102", 
        "title": "Filter state resets on page refresh",
        "description": "When user is on 'Active' filter view and refreshes, filter returns to 'All'",
        "affected_area": "filtering",
        "severity": "low"
    },
    {
        "id": "BUG-103",
        "title": "Checkbox not responding on mobile viewport",
        "description": "On small screen sizes, the todo completion checkbox click area is too small",
        "affected_area": "todo_completion",
        "severity": "high"
    },
    {
        "id": "BUG-104",
        "title": "Edit mode not exiting on focus loss",
        "description": "When editing a todo and clicking outside, the edit mode stays active",
        "affected_area": "todo_editing",
        "severity": "medium"
    },
    {
        "id": "BUG-105",
        "title": "Clear completed button visible with no completed items",
        "description": "The 'Clear completed' button sometimes shows even when there are no completed todos",
        "affected_area": "ui_state",
        "severity": "low"
    }
]


def get_mock_stories() -> List[Dict]:
    return MOCK_JIRA_STORIES


def get_story_by_id(story_id: str) -> Dict:
    for story in MOCK_JIRA_STORIES:
        if story["id"] == story_id:
            return story
    return None


def get_historical_bugs() -> List[Dict]:
    return HISTORICAL_BUGS
