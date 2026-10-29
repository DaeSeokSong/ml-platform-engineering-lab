from pathlib import Path
import runpy
import numpy as np
import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature

state = runpy.run_path("track_tree.py")
model = state["model"]
run_id = state["run_id"]
X_valid = state["X_valid"]

with mlflow.start_run(run_id=run_id):
    info = mlflow.sklearn.log_model(
        sk_model=model,
        name="income-classifier",
        signature=infer_signature(X_valid, model.predict(X_valid)),
        input_example=X_valid.head(3),
    )
    mlflow.log_artifact("save_reload_model.py", artifact_path="code")

loaded = mlflow.sklearn.load_model(info.model_uri)

before = model.predict_proba(X_valid)
after = loaded.predict_proba(X_valid)

np.testing.assert_array_equal(
    model.predict(X_valid), loaded.predict(X_valid)
)
np.testing.assert_allclose(before, after)

Path("latest_model_uri.txt").write_text(info.model_uri + "\n")

print("\n모델 URI:", info.model_uri)
print("비교한 검증 데이터:", len(X_valid))
print("저장 전후 예측 일치: 성공")
print("최대 확률 차이:", float(np.max(np.abs(before - after))))
