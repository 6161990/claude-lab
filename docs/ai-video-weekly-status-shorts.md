# AI 영상 제작 실행안: 주간 과제 뉴스 쇼츠

## 목표

- 플랫폼: YouTube Shorts
- 길이: 40초
- 화면비: 9:16
- 톤: 유머러스하고 귀여운 팀 내부 뉴스 브리핑
- 제작 순서: 이미지 시안 생성 → 베스트 컷 선택 → Veo 3.1 I2V → BGM/나레이션 생성 → 편집

## 캐릭터 고정 스타일

```text
A cute Shiba Inu mascot reporter with a round white mascot body inspired by the provided ixio reference image. The character has a Shiba Inu face only: tan fur, cream muzzle, round black eyes, small triangular ears, cheerful expression. The body is a smooth glossy white chubby mascot suit with short arms and legs. It wears a deep purple wizard hat with small yellow stars, a purple strap detail on the side, and a small purple pin shaped like the ixio logo on the chest. Cute, clean, soft 3D mascot style, pastel lavender background, soft studio lighting, playful corporate news vibe, high-quality 3D animation, vertical 9:16 composition.

Keep the same character face, body shape, hat, purple color, ixio logo pin, and soft 3D mascot style in every scene.
```

## 공통 부정 프롬프트

```text
Do not change the character design. No human face, no realistic dog body, no scary expression, no extra limbs, no distorted paws, no unreadable messy text, no watermark, no random logos, no broken face, no aggressive mood, no dark dramatic lighting.
```

## 1단계: Hylo 이미지 시안 생성 지시문

Hylo Agent에 아래 내용을 그대로 넣는다.

```text
아직 영상을 만들지 말고 이미지 시안만 생성해줘.

모델: Nano-Banana Pro
목표: YouTube Shorts용 40초 AI 영상의 이미지 시안 생성
화면비: 9:16
출력: 각 장면당 4컷씩
스타일: 귀엽고 유머러스한 3D 마스코트 뉴스 리포트
중요: 캐릭터 일관성을 반드시 유지해줘.

공통 캐릭터:
A cute Shiba Inu mascot reporter with a round white mascot body inspired by the provided ixio reference image. The character has a Shiba Inu face only: tan fur, cream muzzle, round black eyes, small triangular ears, cheerful expression. The body is a smooth glossy white chubby mascot suit with short arms and legs. It wears a deep purple wizard hat with small yellow stars, a purple strap detail on the side, and a small purple pin shaped like the ixio logo on the chest. Cute, clean, soft 3D mascot style, pastel lavender background, soft studio lighting, playful corporate news vibe.

공통 금지:
Do not change the character design, no human face, no realistic dog body, no distorted paws, no extra limbs, no unreadable text, no watermark, no random logos.

Scene 01: 오프닝 뉴스 데스크
- 목적: "팀 주간 과제 뉴스" 시작
- 컷 A: 시바견 앵커가 작은 뉴스 데스크 뒤에서 손을 흔드는 장면
- 컷 B: 보라색 말풍선에 "주간 과제 뉴스"가 떠 있는 장면
- 컷 C: 작은 수정구슬 모양 화면에 업무 보드가 반짝이는 장면
- 컷 D: 카메라를 향해 귀엽게 인사하는 클로즈업

Scene 02: 완료된 과제
- 목적: 이번 주 완료된 업무를 기쁘게 전달
- 컷 A: 체크 표시가 뜬 작은 업무 카드들을 가리키는 장면
- 컷 B: "DONE" 스티커들이 반짝이고 시바견이 뿌듯한 표정
- 컷 C: 미니 화이트보드 앞에서 완료 항목을 발표하는 장면
- 컷 D: 작은 별 파티클이 터지는 축하 뉴스 장면

Scene 03: 진행 중 과제
- 목적: 아직 진행 중인 과제를 귀엽게 보도
- 컷 A: 시바견이 여러 업무 카드를 양손에 들고 바쁜 표정
- 컷 B: 회전하는 진행률 바 옆에서 고개를 끄덕이는 장면
- 컷 C: 노트북과 업무 보드 사이를 분주히 보는 장면
- 컷 D: "IN PROGRESS" 느낌의 보라색 진행 카드 앞에 선 장면

Scene 04: 이슈와 블로커
- 목적: 막힌 이슈를 유머러스하게 표현
- 컷 A: 작은 빨간 경고등 앞에서 시바견이 놀란 표정
- 컷 B: 꼬인 업무 라인을 들여다보는 장면
- 컷 C: "ISSUE" 카드가 살짝 흔들리고 시바견이 침착하게 리포트
- 컷 D: 수정구슬 안에 작은 버그 아이콘과 물음표가 보이는 장면

Scene 05: 다음 액션과 엔딩
- 목적: 다음 주 액션을 긍정적으로 마무리
- 컷 A: 시바견이 보라색 체크리스트를 들고 엄지척
- 컷 B: 팀 로드맵이 별자리처럼 이어지는 귀여운 배경
- 컷 C: "다음 주도 계속됩니다" 느낌의 엔딩 포즈
- 컷 D: 시바견이 마법봉처럼 펜을 들고 반짝이는 마무리

선택 기준:
- 시바견 얼굴과 익시오 스타일 의상이 모든 장면에서 동일해야 함
- ixio 로고 핀이 가슴 쪽에 작고 깔끔하게 보여야 함
- 영상화하기 좋게 캐릭터가 화면 중앙에 안정적으로 있어야 함
- 텍스트는 너무 많이 넣지 말고, 필요하면 큰 키워드만 사용
```

