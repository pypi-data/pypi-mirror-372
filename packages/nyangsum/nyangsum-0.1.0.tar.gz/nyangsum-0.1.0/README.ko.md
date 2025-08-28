Nyangsum (냥썸)

[English](README.md) | [한국어](README.ko.md)

한국어 고양이 소리 로렘 입숨 생성기입니다. 냥/냐옹/나앙과 같은 기본 토큰이 자주 나오고, 때때로 늘임형(예: 냐아앙, 냐아아옹 등)이 섞입니다.

핵심 특징
- 토큰: 냥, 냐옹, 나앙(요청 반영), 늘임형 “냐” + “아”*k + (“앙” | “옹”)
- 기본 분포(조절 가능): 냥 0.45, 냐옹 0.30, 나앙 0.15, 늘임형 0.10
- 구두점: 문장 내부 쉼표/!/?/... 가능, 문장 끝 [., !, ?, ...], 가끔 따옴표/괄호
- 시드 고정으로 결정적 출력 제공

설치(로컬 개발)
```bash
python -m pip install -e .
```

빠른 시작

Python:
```python
from nyangsum import nyang

print(nyang.words(5))                     # 예: "냥 냐옹 냥 냥 냐옹"
print(nyang.sentence(words=8))            # 정확히 8단어로 한 문장
print("\n\n".join(nyang.paragraphs(2)))   # 두 개의 문단
```

CLI:
```bash
# 정확히 N개의 문장을, 각 M 단어로
python3 -m nyangsum --phrases 2 --words 6

# N개의 문장(단어 수는 [min, max]에서 균등 샘플)
python3 -m nyangsum --sentences 3 --min-words 5 --max-words 10

# N개의 문단, HTML 래핑 옵션
python3 -m nyangsum --paragraphs 2 --html

# 시드로 결정적 출력
python3 -m nyangsum --phrases 1 --words 10 --seed 42
```

예시
```bash
$ python3 -m nyangsum --phrases 1 --words 6
냥 냐옹 냥, 냐옹 나앙 냥.

$ python3 -m nyangsum --paragraphs 1 --html
<p>냐옹 냥 냥 냥? 냥 냐옹 냐옹 냥 냥 냥. 냥 냥 냥...</p>
```

API
- nyang.seed(value: int | None) -> None
  - 내부 RNG 시드 고정(결정적 출력)
- nyang.word(max_len=6, capitalize=False, weights: dict | None = None, elong_min_a=1, elong_max_a=4, tail_weights=None) -> str
  - 한 단어 생성
  - 기본 토큰: "냥", "냐옹", "나앙"
  - 늘임형: "냐" + "아"*k + ("앙" | "옹"), k ∈ [elong_min_a, elong_max_a]
  - 가중치 오버라이드 예: {"냥":0.5, "냐옹":0.3, "나앙":0.15, "elongated":0.05}
- nyang.words(n=1, as_list=False, sep=" ") -> str | list[str]
  - n개의 단어 생성(문자열 또는 리스트)
- nyang.phrase(words_count: int, punctuation=True) -> str
  - 정확히 words_count 단어로 한 문장, 내부 구두점/괄호/따옴표 가능
- nyang.phrases(n: int, words_count: int, as_list=False, punctuation=True) -> str | list[str]
  - n개의 문장을 생성(기본 줄바꿈으로 연결)
- nyang.sentence(words: int | None = None, word_range=(4, 12), punctuation=True) -> str
  - 한 문장. words 미지정 시 word_range에서 균등 샘플
- nyang.sentences(n=1, words: int | None = None, word_range=(4, 12), as_list=False, punctuation=True) -> str | list[str]
  - 여러 문장(기본 공백으로 연결)
- nyang.paragraph(sentence_range=(3, 7)) -> str
  - 문장 수를 범위에서 샘플하여 문단 생성
- nyang.paragraphs(n=1, sentence_range=(3, 7), as_list=False) -> str | list[str]
  - 여러 문단(기본 빈 줄로 구분)
- nyang.text(paragraphs_count=3, sentence_range=(3, 7), html=False) -> str
  - 여러 문단 생성; html=True 시 각 문단을 <p>로 감싸서 반환

CLI
- 선택
  - --phrases N --words M       N개의 문장, 각 M 단어
  - --sentences N               N개의 문장(단어 수는 --words 또는 --min-words/--max-words)
  - --paragraphs N              N개의 문단(--html 옵션 가능)
  - --words M                   정확히 M개의 단어(단독)
- 범위
  - --min-words X --max-words Y
  - --min-sentences A --max-sentences B
- 서식
  - --html                      문단을 <p>...</p>로 래핑(--paragraphs에서만 유효)
  - --no-punct                  문장부호 비활성화
- 재현성/튜닝
  - --seed INT
  - --weights JSON              기본/늘임형 가중치 덮어쓰기
    - 예: --weights '{"냥":0.5,"냐옹":0.3,"나앙":0.15,"elongated":0.05}'

분포/길이/늘임형
- 기본값은 “냥/냐옹/나앙”이 가장 자주 등장하도록 설계되어 있습니다.
- word(max_len)으로 단어 최대 길이를 제한해 과도한 늘임을 억제합니다(기본 6).
- 늘임형은 tail_weights로 "앙"/"옹" 비율을 조정할 수 있습니다.

개발
- 레퍼런스: meowrem_meosum(파이썬, 동일 UX)
- 빌드/배포 메타: pyproject.toml(hatchling)
- 테스트는 pytest 기반으로 손쉽게 추가 가능

라이선스
- MIT

링크
- 저장소: https://github.com/jadhvank/nyang_lorem_ipsum
