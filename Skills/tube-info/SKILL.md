---
name: tube-info
description: TubeAlfred MCP 도구로 유튜브 영상의 채널정보(채널명/구독자/채널URL), 영상정보(제목/조회수/좋아요/댓글수/업로드일/길이/카테고리/설명), 챕터 타임라인, 전체 자막을 가져와 정리해서 보여준다. 사용자가 유튜브 영상 URL을 주면서 정보를 요약해달라거나, 영상 내용이나 자막을 알고 싶다고 하거나, "/tube-info"를 직접 언급하면 이 스킬을 사용한다.
---

# tube-info — TubeAlfred로 유튜브 영상 정보 요약

유튜브 URL 하나를 받아서, TubeAlfred MCP 도구 3개만으로 영상 메타데이터와 전체 자막을 정리해 보여준다.

## 실행 순서

1. **URL 확보**: 인자로 유튜브 URL이 주어지면 그것을 사용한다. 없으면 사용자에게 물어본다.

2. **도구 스키마 로드**: 아래 세 도구가 아직 로드되지 않았다면 먼저 ToolSearch를 호출한다. MCP 서버 접두사(`mcp__<server-id>__`)는 연결될 때마다 바뀔 수 있으므로, 접두사를 하드코딩하지 말고 도구 이름 키워드로 검색한다.
   ```
   ToolSearch(query: "youtube_video_enhanced youtube_channel_get youtube_video_transcript")
   ```

3. **영상/채널 정보 조회** (병렬로 호출 가능):
   - `youtube_video_enhanced(video_id=<URL>)` — 제목, 조회수, 좋아요, 댓글수, 업로드일, 길이, 카테고리, 설명, 챕터, 채널 id/url을 담고 있다.
   - `youtube_channel_get(channel_id=<video_enhanced 결과의 channel.id 또는 channel.url>)` — 구독자 수 등 채널 정보.

4. **자막 조회** (한국어 우선):
   - 먼저 `youtube_video_transcript(video_id=<URL>)`을 언어 지정 없이 호출해서 `available_tracks`를 확인한다.
   - `available_tracks`에 `ko` 계열 언어가 있는데 방금 받은 결과가 한국어가 아니면, `youtube_video_transcript(video_id=<URL>, language="ko")`로 한 번 더 호출해 한국어 트랙을 받는다.
   - 한국어가 아예 없으면 처음 받은 결과(보통 영어 또는 유일하게 존재하는 언어)를 그대로 쓴다.
   - 표시할 전체 자막 텍스트는 `transcript_only_text` 필드를 사용한다 (이미 줄 단위로 합쳐진 텍스트라 따로 가공할 필요 없음).

5. **결과 정리해서 채팅에 텍스트로 보여준다** (파일 생성하지 않음). 아래 형식을 따른다:

```
채널명: ...
구독자: ...
채널 URL: ...

제목: ...
조회수: ...
좋아요: ...
댓글: ...
업로드일: ...
길이: ...
카테고리: ...
URL: ...

설명:
...

타임라인: (chapters 배열이 비어있지 않을 때만 이 섹션을 포함)
[시작시간] 챕터 제목
...

전체 자막:
...
```

## 참고사항

- `youtube_comments_list`는 이 스킬의 기본 흐름에 포함하지 않는다 — 다른 도구들은 호출당 1크레딧이지만 댓글 조회는 20크레딧으로 훨씬 비싸다. 사용자가 댓글 반응이나 시청자 인사이트를 따로 요청하면 그때 별도로 호출한다.
- `youtube_video_enhanced`의 `related_videos`는 이 스킬 결과에 기본 포함하지 않는다 (실제 테스트에서 관련성이 낮은 결과가 섞여 나온 적 있음). 사용자가 경쟁/관련 영상 비교를 요청하면 그때 활용한다.