## 2단계: 베스트 컷 선택 기준

- 캐릭터 얼굴, 의상, 모자, 로고 핀이 가장 일관적인 컷을 고른다.
- 손/발/얼굴이 깨진 컷은 버린다.
- 텍스트가 이상하게 나온 컷은 버린다.
- 캐릭터가 너무 작거나 화면 가장자리에서 잘린 컷은 버린다.
- 장면별로 감정이 명확한 컷을 고른다.

## 3단계: Veo 3.1 I2V 공통 설정

```text
Model: Veo 3.1
Format: vertical 9:16
Duration: 8 seconds
Style: cute humorous 3D mascot news report
Keep the Shiba Inu mascot character exactly consistent with the source image: Shiba Inu face, round white mascot body, purple wizard hat with yellow stars, purple ixio logo pin, pastel lavender studio lighting.
Negative prompt: no character redesign, no face distortion, no extra limbs, no messy text, no watermark, no random logo, no realistic dog body.
```

## 4단계: 장면별 Veo 3.1 I2V 프롬프트

### Scene 01

```text
The Shiba Inu mascot anchor waves at the camera from behind a tiny news desk. A soft purple speech bubble pops in with a playful weekly news intro feeling. Camera slowly pushes in. Cute upbeat expression. Keep the source image character design exactly the same.
```

### Scene 02

```text
The mascot points proudly at floating task cards with check marks. The cards gently bounce and sparkle. The mascot nods with a confident smile. Camera pans slightly from left to right. Keep motion smooth and cute.
```

### Scene 03

```text
The mascot looks busy but cheerful, holding several floating task cards labeled as progress items. A progress bar fills slowly in the background. Camera stays in a medium shot with subtle playful cartoon energy.
```

### Scene 04

```text
A small warning light blinks softly. The mascot reacts with a surprised but cute expression, then quickly becomes serious like a professional reporter. A tiny issue card shakes gently. Camera does a quick comedic zoom-in, then settles.
```

### Scene 05

```text
The mascot holds a checklist and gives a cheerful thumbs up. Soft star particles appear around the character. The background roadmap lights up one step at a time. Camera slowly pulls back for a clean ending pose.
```

## 5단계: BGM 생성 프롬프트

```text
Create a cute and humorous corporate news background music track for a 40-second YouTube Shorts video. Bright marimba, soft synth plucks, light percussion, playful newsroom rhythm, upbeat but not too loud, friendly tech-company mood, clean loopable ending. No dramatic tension, no heavy bass, no vocals.
```

## 6단계: 나레이션 대본

```text
Scene 01:
안녕하세요. 이번 주 과제 진행 상황을 전해드릴 시바 특파원입니다.

Scene 02:
먼저 완료 소식입니다. 핵심 과제 몇 건이 무사히 체크 완료됐습니다. 박수는 마음속으로 크게 부탁드립니다.

Scene 03:
진행 중인 과제도 있습니다. 아직 달리는 중이지만, 방향은 맞고 속도도 나쁘지 않습니다.

Scene 04:
이슈도 있었습니다. 일부 항목은 확인이 더 필요하고, 의존 작업이 살짝 줄을 잡고 있습니다.

Scene 05:
다음 액션은 이슈 정리, 담당자 확인, 우선순위 재조정입니다. 이상, 다음 주에도 귀엽지만 정확하게 전해드리겠습니다.
```

## 7단계: 편집 체크리스트

- 첫 1초 안에 "주간 과제 뉴스" 콘셉트가 보여야 한다.
- 각 장면은 8초 기준으로 자른다.
- 자막은 하단 안전 영역 안에 배치한다.
- 실제 팀 과제명은 자막 또는 업무 카드에 후반 편집으로 넣는다.
- 이슈 장면은 부정적으로 끝내지 말고 바로 다음 액션으로 연결한다.
- 컷 전환은 pop, soft wipe, sparkle transition 중 하나로 통일한다.
