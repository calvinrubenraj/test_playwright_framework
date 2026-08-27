import re
import time
from datetime import datetime
from typing import Any, Generator
from pages.login_page import LoginPage
import subprocess

import pytest
from utils.config import Settings, load_settings
from utils.slack_notifier import send_slack_message
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright
from pathlib import Path

ARTIFACT_ROOT = Path("artifacts")
TRACE_DIR = ARTIFACT_ROOT / "traces"
SCREENSHOT_DIR = ARTIFACT_ROOT / "screenshots"
AUTH_DIR = ARTIFACT_ROOT / "auth"

def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="qa")
    parser.addoption("--browser-name", action="store", default="chromium", choices=["chromium", "firefox", "webkit"])
    parser.addoption("--show_browser", action="store_true", default=False)
    parser.addoption("--skip-optional", action="store_true", default=False)
    parser.addoption(
        "--open-allure",
        action="store_true",
        default=False,
        help="Generate and open Allure report after execution."
    )
    parser.addoption("--no-login", action="store_true", default=False)


def pytest_configure(config):
    config._qa_run_start = time.time()
    config._qa_stats = {"passed": 0, "failed": 0, "skipped": 0}

def pytest_collection_modifyitems(config, items):
    if config.getoption("--skip-optional"):
        skip_marker = pytest.mark.skip(reason="Skipped by --skip-optional")
        for item in items:
            if "optional_skip" in item.keywords:
                item.add_marker(skip_marker)

@pytest.fixture(scope="session")
def environment(pytestconfig) -> str:
    return pytestconfig.getoption("--env")


@pytest.fixture(scope="session")
def settings(environment: str) -> Settings:
    return load_settings(environment)

@pytest.fixture(scope="session")
def playwright_instance() -> Generator[Playwright, Any, None]:
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright, pytestconfig) -> Generator[Browser, Any, None]:
    browser_name = pytestconfig.getoption("--browser-name")
    headed = pytestconfig.getoption("--show_browser")
    browser_type = getattr(playwright_instance, browser_name)
    browser = browser_type.launch(headless= not headed, args=["--disable-gpu", "--disable-software-rasterizer"])
    yield browser
    browser.close()

@pytest.fixture(scope="session")
def auth_state(browser: Browser, settings: Settings,pytestconfig) -> str | None:
    state_dir = AUTH_DIR / settings.environment
    state_dir.mkdir(parents=True, exist_ok=True)
    state_file = state_dir / "storage_state.json"
    no_login = pytestconfig.getoption("--no-login")

    if no_login:
        if state_file.exists():
            state_file.unlink(missing_ok=True)
            #return str(state_file)

        context = browser.new_context(base_url=settings.base_url)
        page = context.new_page()
        login = LoginPage(page)
        login.open()
        login.login(settings.username, settings.password)
        page.wait_for_load_state("networkidle")
        context.storage_state(path=str(state_file))
        context.close()
        return str(state_file)
    return None


@pytest.fixture
def context(browser: Browser, auth_state: str, settings: Settings, request) -> Generator[BrowserContext, Any, None]:
    if auth_state is None:
        context = browser.new_context(
            base_url=settings.base_url,
            storage_state=auth_state,
        )
    else:
        context = browser.new_context(
            base_url=settings.base_url,
        )
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield context

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", request.node.nodeid)
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    context.tracing.stop(path=str(TRACE_DIR / f"{safe_name}_{timestamp}.zip"))
    context.close()

@pytest.fixture
def page(context: BrowserContext) -> Generator[Page, Any, None]:
    page = context.new_page()
    yield page

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)

    if report.when == "call":
        stats = item.config._qa_stats
        if report.passed:
            stats["passed"] += 1
        elif report.failed:
            stats["failed"] += 1
        elif report.skipped:
            stats["skipped"] += 1

        if report.failed:
            page = item.funcargs.get("page")
            if page:
                folder = SCREENSHOT_DIR / datetime.now().strftime("%Y-%m-%d")
                folder.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now().strftime("%H%M%S_%f")
                safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", item.nodeid)
                screenshot = folder / f"{safe_name}_{timestamp}.png"
                page.screenshot(path=str(screenshot), full_page=True)
                try:
                    import allure
                    allure.attach.file(str(screenshot), name="Failure Screenshot", attachment_type=allure.attachment_type.PNG)
                except Exception:
                    pass


def pytest_sessionfinish(session, exitstatus):
    stats = session.config._qa_stats
    duration = time.time() - session.config._qa_run_start
    env = session.config.getoption("--env")
    total = stats["passed"] + stats["failed"] + stats["skipped"]
    message = (
        "*Playwright Pytest Automation Result*\n"
        f"Environment: `{env}`\n"
        f"Total: *{total}*\n"
        f"Passed: *{stats['passed']}*\n"
        f"Failed: *{stats['failed']}*\n"
        f"Skipped: *{stats['skipped']}*\n"
        f"Duration: *{duration:.2f}s*\n"
        f"Exit status: *{exitstatus}*"
    )
    # ----------------------
    # slack notification
    #-----------------------
    try:
        cfg = load_settings(env)
        send_slack_message(cfg.slack_webhook_url, message)
    except Exception as exc:
        print(f"Slack notification failed: {exc}")

    # -------------------------
    # Generate Allure Report
    # -------------------------

    if session.config.getoption("--open-allure"):

        print("\nGenerating Allure Report...")

        try:

            subprocess.run(
                [
                    "allure",
                    "generate",
                    "allure-results",
                    "-o",
                    "allure-report",
                    "--clean"
                ],
                check=True
            )

            print(
                "Allure report generated successfully."
            )

            # Open report in browser
            subprocess.Popen(
                [
                    "allure",
                    "open",
                    "allure-report"
                ]
            )

        except FileNotFoundError:

            print(
                "Allure command not found. "
                "Install Allure CLI and add it to PATH."
            )

        except subprocess.CalledProcessError as exc:

            print(
                f"Allure report generation failed: {exc}"
            )