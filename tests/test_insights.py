def add(client, amount, category="food", merchant="Swiggy", date="2026-10-03"):
    client.post(
        "/transactions",
        json={
            "amount": amount,
            "merchant": merchant,
            "category": category,
            "date": date,
        },
    )


def test_monthly_summary(client):
    add(client, 100, "food", "Swiggy")
    add(client, 50, "food", "Zomato")
    add(client, 200, "bills", "Airtel")
    add(client, 999, "food", "Swiggy", date="2026-09-15")  # different month

    body = client.get("/insights/summary", params={"month": "2026-10"}).json()
    assert body["total_spend"] == 350
    assert body["by_category"] == {"food": 150, "bills": 200}
    assert body["top_merchants"][0]["merchant"] == "Airtel"


def test_summary_rejects_bad_month(client):
    r = client.get("/insights/summary", params={"month": "October"})
    assert r.status_code == 422


def test_anomaly_detected(client):
    for _ in range(9):
        add(client, 100)
    add(client, 1000, merchant="Fancy Store")

    flagged = client.get("/insights/anomalies").json()
    assert len(flagged) == 1
    assert flagged[0]["merchant"] == "Fancy Store"


def test_no_anomalies_with_too_little_data(client):
    for amount in [100, 100, 1000]:
        add(client, amount)
    assert client.get("/insights/anomalies").json() == []