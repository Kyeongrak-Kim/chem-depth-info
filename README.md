# chem-depth-info

화학 분석 장비에 따른 주기율표에서 선택된 원소가 얼마나 깊이, 넓게 파고 들어가는지 시뮬레이션으로 알아보는 Web app. 모바일/데스크톱 양쪽을 지원합니다.

**지금 바로 열기:** [정적 시뮬레이터 미리보기](https://raw.githack.com/Kyeongrak-Kim/chem-depth-info/cursor/github-pages-static-0f05/docs/index.html)

공식 GitHub Pages 주소(`https://kyeongrak-kim.github.io/chem-depth-info/`)는 저장소 소유자가 [Pages 설정](https://github.com/Kyeongrak-Kim/chem-depth-info/settings/pages)에서 한 번 켜야 살아납니다. 이 에이전트 토큰으로는 Pages를 켤 수 없습니다.

## 개요

- 주기율표에서 원소를 고르고, 분석 장비(SIMS · GD-OES · XPS · AES · EPMA)와 빔 에너지를 선택하면
- 해당 조건에서의 **침투 깊이**와 **분석 폭**을 물리 기반 모델로 계산하고, 단면 시각화로 보여줍니다.
- 반응형 UI로 데스크톱과 모바일을 모두 지원합니다.

## 기술 스택

- 공개 사이트: 정적 HTML/CSS/JavaScript (`docs/`). 시뮬레이션은 브라우저에서 계산합니다.
- 로컬/Codespaces 개발 서버: Python 3.12 + [Flask](https://flask.palletsprojects.com/)
- 원소 데이터: [`mendeleev`](https://mendeleev.readthedocs.io/) 로 생성한 정적 JSON (`docs/data/elements.json`)

## 로컬 실행

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py            # http://localhost:5000
```

환경변수 `HOST`(기본 `0.0.0.0`), `PORT`(기본 `5000`), `FLASK_DEBUG`(기본 `1`)로 바인딩과 디버그 모드를 바꿀 수 있습니다.

## GitHub Codespaces에서 열기

[![Open in GitHub Codespaces](https://img.shields.io/badge/Open%20in-GitHub%20Codespaces-blue?logo=github)](https://codespaces.new/Kyeongrak-Kim/chem-depth-info/tree/cursor/github-codespaces-0f05)

1. 위 배지를 누르거나, 저장소에서 **Code → Codespaces → Create codespace on `cursor/github-codespaces-0f05`** 를 선택합니다.
2. 컨테이너가 준비되면 `postStartCommand`가 Flask를 **5000** 포트에서 자동으로 켭니다.
3. Codespaces가 미리보기 탭을 열거나, `https://<codespace이름>-5000.app.github.dev` 로 페이지가 열립니다.

## GitHub Pages

정적 사이트는 `docs/` 에 있습니다. 주소는 [https://kyeongrak-kim.github.io/chem-depth-info/](https://kyeongrak-kim.github.io/chem-depth-info/) 입니다.

저장소 소유자가 [Pages 설정](https://github.com/Kyeongrak-Kim/chem-depth-info/settings/pages)에서 한 번 켜 줘야 공개됩니다.

1. **바로 켜기:** Source를 **Deploy from a branch** 로 두고, Branch를 `cursor/github-pages-static-0f05`(머지 후에는 `main`), Folder를 `/docs` 로 저장합니다.
2. **Actions로 켜기:** Source를 **GitHub Actions** 로 저장한 뒤 `main`에 머지하거나 workflow를 수동 실행합니다.

로컬에서 정적 버전만 보려면:

```bash
python3 -m http.server 8080 --directory docs
# http://127.0.0.1:8080
```

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
