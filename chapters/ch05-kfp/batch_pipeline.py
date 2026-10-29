from pathlib import Path
from uuid import uuid4

import kfp
from kfp import compiler, dsl, kubernetes

IMAGE = "localhost:5001/ml-platform-batch:week02-v1"

COMMON = """
import sys
import io
import pandas as pd
import boto3
from botocore.config import Config

batch_prefix = sys.argv[2]
batch_bucket = "feature-data-sets"

batch_s3 = boto3.client(
    "s3",
    endpoint_url="http://external-seaweedfs:8333",
    config=Config(
        signature_version="s3v4",
        s3={"addressing_style": "path"},
        connect_timeout=5,
        read_timeout=30,
    ),
)

def read_bytes(key):
    response = batch_s3.get_object(Bucket=batch_bucket, Key=key)
    try:
        return response["Body"].read()
    finally:
        response["Body"].close()
"""

FEAST_CODE = (
    COMMON
    + Path("check_feast_from_pod.py").read_text()
    + """
batch_s3.put_object(
    Bucket=batch_bucket,
    Key=f"{batch_prefix}/intermediate/features.csv",
    Body=result.to_csv(index=False).encode("utf-8"),
)
print("중간 피처 저장:", len(result))
"""
)

PREDICT_CODE = (
    COMMON
    + Path("check_model_from_pod.py").read_text()
    + """
table = pd.read_csv(
    io.BytesIO(read_bytes(f"{batch_prefix}/intermediate/features.csv")),
    dtype=str,
    keep_default_na=False,
)

rename = {
    column: column.split("__", 1)[1]
    for column in table.columns
    if "__" in column
}
inputs = table.rename(columns=rename)[list(model.feature_names_in_)]

predictions = model.predict(inputs)
positive_index = list(model.classes_).index(1)
probabilities = model.predict_proba(inputs)[:, positive_index]

output = table[["user_id", "event_timestamp"]].copy()
output["prediction"] = predictions
output["probability_gt_50k"] = probabilities
output["model_uri"] = manifest["source_model_uri"]

batch_s3.put_object(
    Bucket=batch_bucket,
    Key=f"{batch_prefix}/intermediate/predictions.csv",
    Body=output.to_csv(index=False).encode("utf-8"),
)

print("추론한 사용자 수:", len(output))
print(output[["prediction", "probability_gt_50k"]].to_string(index=False))
"""
)

SAVE_CODE = COMMON + """
payload = read_bytes(f"{batch_prefix}/intermediate/predictions.csv")
table = pd.read_csv(io.BytesIO(payload))

assert len(table) == 3, "예측 결과가 3행이 아닙니다."
assert table["prediction"].isin([0, 1]).all(), "예측 클래스가 잘못됐습니다."
assert table["probability_gt_50k"].between(0, 1).all(), "확률 범위가 잘못됐습니다."

final_key = f"{batch_prefix}/results/predictions.csv"

batch_s3.put_object(
    Bucket=batch_bucket,
    Key=final_key,
    Body=payload,
    ContentType="text/csv",
)

assert read_bytes(final_key) == payload, "최종 저장 결과가 다릅니다."

print("최종 결과:", f"s3://{batch_bucket}/{final_key}")
print("저장한 예측 행 수:", len(table))
print("배치 추론 결과 저장·재읽기 확인: 성공")
"""


@dsl.container_component
def run_step(code: str, prefix: str, next_prefix: dsl.OutputPath(str)):
    runner = """
import sys
from pathlib import Path

exec(sys.argv[1], globals())

output_path = Path(sys.argv[3])
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(sys.argv[2])
"""
    return dsl.ContainerSpec(
        image=IMAGE,
        command=["python"],
        args=["-c", runner, code, prefix, next_prefix],
    )


@dsl.pipeline(name="income-batch-inference")
def batch_pipeline(prefix: str):
    retrieve = run_step(code=FEAST_CODE, prefix=prefix)
    retrieve.set_display_name("1. Feast 피처 조회")

    predict = run_step(
        code=PREDICT_CODE,
        prefix=retrieve.outputs["next_prefix"],
    )
    predict.set_display_name("2. MLflow 모델 추론")

    save = run_step(
        code=SAVE_CODE,
        prefix=predict.outputs["next_prefix"],
    )
    save.set_display_name("3. S3 결과 저장·검증")

    for task in [retrieve, predict, save]:
        kubernetes.use_secret_as_env(
            task,
            secret_name="feature-s3-credentials",
            secret_key_to_env={
                "AWS_ACCESS_KEY_ID": "AWS_ACCESS_KEY_ID",
                "AWS_SECRET_ACCESS_KEY": "AWS_SECRET_ACCESS_KEY",
                "AWS_DEFAULT_REGION": "AWS_DEFAULT_REGION",
            },
        )
        task.set_env_variable("AWS_EC2_METADATA_DISABLED", "true")
        task.set_env_variable("OPENBLAS_NUM_THREADS", "1")
        task.set_cpu_limit("1")
        task.set_memory_limit("1Gi")


if __name__ == "__main__":
    prefix = f"week02-batch/{uuid4().hex}"

    compiler.Compiler().compile(
        pipeline_func=batch_pipeline,
        package_path="batch_pipeline.yaml",
    )
    print("실행 명세 생성: batch_pipeline.yaml")

    client = kfp.Client(
        host="http://127.0.0.1:8088",
        namespace="kubeflow",
    )
    run = client.create_run_from_pipeline_package(
        pipeline_file="batch_pipeline.yaml",
        arguments={"prefix": prefix},
        experiment_name="week02-batch-inference",
        run_name="feast-mlflow-s3-batch",
        enable_caching=False,
    )

    Path("latest_batch_run_id.txt").write_text(run.run_id)
    Path("latest_batch_prefix.txt").write_text(prefix)

    print("실행 제출 완료")
    print("Run ID:", run.run_id)
    print("최종 결과:", f"s3://feature-data-sets/{prefix}/results/predictions.csv")
