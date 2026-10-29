# 공개 데이터 준비

[UCI Adult](https://archive.ics.uci.edu/dataset/2/adult)의 adult.data를 내려받아 결측 표기 ?가 있는 행을 제외하고 범주형 피처 8개와 Target을 선택합니다. UCI 원본은 CC BY 4.0이며 출처는 Becker, B. & Kohavi, R. (1996), DOI:10.24432/C5XW20입니다.

```bash
.venv/bin/python prepare_data.py
```

실제 학습 환경은 Docker Python 3.11이므로 위 코드는 해당 컨테이너 안에서 실행합니다. 자세한 명령은 [챕터 안내](../README.md)를 따릅니다. 기존 income_data.csv는 덮어쓰지 않습니다.

| 생성 파일 | 내용 |
|---|---|
| data/income_data.csv | 30,162행·범주 피처 8개·Target |
| feast/feature_data/demographic_features.parquet | Sex·Native_country·Race·키·시각 |
| feast/feature_data/occupational_features.parquet | Workclass·Education·Occupation·키·시각 |
| feast/feature_data/relationship_features.parquet | Relationship·Marital-Status·키·시각 |
| data/provenance.json | 다운로드 출처·압축 파일 SHA-256·합성 값 안내 |

범주 문자열의 선행 공백을 유지합니다. user_id와 feature_timestamp는 실제 사람 식별자·관측 시각이 아닌 결정적으로 생성한 실습용 값입니다. 기존 강의 데이터의 UUID·시각과 동일하다고 주장하지 않습니다. 공개 원본에서 새로 생성한 CSV로 기존 모델 지표가 재현됨을 확인했습니다.
