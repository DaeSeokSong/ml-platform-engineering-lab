# Prometheus·Grafana

prometheus-values.yaml과 grafana-values.yaml은 기존 Helm 설치에서 사용한 설정입니다. hello-joker의 /metrics를 수집하며 Grafana는 클러스터 내부 Prometheus 서비스를 데이터 소스로 사용합니다.

기존 실습의 포트는 Prometheus 9090, Grafana 3001이었습니다. Helm chart 정확한 버전과 신규 설치 명령은 추가 확인 대상이며 현재 파일만으로 설치를 완료했다고 간주하지 않습니다. Grafana 영속 저장은 꺼져 있으므로 대시보드 JSON을 별도로 관리해야 합니다.
