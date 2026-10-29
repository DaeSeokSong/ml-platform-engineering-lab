import kfp
from kfp import compiler, dsl


@dsl.component(base_image="python:3.11-bookworm")
def pass_number(value: int) -> int:
    print("전달할 값:", value)
    return value


@dsl.component(base_image="python:3.11-bookworm")
def double_number(value: int) -> int:
    result = value * 2
    print("받은 값:", value)
    print("두 배 결과:", result)
    return result


@dsl.pipeline(name="first-two-step-pipeline")
def first_pipeline(value: int = 5):
    first = pass_number(value=value)
    double_number(value=first.output)


if __name__ == "__main__":
    compiler.Compiler().compile(
        pipeline_func=first_pipeline,
        package_path="first_pipeline.yaml",
    )
    print("실행 명세 생성: first_pipeline.yaml")

    client = kfp.Client(host="http://127.0.0.1:8088")
    run = client.create_run_from_pipeline_package(
        pipeline_file="first_pipeline.yaml",
        arguments={"value": 5},
        experiment_name="week02-first-pipeline",
        run_name="pass-five-and-double",
        enable_caching=False,
    )
    print("실행 제출 완료")
    print("Run ID:", run.run_id)
