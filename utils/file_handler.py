import pandas as pd

df = pd.read_csv("data/support_issues/support_issues.csv")

rows = df.to_dict(orient="records")

for row in rows:
    issue = str(row.get("Issue") or row.get("issue")).strip()
    company = str(row.get("Company") or row.get("company")).strip()