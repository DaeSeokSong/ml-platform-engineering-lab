"""공개 저장소의 코드 문법·문서 연결·인증정보 노출을 검사합니다."""
import ast
import json
import re
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
tracked = subprocess.check_output(['git', '-C', str(root), 'ls-files', '--cached', '--others', '--exclude-standard'], text=True).splitlines()
errors = []
python_count = 0
links = 0
for relative in sorted(set(tracked)):
    path = root / relative
    if path.suffix not in {'.py', '.md', '.html', '.yaml', '.yml', '.txt', '.sh', '.json', '.example'}:
        continue
    text = path.read_text(encoding='utf-8-sig')
    if path.suffix == '.py':
        python_count += 1
        try:
            ast.parse(text, filename=relative)
        except SyntaxError as exc:
            errors.append(f'문법: {relative}:{exc.lineno}')
    if re.search(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]', text):
        errors.append(f'설명 언어 확인: {relative}')
    if re.search(r'github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16}|-{5}BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-{5}', text):
        errors.append(f'인증정보 형식: {relative}')
    if re.search(r'/home/[a-zA-Z0-9_-]+/', text) or re.search(r'[A-Z]:[/\\]Users[/\\][A-Za-z0-9_.-]+[/\\]', text):
        errors.append(f'개인 절대 경로: {relative}')
    if path.suffix == '.md':
        for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', text):
            if target.startswith(('http:', 'https:', '#', 'mailto:')):
                continue
            target = target.split('#')[0]
            links += 1
            if not (path.parent / target).exists():
                errors.append(f'끊어진 링크: {relative} -> {target}')
print(json.dumps({'python_files': python_count, 'local_links': links, 'errors': errors}, ensure_ascii=False, indent=2))
if errors:
    raise SystemExit(1)
