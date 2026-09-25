# chem-depth-info

화학 분석 장비에 따른 주기율표에서 선택된 원소가 얼마나 깊이, 넓게 파고 들어가는지 시뮬레이션으로 알아보는 Web app.

**Python 코드는 그대로 있습니다.** 핵심 모델은 `app/simulation.py` 이고, Flask와 Streamlit이 같은 함수를 씁니다. GitHub Pages용으로 `docs/` 정적 파일을 **추가**했을 뿐, Flask/Python을 지우지 않았습니다.

## 실행

Python 3.12:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Streamlit (추천하는 로컬/클라우드 Python UI)

```bash
streamlit run streamlit_app.py    # http://localhost:8501
```

공개 무료 호스팅은 [Streamlit Community Cloud](https://share.streamlit.io/)에 이 GitHub 저장소를 연결하면 됩니다. GitHub Pages와 달리 Python 서버를 켜 줍니다.

### Flask (커스텀 주기율표 · REST API)

```bash
python app.py                     # http://localhost:5000
```

환경변수 `HOST`(기본 `0.0.0.0`), `PORT`(기본 `5000`), `FLASK_DEBUG`(기본 `1`).

## 왜 Flask가 있었고, Streamlit도 되나?

됩니다. 처음 환경설정 에이전트가 Flask를 고른 이유는 **커스텀 주기율표 + Canvas 단면 + `/api/simulate` JSON API**를 한 페이지에 넣기 쉬워서입니다. 과학 계산 UI만 필요하면 Streamlit이 더 짧고, 계산은 전부 기존 Python을 그대로 씁니다.

GitHub Pages에는 Flask/Streamlit 둘 다 그대로 올릴 수 없습니다. Pages는 정적 파일만 호스팅해서, 그때만 `docs/` JavaScript 복사본이 필요합니다.

## 기술 스택

- 시뮬레이션: Python (`app/simulation.py`)
- UI: Streamlit (`streamlit_app.py`) 또는 Flask (`app.py` + `app/templates` + `app/static`)
- 원소 데이터: `app/static/data/elements.json` (`mendeleev`로 생성)
- 선택: GitHub Pages 정적본 (`docs/`)

## 개발

```bash
pip install -r requirements-dev.txt
pytest
python scripts/generate_elements.py
```

## Flask API

| 메서드 | 경로 | 설명 |
| --- | --- | --- |
| GET | `/` | 웹 UI |
| GET | `/healthz` | 헬스체크 |
| GET | `/api/elements` | 원소 데이터 목록 |
| GET | `/api/equipment` | 분석 장비 메타데이터 |
| POST | `/api/simulate` | `{symbol, equipment, energy, shots?}` → 깊이/폭 계산 |

## Cloud Agent 환경

`.cursor/environment.json` 의 `web` 터미널은 Flask(5000), `streamlit` 터미널은 Streamlit(8501)입니다.

## 시뮬레이션 모델 (단순화)

정밀 계측이 아닌, 원소(질량·원자번호·밀도)와 장비·에너지에 따라 값이 일관되게 변하도록 설계한 근사 모델입니다.

- 전자 프로브(EDS, EPMA/WDS): 깊이 = Kanaya–Okayama 전자 비정. 폭 = 프로브 직경 + Castaing/Reed 상호작용 배(pear)
- AES: 깊이는 오제 전자 탈출 깊이(~3λ), 폭은 집속 빔
- 이온 빔(SIMS, GD-OES, GD-MS): 깊이 = LSS형 투사 범위. 폭 = 래스터/양극 직경(기본값은 일상적인 스팟이지 최대 크레이터가 아님)
- 광전자(XPS): 깊이 = IMFP의 약 3배(TPP형). 폭 = X선 스팟
- 레이저(LDI-MS, LIBS, LA-ICP-MS): 깊이 = 펄스 에너지·shot 삭마. 폭 = 집속 스팟
- GD-MS / LDI-MS / LIBS / LA-ICP-MS는 빔 세기와 shot 수를 같이 조절합니다.
