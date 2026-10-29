from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

out = Path("artifacts/eda")
out.mkdir(parents=True, exist_ok=True)

df = pd.read_csv("data/income_data.csv")
df = df.apply(lambda column: column.str.strip())

print("결측값 수:", int(df.isna().sum().sum()))
print("'?' 값 수:", int(df.eq("?").sum().sum()))
print("동일한 행 수:", int(df.duplicated().sum()))

counts = pd.crosstab(df["Education"], df["Target"])
counts = counts.reindex(columns=["<=50K", ">50K"], fill_value=0)
counts = counts.sort_index()
ratios = counts.div(counts.sum(axis=1), axis=0)

counts.to_csv(out / "education_counts.csv")
ratios.to_csv(out / "education_ratios.csv")

fig, axes = plt.subplots(1, 2, figsize=(16, 6))
counts.plot.bar(stacked=True, ax=axes[0], color=["#8b5cf6", "#f97316"])
ratios.plot.bar(stacked=True, ax=axes[1], color=["#8b5cf6", "#f97316"])

axes[0].set(title="Income counts by education", ylabel="People")
axes[1].set(title="Income proportions by education", ylabel="Proportion")
fig.tight_layout()
fig.savefig(out / "education_income.png", dpi=150)
plt.close(fig)

print("\n학력별 소득 건수:")
print(counts.to_string())
print("\n저장 위치:", out / "education_income.png")
