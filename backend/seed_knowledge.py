"""
Seed Script: Run this ONCE before the demo to pre-populate ChromaDB
with historical test knowledge and bug reports.

Run with: python seed_knowledge.py
(from the backend/ directory)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.core.rag import get_rag_pipeline
from backend.integrations.mock_data import HISTORICAL_BUGS, MOCK_JIRA_STORIES

def seed():
    print("Seeding ChromaDB knowledge base...")
    rag = get_rag_pipeline()

    # Seed bug reports
    for bug in HISTORICAL_BUGS:
        rag.add_bug_report(
            bug_id=bug["id"],
            title=bug["title"],
            description=bug["description"],
            affected_area=bug["affected_area"],
            severity=bug["severity"]
        )
    print(f"  ✓ Seeded {len(HISTORICAL_BUGS)} historical bug reports")

    # Seed some historical test cases (simulating past runs)
    historical_tests = [
        {
            "story_id": "HIST-001",
            "story_text": "User wants to add a todo item to track tasks",
            "test_code": """
def test_add_todo_basic():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://demo.playwright.dev/todomvc")
        page.locator(".new-todo").fill("Buy groceries")
        page.locator(".new-todo").press("Enter")
        expect(page.locator(".todo-list li")).to_have_count(1)
        browser.close()""",
            "test_name": "test_add_todo_basic",
            "outcome": "passed"
        },
        {
            "story_id": "HIST-001",
            "story_text": "User wants to add a todo item to track tasks",
            "test_code": """
def test_add_empty_todo():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://demo.playwright.dev/todomvc")
        page.locator(".new-todo").press("Enter")
        expect(page.locator(".todo-list li")).to_have_count(0)
        browser.close()""",
            "test_name": "test_add_empty_todo_rejected",
            "outcome": "passed"
        },
        {
            "story_id": "HIST-002",
            "story_text": "User wants to complete a todo item",
            "test_code": """
def test_complete_todo():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://demo.playwright.dev/todomvc")
        page.locator(".new-todo").fill("Test item")
        page.locator(".new-todo").press("Enter")
        page.locator(".todo-list li .toggle").click()
        expect(page.locator(".todo-list li")).to_have_class("completed")
        browser.close()""",
            "test_name": "test_complete_todo",
            "outcome": "passed"
        },
        {
            "story_id": "HIST-003",
            "story_text": "User wants to filter active and completed todos",
            "test_code": """
def test_filter_todos():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://demo.playwright.dev/todomvc")
        page.locator(".new-todo").fill("Task 1")
        page.locator(".new-todo").press("Enter")
        page.locator(".filters a", has_text="Active").click()
        expect(page.locator(".todo-list li")).to_have_count(1)
        browser.close()""",
            "test_name": "test_filter_active_todos",
            "outcome": "passed"
        },
        {
            "story_id": "HIST-003",
            "story_text": "User wants to delete a todo item",
            "test_code": "...",
            "test_name": "test_delete_todo_on_hover",
            "outcome": "failed"
        }
    ]

    for test in historical_tests:
        rag.add_test_case(
            story_id=test["story_id"],
            story_text=test["story_text"],
            test_code=test["test_code"],
            test_name=test["test_name"],
            outcome=test["outcome"]
        )
        rag.add_run_baseline(
            story_id=test["story_id"],
            test_name=test["test_name"],
            pass_rate=1.0 if test["outcome"] == "passed" else 0.0,
            avg_duration_ms=1200.0
        )

    print(f"  ✓ Seeded {len(historical_tests)} historical test cases")

    stats = rag.get_collection_stats()
    print(f"\n✅ Knowledge base seeded successfully!")
    print(f"   Test cases: {stats['test_cases']}")
    print(f"   Bug reports: {stats['bug_reports']}")
    print(f"   Run baselines: {stats['run_baselines']}")


if __name__ == "__main__":
    seed()
