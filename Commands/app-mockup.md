---
name: app-mockup
description: "앱 스크린샷/화면 녹화를 아이폰·갤럭시 기기 목업 프레임으로 합성"
category: utility
complexity: basic
mcp-servers: []
personas: []
---

# /app-mockup - 앱 스크린샷 기기 목업 생성

`app-mockup` Skill을 실행한다. Skill 도구로 `app-mockup`을 호출하고, 그 안에 정의된 워크플로우(0번 확인 질문부터 산출물 검증까지)와 디바이스 프레임 스펙·레이아웃·렌더링 방법을 그대로 따른다.

사용자가 이 명령어와 함께 원본 이미지/영상을 첨부했다면 그것을 원본으로 쓴다. 첨부가 없으면 Skill의 0번 규칙대로, 폴더에서 임의로 찾지 말고 반드시 사용자에게 원본 파일을 요청한다.

인자(있다면): $ARGUMENTS
