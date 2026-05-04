# PowerSite MVP

Vercel 배포 루트입니다. 실제 앱 코드는 `power_site_mvp/` 폴더 안에 있습니다.

## Vercel 라우팅

저장소 루트가 Vercel Root Directory로 설정되어도 `/`와 `/api/*` 요청은 `api/index.py`를 통해 `power_site_mvp.app.main:app` FastAPI 앱으로 연결됩니다.

```text
/
/login
/api/analyze
/api/score
/api/report/markdown
```

기존처럼 Vercel Root Directory를 `power_site_mvp`로 잡아도 `power_site_mvp/vercel.json`과 `power_site_mvp/api/index.py`가 동작합니다.

## 빌드 확인

```bash
npm run build
```

## 환경변수

Vercel 환경변수에 아래 값을 등록합니다.

```text
KAKAO_REST_API_KEY=
VWORLD_API_KEY=
APP_LOGIN_ID=
APP_LOGIN_PASSWORD=
KAKAO_JS_KEY=
APP_SESSION_SECRET=
VWORLD_DOMAIN=https://배포도메인.vercel.app
```

`KAKAO_REST_API_KEY`와 `VWORLD_API_KEY`는 서버 API에서만 사용합니다. 지도 표시용 `KAKAO_JS_KEY`는 브라우저 키이므로 카카오 개발자 콘솔에서 배포 도메인 제한을 설정하세요.
