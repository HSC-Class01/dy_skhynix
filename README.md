# SK hynix DART Financial Agent

[![Dashboard](https://img.shields.io/badge/%F0%9F%94%97-Dashboard-1751D0?style=for-the-badge)](https://hsc-class01.github.io/dy_skhynix/)

> **대시보드 URL:** `https://hsc-class01.github.io/dy_skhynix/`  
> GitHub Pages를 활성화한 뒤 위 주소가 제공됩니다.

Open DART API로 SK하이닉스(고유번호 `00164779`)의 연결재무제표를 2010년부터 수집하고, 주요 재무수치·비율을 계산해 GitHub Pages 대시보드에 게시하는 자동화 프로젝트입니다.

## 수집 범위
| 구분 | DART 보고서 코드 | 저장 카테고리 |
|---|---:|---|
| 사업보고서 | 11011 | Annual |
| 반기보고서 | 11012 | Half-year |
| 1분기보고서 | 11013 | Quarterly |
| 3분기보고서 | 11014 | Quarterly |

매월 **1일 09:15 KST**에 GitHub Actions가 실행되며, 수동 실행도 가능합니다. 보고서 미공시·구조화 계정 미제공 연도는 임의 수치로 채우지 않고 `docs/data/unavailable_reports.json`에 사유를 기록합니다.

## API 키 설정
1. [Open DART](https://opendart.fss.or.kr/)에서 인증키를 발급받습니다.
2. GitHub 저장소 → **Settings → Secrets and variables → Actions** → **New repository secret**.
3. Name을 `DART_API_KEY`로, Value에 인증키를 입력합니다.
4. Actions 탭에서 **Refresh Open DART financials**를 선택해 **Run workflow**를 실행합니다.

API 키는 코드·README·브라우저 데이터에 포함하지 마세요.

## GitHub Pages 배포
1. `github-workflows` 폴더를 저장소의 `.github/workflows`로 이름 변경/이동합니다. (압축파일의 숨김폴더 업로드 문제를 피하기 위해 별도 폴더로 제공)
2. 저장소 **Settings → Pages**에서 Source를 **Deploy from a branch**, Branch를 `main`, Folder를 `/docs`로 설정합니다.
3. **About** 영역의 Website에 `https://hsc-class01.github.io/dy_skhynix/`를 입력합니다.
4. 배포 완료 후 README 상단 배지와 About 링크가 대시보드로 연결됩니다.

## 재무 데이터 및 비율
- 핵심 수치: 매출액, 매출총이익, 영업이익, 당기순이익, 자산·부채·자본, 유동자산·유동부채, 현금, 재고, 영업현금흐름(CFO), CAPEX
- 분석: 매출성장률, 매출총/영업/순이익률, 유동비율, 부채비율, 자기자본비율, FCF, ROA, ROE
- 단위: 원(KRW). 대시보드 그래프는 조원 표시.
- ROA/ROE/매출성장률은 연간 비교가 가능한 **Annual** 행에만 계산합니다.

## 국내 Peer firms
| 기업 | 비교 관점 | 비고 |
|---|---|---|
| 삼성전자 DS부문 | 메모리·파운드리 및 반도체 사이클 | 사업부문 공시 기준 차이 유의 |
| DB하이텍 | 시스템반도체 파운드리 | 메모리 중심 SK하이닉스와 사업모델 차이 |
| LX세미콘 | 팹리스·디스플레이 구동칩 | 고객·제품 믹스 차이 |
| 한미반도체 | HBM 후공정 장비 | 직접 메모리 제조사보다는 공급망 peer |
| ISC | 반도체 테스트 솔루션 | 후공정·테스트 공급망 peer |

## 주의
Open DART 구조화 재무제표의 이용 가능 범위와 계정명은 과거 공시·회계기준에 따라 다를 수 있습니다. 분석 전 `unavailable_reports.json`, 원 공시 및 `src/fetch_dart.py`의 계정 매핑을 검토하세요.
