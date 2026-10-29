import kfp

client = kfp.Client(host="http://127.0.0.1:8088")
pipelines = client.list_pipelines(page_size=10).pipelines or []

print("KFP 서버 연결: 성공")
print("조회한 파이프라인 수:", len(pipelines))
for pipeline in pipelines:
    print("-", pipeline.display_name)
