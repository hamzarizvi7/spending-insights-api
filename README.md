# Spending Insights API

A REST API that records card-style transactions and turns them into
spending insights: monthly summaries and unusual-charge detection.
Built with Python, FastAPI, SQLAlchemy and pytest.

## Features
- Add and list transactions, with filters by category and date range
- Input validation (amount must be positive, date can't be in the future)
- Monthly summary: total spend, spend by category, top merchants
- Anomaly detection: flags charges far above a category's usual spending
- Auto-generated interactive API docs (Swagger UI)
- Automated tests with pytest

## Tech stack
Python, FastAPI, SQLAlchemy, SQLite, Pydantic, pytest

## Run it locally
```bash
git clone https://github.com/hamzarizvi7/spending-insights-api.git
cd spending-insights-api
python -m venv .venv
.venv\Scripts\activate        # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Then open http://127.0.0.1:8000/docs to try the endpoints.

## Endpoints
| Method | Path | Description |
|--------|------|-------------|
| POST | /transactions | Add a transaction |
| GET | /transactions | List transactions (filters: category, start_date, end_date) |
| GET | /insights/summary?month=2026-10 | Spend totals for a month |
| GET | /insights/anomalies | Unusually large transactions |

Full details are in [docs/api-spec.md](docs/api-spec.md).

## How anomaly detection works
For each category with at least 6 transactions, the API computes the mean
and standard deviation of the amounts. A transaction is flagged if it is
more than 2 standard deviations above its category's mean. Each flagged
item includes a plain-English reason.

## Testing
```bash
python -m pytest
```
9 tests cover validation, filtering, monthly summaries and anomaly detection.

## How I built it
I wrote the API spec first, then built each feature on its own branch
and merged it through a pull request.

- Sprint 0: project setup and API spec
- Sprint 1: transactions endpoints, validation, tests
- Sprint 2: insights endpoints and tests

## Possible next steps
- Authentication and per-user data
- Docker support
- Pagination for large transaction lists