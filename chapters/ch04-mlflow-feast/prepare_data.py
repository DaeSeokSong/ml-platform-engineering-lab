"""UCI 공개 데이터에서 학습 CSV와 실습용 피처 파일을 생성합니다."""
import argparse
import hashlib
import io
import json
import uuid
import zipfile
from pathlib import Path
from urllib.request import urlopen

import pandas as pd

URL = 'https://archive.ics.uci.edu/static/public/2/adult.zip'
parser = argparse.ArgumentParser()
parser.add_argument('--output-dir', default='.')
args = parser.parse_args()
root = Path(args.output_dir)
output = root / 'data/income_data.csv'
if output.exists():
    raise SystemExit('기존 income_data.csv를 덮어쓰지 않습니다. 다른 출력 폴더를 지정하세요.')
with urlopen(URL, timeout=60) as response:
    archive = response.read()
with zipfile.ZipFile(io.BytesIO(archive)) as zipped:
    raw = pd.read_csv(zipped.open('adult.data'), header=None, dtype=str)
clean = raw.loc[~raw.apply(lambda column: column.str.strip().eq('?')).any(axis=1)].copy()
columns = {1: 'Workclass', 3: 'Education', 5: 'Marital-Status', 6: 'Occupation',
           7: 'Relationship', 8: 'Race', 9: 'Sex', 13: 'Native_country', 14: 'Target'}
df = clean[list(columns)].rename(columns=columns).reset_index(drop=True)
df['Target'] = df['Target'].str.strip()
assert len(df) == 30162, '공개 데이터의 예상 행 수가 달라졌습니다.'
output.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output, index=False)
ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, f'ml-platform-lab/adult/{index}')) for index in range(len(df))]
timestamps = pd.date_range('2023-01-01', periods=len(df), freq='s').astype('datetime64[us]')
feature_dir = root / 'feast/feature_data'
feature_dir.mkdir(parents=True, exist_ok=True)
groups = {
    'demographic_features.parquet': ['Sex', 'Native_country', 'Race'],
    'occupational_features.parquet': ['Workclass', 'Education', 'Occupation'],
    'relationship_features.parquet': ['Relationship', 'Marital-Status'],
}
for name, features in groups.items():
    frame = df[features].copy()
    frame['user_id'] = ids
    frame['feature_timestamp'] = timestamps
    frame.to_parquet(feature_dir / name, index=False)
metadata = {'source': URL, 'archive_sha256': hashlib.sha256(archive).hexdigest(), 'rows': len(df),
    'license': 'CC BY 4.0', 'citation': 'Becker, B. & Kohavi, R. (1996). Adult. DOI:10.24432/C5XW20',
    'note': 'user_id와 시각은 실제 인물 식별자·관측 시각이 아닌 재현 가능한 실습용 합성 값입니다.'}
(root / 'data/provenance.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
print('학습 CSV:', df.shape)
print('생성한 피처 파일:', len(groups))
print('ID·시각은 실습용 합성 값이며 범주 문자열의 선행 공백은 유지했습니다.')
