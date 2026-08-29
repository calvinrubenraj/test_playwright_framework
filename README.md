# RR - QA - Automation Assignment

# Test plan Test case Document
filename: `RR – QA - Automation Assignment.pdf`

# Test report
- Unzip `rr-allure-report.zip`
- Open `index.html` in browser`

## Test Result status
|Test ID|        Test Name        | Status |
| :--- |:-----------------------:|-------:|
|001| Verify Popular Category |   Pass |
|002|Verify Trending Category |   Pass |
|003| Verify Newest Category  |   Fail |
|004|Verify Top rated Category|   Pass |
|005|Search/Filter Using Valid Title|   Pass |
|006|Search/Filter Using Invalid Title|   Pass |
|007|Filter Movies Types|   Pass |
|008|Filter TV ShowsTypes|   Pass |
|009|Filter by Valid Year range|   Fail |
|010|Filter by Rating|   Pass |
|011|Filter by Genre|   Pass |
|012|Combination of Multiple Filters|   Fail |
|013|Verify First Section pagination Functionality|   Pass |
|014|Verify Last Section pagination Functionality|   Fail |
|015|Verify Middle Section pagination Functionality|   Pass |
|016|Verify Previous and Next button page Functionality|   Pass |
|017|Direct Navigation to All Category|   Fail |

- Total 17 test cases
- Total 12 test cases pass
- Total 5 test cases fail (2 Known issues)

## Prerequisite to be installed
- Python 3.8+
- pip
- Playwright
- allure

## Installation
```bash
pip install -r requirements.txt
```
## Setup
create file `.env.rr`
copy below content in file
```text
BASE_URL=https://tmdb-discover.surge.sh/
API_BASE_URL=https://api.example.test
USERNAME=test
PASSWORD=test
SLACK_WEBHOOK_URL=
```
## Run the framework
```bash
pytest --env=rr --show_browser --open-allure
```


# Playwright + Pytest Framework For UI and API automation

This framework demonstrates a scalable UI + API automation architecture

## Key design

- Session-scoped browser fixture
- Function-scoped browser context for isolation
- Session-scoped authenticated `storage_state`
- Environment selection with `--env=qa|stage`
- UI and API layers separated
- Parallel runs using `pytest-xdist`
- Smoke/regression/optional-skip markers
- Timestamped Playwright traces
- Failure-only screenshots organized by date
- Allure reporting
- Slack execution summary
- Jenkins pipeline for CI/CD

## Structure

```text
api/                 API client layer
pages/               Page Object Model
utils/               Configuration and Slack utilities
tests/ui/            UI tests
tests/api/           API tests
conftest.py          Fixtures + pytest hooks
pytest.ini           Markers and default pytest settings
.env.qa              QA environment example
Jenkinsfile          Linux Jenkins pipeline
Jenkinsfile.windows  Windows Jenkins pipeline
```

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

Windows activation:

```bat
.venv\Scripts\activate
```

## Commands

QA environment:

```bash
pytest --env=qa
```

Smoke suite:

```bash
pytest --env=qa -m smoke
```

Regression suite:

```bash
pytest --env=stage -m regression
```

Parallel execution:

```bash
pytest --env=qa -n auto
```

Skip selected optional tests:

note: test add marker `optional_skip`

```bash
pytest --env=qa --skip-optional
```

Run UI only:

```bash
pytest tests/ui --env=qa
```

Run API only:

```bash
pytest tests/api --env=qa
```

Show the running test in browser:

```bash
pytest --env=qa --show_browser
```

Generate Allure report and open allure report:

```bash
 pytest --env=qa --show_browser --open-allure
```

## Environment management

`.env.qa` example:

```dotenv
BASE_URL=https://example.test
API_BASE_URL=https://api.example.test
USERNAME=qa_user
PASSWORD=qa_password
SLACK_WEBHOOK_URL=
```

Never commit real secrets. In a production Jenkins setup, credentials should normally come from Jenkins Credentials and be injected at runtime rather than stored in Git.

## Authentication design

The `auth_state` fixture logs in once per pytest session and stores:

```text
artifacts/auth/<environment>/storage_state.json
```

Each UI test gets a fresh BrowserContext initialized from the saved state. This gives isolation without paying the cost of logging in for every test.

# Explination of framework feature

## Use of storge_state so the authentication single time
Browser launch is expensive, so the browser fixture is session scoped. BrowserContext is lightweight and provides cookie/local-storage isolation, so it is function scoped. Authentication state is session scoped and reused by contexts.

## API Testing context isolation
API testing uses Playwright `APIRequestContext`, keeping API automation inside the same Playwright stack while separating API client classes from test assertions.

## Skip test feature

Pytest markers support business-focused suites such as smoke and regression. `optional_skip` plus `--skip-optional` demonstrates dynamic execution control.

## Logging using tracing playwright
`pytest_runtest_makereport` captures failure screenshots because it has access to the final test outcome. Tracing is started per context and stored as a timestamped ZIP so failures can be debugged with Playwright Trace Viewer.

## Reporting feature(Allure and Slack notification using webhook)
Allure gives step-level reporting and attachments. Slack is handled from `pytest_sessionfinish`, so the team receives a concise execution summary after the run.

## CI/CD using Jenkins(just concept)
Jenkins exposes environment, suite, browser, and optional-skip behavior as pipeline parameters and archives reports/debug artifacts after execution.

## Important parallel-execution note

For a production-grade `xdist` setup, avoid multiple workers trying to generate the same auth file simultaneously. Recommended patterns are:

1. Generate storage state in a dedicated setup stage before invoking parallel pytest workers, or
2. Create one auth-state file per worker/account when tests modify user/session state.

The included framework demonstrates shared state reuse. For heavily parallel enterprise suites, move auth generation into a pre-test setup job or use worker-specific accounts.
