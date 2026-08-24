---
name: tube-info
description: "TubeAlfred로 유튜브 영상 정보/자막 요약"
category: utility
complexity: basic
mcp-servers: []
personas: []
---

# /tube-info - TubeAlfred로 유튜브 영상 정보 요약

`tube-info` Skill을 실행한다. Skill 도구로 `tube-info`를 호출하고, 그 안에 정의된 실행 순서(도구 스키마 로드 → 영상/채널 정보 조회 → 자막 조회 → 정리된 출력)를 그대로 따른다.

URL은 이 명령어의 인자로 받는다. 인자가 없으면 사용자에게 유튜브 영상 URL을 물어본다.

인자: $ARGUMENTS
