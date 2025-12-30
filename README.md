# KDS OCR Paddle

이 프로젝트는 PDF 파일의 레이아웃을 파싱하고 OCR 기술을 사용하여 텍스트와 이미지를 추출하는 워크플로우를 제공합니다.

## 시스템 구조

프로젝트는 데이터 관리를 위해 다음과 같은 디렉토리 구조를 사용합니다:

- `data/input/`: 처리할 원본 PDF 파일을 배치하는 곳입니다.
- `data/chunks/`: 큰 PDF 파일을 처리하기 쉬운 크기로 분할한 파일들이 저장됩니다.
- `data/output/`: OCR 처리가 완료된 결과물(Markdown, 이미지)이 저장됩니다.
- `archive/`: 과거의 스크립트와 데이터 파일들이 보관되는 아카이브 폴더입니다.

## 주요 스크립트 및 사용법

### 1. PDF 분할 (`split_pdf.py`)
원본 PDF 파일을 일정한 페이지 단위(기본 30페이지)로 분할합니다.

```powershell
python split_pdf.py data/input/your-file.pdf --output_dir data/chunks/your-file --chunk_size 10
```
- `file_path`: (필수) 원본 PDF 경로
- `--output_dir`: 분할된 파일이 저장될 디렉토리 (기본: `data/chunks`)
- `--chunk_size`: 분할할 페이지 수 (기본: 30)

### 2. OCR 일괄 처리 (`batch_process_pdfs.py`)
분할된 PDF 또는 이미지 파일들을 외부 layout-parsing API를 통해 처리합니다.

```powershell
python batch_process_pdfs.py
```
> [!NOTE]
> 현재 `batch_process_pdfs.py` 내의 `INPUT_DIR`와 `OUTPUT_ROOT` 변수가 `data/chunks/design-parsed`와 `data/output/design-parsed`로 설정되어 있습니다. 다른 파일을 처리하려면 스크립트 내의 경로를 수정하거나 명령행 인자를 사용하세요.

## 주의 사항 (네트워크 및 보안)

### SSL 인증서 문제
로컬 환경의 인증서 문제로 인해 API 호출 시 SSL 검증을 건너뛰도록 설정되어 있습니다 (`verify=False`).

### 방화벽 문제
현재 외부 API 도메인(`oeocy5w7q4f7ufe1.aistudio-app.com`)이 사내 방화벽(FortiGuard)에 의해 "Newly Observed Domain"으로 분류되어 차단될 수 있습니다. 정상적인 처리를 위해서는 해당 도메인의 화이트리스트 등록이 필요할 수 있습니다.
