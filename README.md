# todo-cli

간단한 할일 목록 CLI 학습용 프로젝트입니다.

## 기능

- `add_task(tasks, task_name)`: tasks 리스트에 새 할일을 추가하고 리스트를 반환합니다.
- `format_task(index, task_name)`: `"1. 할일이름"` 형태의 문자열로 포맷합니다.

## 실행

```bash
python todo.py
```

출력 예시:

```
1. 장보기
2. 운동하기
3. 독서하기
```

## 카카오톡 날씨 알림

매일 정해진 시간에 서울 날씨 요약을 카카오톡 "나에게 보내기"로 발송하는 기능입니다.

- `kakao_auth.py`: 카카오 로그인 OAuth 인증(최초 1회 실행, 브라우저로 로그인/동의 후 `kakao_token.json`에 토큰 저장)
- `kakao_send.py`: 토큰을 이용해 카카오톡 "나에게 보내기"로 메시지를 발송(만료 시 자동 갱신)
- `notify_weather.py`: wttr.in에서 서울 날씨를 가져와 메시지를 만들고 발송

### 설정

1. [카카오 디벨로퍼스](https://developers.kakao.com)에서 앱을 등록하고 REST API 키, Client Secret을 발급받습니다.
2. 카카오 로그인 Redirect URI에 `http://localhost:5000/oauth`를 등록하고, 동의항목에서 `talk_message`를 활성화합니다.
3. 프로젝트 루트에 `.env` 파일을 만들고 아래 값을 채웁니다.

   ```
   KAKAO_REST_API_KEY=발급받은 REST API 키
   KAKAO_CLIENT_SECRET=발급받은 Client Secret
   KAKAO_REDIRECT_URI=http://localhost:5000/oauth
   ```

4. 최초 1회 인증을 진행합니다.

   ```bash
   python kakao_auth.py
   ```

5. 날씨 알림을 테스트합니다.

   ```bash
   python notify_weather.py
   ```

### 자동 실행 (Windows 작업 스케줄러)

매일 오전 8시에 자동 실행되도록 `KakaoWeatherNotify`라는 이름의 작업 스케줄러 작업이 등록되어 있습니다.

```powershell
$action = New-ScheduledTaskAction -Execute "python.exe 경로" -Argument "notify_weather.py" -WorkingDirectory "프로젝트 경로"
$trigger = New-ScheduledTaskTrigger -Daily -At 8:00AM
Register-ScheduledTask -TaskName "KakaoWeatherNotify" -Action $action -Trigger $trigger -Force
```

> 참고: 카카오 "나에게 보내기" API로 보낸 메시지는 카카오톡 푸시 알림이 뜨지 않을 수 있습니다(카카오 정책상 본인이 보낸 메시지로 처리됨). 메시지 자체는 정상적으로 채팅방에 도착합니다.

> `.env`, `kakao_token.json`에는 민감한 인증 정보가 들어있어 `.gitignore`에 포함되어 있습니다.
