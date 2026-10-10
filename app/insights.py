import datetime
import statistics
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models

MIN_TRANSACTIONS = 6   # need at least this many in a category to judge
THRESHOLD = 2.0        # flag amounts this many std deviations above average


def month_range(month: str):
    year, mon = map(int, month.split("-"))
    start = datetime.date(year, mon, 1)
    end = datetime.date(year + (mon == 12), mon % 12 + 1, 1)
    return start, end  # end is exclusive


def monthly_summary(db: Session, month: str):
    start, end = month_range(month)
    rows = db.scalars(
        select(models.Transaction).where(
            models.Transaction.date >= start,
            models.Transaction.date < end,
        )
    ).all()

    by_category = defaultdict(float)
    by_merchant = defaultdict(float)
    for t in rows:
        by_category[t.category] += t.amount
        by_merchant[t.merchant] += t.amount

    top = sorted(by_merchant.items(), key=lambda x: x[1], reverse=True)[:3]
    return {
        "month": month,
        "total_spend": round(sum(by_category.values()), 2),
        "by_category": {k: round(v, 2) for k, v in by_category.items()},
        "top_merchants": [{"merchant": m, "total": round(v, 2)} for m, v in top],
    }


def find_anomalies(db: Session):
    rows = db.scalars(select(models.Transaction)).all()
    groups = defaultdict(list)
    for t in rows:
        groups[t.category].append(t)

    flagged = []
    for category, txns in groups.items():
        if len(txns) < MIN_TRANSACTIONS:
            continue
        amounts = [t.amount for t in txns]
        mean = statistics.mean(amounts)
        sd = statistics.stdev(amounts)
        if sd == 0:
            continue
        for t in txns:
            z = (t.amount - mean) / sd
            if z > THRESHOLD:
                flagged.append(
                    {
                        "id": t.id,
                        "amount": t.amount,
                        "merchant": t.merchant,
                        "category": t.category,
                        "date": t.date,
                        "reason": f"{z:.1f} standard deviations above the "
                        f"{category} average of {mean:.2f}",
                    }
                )
    return flagged