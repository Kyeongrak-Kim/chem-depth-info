# chem-depth-info

화학 분석 장비에 따른 주기율표에서 선택된 원소가 얼마나 깊이, 넓게 파고 들어가는지 시뮬레이션으로 알아보는 Web app. 파이썬 기반이며 모바일/데스크톱 버전 양쪽 다 지원.

## 개요

- 주기율표에서 원소를 고르고, 분석 장비(SIMS · GD-OES · XPS · AES · EPMA)와 빔 에너지를 선택하면
- 해당 조건에서의 **침투 깊이**와 **분석 폭**을 물리 기반 모델로 계산하고, 단면 시각화로 보여줍니다.
- 반응형 UI로 데스크톱과 모바일을 모두 지원합니다.

## 기술 스택

- Backend: Python 3.12 + [Flask](https://flask.palletsprojects.com/)
- Frontend: 순수 HTML/CSS/JavaScript (Canvas 시각화)
- 원소 데이터: [`mendeleev`](https://mendeleev.readthedocs.io/) 로 생성한 정적 JSON (`app/static/data/elements.json`)

## 로컬 실행

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py            # http://localhost:5000
```

환경변수 `HOST`(기본 `0.0.0.0`), `PORT`(기본 `5000`)로 바인딩을 바꿀 수 있습니다.

## 개발 (테스트 · 데이터 재생성)

```bash
pip install -r requirements-dev.txt
pytest                              # 테스트 실행
python scripts/generate_elements.py # elements.json 재생성 (mendeleev 필요)
```

## API

| 메서드 | 경로 | 설명 |
| --- | --- | --- |
| GET | `/` | 웹 UI |
| GET | `/healthz` | 헬스체크 |
| GET | `/api/elements` | 원소 데이터 목록 |
| GET | `/api/equipment` | 분석 장비 메타데이터 |
| POST | `/api/simulate` | `{symbol, equipment, energy}` → 깊이/폭 계산 |

## Cloud Agent 환경

`.cursor/environment.json` 에 정의되어 있습니다. `scripts/cloud-setup.sh` 가 venv를 만들고 의존성을 설치하며,
`web` 터미널이 개발 서버를 5000 포트로 띄웁니다.

## 시뮬레이션 모델 (단순화)

정밀 계측이 아닌, 원소(질량·원자번호·밀도)와 장비·에너지에 따라 값이 일관되게 변하도록 설계한 근사 모델입니다.

- 전자 프로브(AES, EPMA): Kanaya–Okayama 전자 침투 범위
- 이온 빔(SIMS, GD-OES): 경험식 기반 이온 투사 범위
- 광전자(XPS): 비탄성 평균자유행로(IMFP) 기반 표면 감지 깊이
