# Upstage Document Parser Plugin for Dataiku

## 개요

이 Dataiku 플러그인은 Upstage의 Document Parser 서비스를 통합하여 Dataiku 워크플로우 내에서 고급 문서 및 이미지 파싱 기능을 제공합니다. 사용자는 Dataiku 폴더나 데이터셋에 저장된 다양한 형식의 문서와 이미지를 처리할 수 있습니다.

## 주요 기능

- 다양한 파일 형식의 문서 파싱
- 이미지 처리 기능
- 폴더 및 데이터셋 입력/출력 지원
- Upstage의 AI 기반 문서 파싱 서비스 통합

## 설치 방법

1. 플러그인 ZIP 파일 다운로드
2. Dataiku DSS에서 **관리 > 플러그인** 메뉴로 이동
3. **플러그인 추가 > 업로드** 클릭 후 다운로드한 ZIP 파일 선택
4. 플러그인 활성화

## 사용 방법

### 사전 요구사항

- Dataiku DSS 10.0 이상
- 유효한 Upstage API 인증 정보
- Python 3.7 이상

### 설정 방법

1. 플로우에 Upstage Document Parser 레시피 추가
2. 입력 설정:
   - 문서/이미지가 포함된 폴더 또는 파일 참조가 있는 데이터셋 선택
3. 출력 설정:
   - 폴더 또는 데이터셋 출력 선택
4. Upstage API 인증 정보 및 파싱 옵션 설정

### 입력/출력

#### 입력 옵션
- **폴더 입력**: 처리할 문서와 이미지가 포함된 디렉토리
- **데이터셋 입력**: 파일 참조 또는 바이너리 데이터가 포함된 데이터셋

#### 출력 옵션
- **폴더 출력**: 처리된 문서와 추출된 데이터
- **데이터셋 출력**: 파싱된 정보가 포함된 구조화된 데이터

## 개발 정보

### 프로젝트 구조
upstage-document-parser/
├── python-lib/
│ └── upstgaedocumentparser/
│ └── utils/
│ ├── init.py
│ └── recipes_io_utils.py
├── custom-recipes/
├── parameter-sets/
├── code-env/
└── plugin.json

### 주요 구성 요소

- `recipes_io_utils.py`: 폴더 및 데이터셋 타입의 입출력 작업 처리
- `plugin.json`: 플러그인 설정 및 메타데이터
- Custom recipes: 특정 문서 파싱 기능 구현

## 라이선스

Apache Software License 2.0

## 지원

문의사항 및 지원은 다음 연락처로 문의해 주세요:
- 개발자: 김태현 (AzwellAI)
- 이메일: taehyun.kim@azwell.ai

## 버전 이력

- 0.0.1: 초기 릴리스

## 주의사항

- API 사용량 및 제한사항은 Upstage 서비스 정책을 따릅니다.
- 대용량 문서 처리 시 메모리 사용량에 주의하세요.
- 민감한 정보가 포함된 문서 처리 시 보안 정책을 준수하세요.

## 문제 해결

일반적인 문제 해결 방법:
1. API 인증 정보가 올바르게 설정되었는지 확인
2. 입력 파일 형식이 지원되는지 확인
3. 로그를 확인하여 구체적인 오류 메시지 확인

## 향후 계획

- 추가 문서 형식 지원
- 성능 최적화
- 사용자 인터페이스 개선