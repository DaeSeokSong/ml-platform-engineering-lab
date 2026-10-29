from pathlib import Path
import pandas as pd
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient

mlflow.set_tracking_uri("sqlite:///mlflow.db")

source_uri = Path("latest_model_uri.txt").read_text().strip()
name = "income-classifier-tree"

version = mlflow.register_model(source_uri, name)
client = MlflowClient()
client.set_registered_model_alias(name, "candidate", version.version)

version_uri = f"models:/{name}/{version.version}"
Path("registered_model_uri.txt").write_text(version_uri + "\n")

print("등록 이름:", name)
print("등록 버전:", version.version)
print("별칭: candidate")
print("버전 주소:", version_uri)

loaded = mlflow.sklearn.load_model(version_uri)
sample = pd.read_csv("data/income_data.csv").drop(columns="Target").head(3)

print("등록 모델 로드: 성공")
print("예측 결과:", loaded.predict(sample).tolist())
print("고소득 확률:", loaded.predict_proba(sample)[:, 1].round(4).tolist())
