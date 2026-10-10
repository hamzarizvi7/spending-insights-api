# Spending Insights API: Spec v0.1

## User stories
- As a cardholder, I want to record my transactions so I can track spending.
- As a cardholder, I want to see my spending by category each month.
- As a cardholder, I want unusual charges flagged so I can spot fraud or mistakes.

## Transaction object
| Field    | Type    | Rules                          |
|----------|---------|--------------------------------|
| id       | integer | auto-generated                 |
| amount   | float   | > 0                            |
| merchant | string  | 1-100 chars                    |
| category | string  | e.g. food, travel, bills       |
| date     | date    | ISO format, not in the future  |

## Endpoints

### POST /transactions
Request:
```json
{"amount": 42.50, "merchant": "Swiggy", "category": "food", "date": "2026-10-03"}
```
Response `201`: the transaction with its `id`.
Errors: `422` for invalid input.

### GET /transactions
Query params (all optional): `category`, `start_date`, `end_date`
Response `200`: list of transactions.

### GET /insights/summary?month=2026-10
Response `200`:
```json
{
  "month": "2026-10",
  "total_spend": 18250.00,
  "by_category": {"food": 6200.00, "bills": 9000.00, "travel": 3050.00},
  "top_merchants": [{"merchant": "Swiggy", "total": 2100.00}]
}
```

### GET /insights/anomalies
Flags transactions more than 2 standard deviations above their category's mean.
Response `200`: list of flagged transactions, each with a `reason` field.
Note: needs at least 6 transactions in a category to be evaluated.