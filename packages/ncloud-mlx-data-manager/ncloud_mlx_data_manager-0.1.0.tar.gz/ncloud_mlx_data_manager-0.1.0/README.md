# ML expert Platform Data Manager SDK

ML expert Platform Data Manager SDK는 **Naver Cloud Platform의 ML expert Platform Data Manager**와 호환되는 데이터셋 관리 라이브러리입니다. 이 SDK는 **Hugging Face Datasets API와 완벽하게 호환**되어 기존 Hugging Face 워크플로우를 그대로 사용할 수 있습니다.

## 🚀 주요 특징

- **🤗 Hugging Face Datasets 호환**: 기존 Hugging Face Datasets API와 동일한 인터페이스 제공
- **☁️ ML expert Platform Data Manager 연동**: Naver Cloud Platform의 ML expert Platform Data Manager와 완벽 연동
- **📊 다양한 데이터 형식 지원**: CSV, JSON, Parquet, 이미지, 오디오, 텍스트 등 모든 형식 지원
- **⚡ 효율적인 스트리밍**: 대용량 데이터셋도 메모리 효율적으로 처리
- **🔄 간편한 데이터 전처리**: map, filter, select 등 강력한 데이터 변환 기능
- **🔐 보안**: 안전한 API 키 기반 인증 시스템

## 📦 설치

### pip을 사용한 설치

```bash
pip install ncloud-mlx[data-manager]
```

## ⚙️ 환경 설정

ML expert Platform Data Manager SDK를 사용하기 전에 다음 환경변수를 설정해야 합니다:

```bash
# ML expert Platform Data Manager 엔드포인트 설정
export MLX_ENDPOINT_URL="your-mlx-endpoint-url"

# API 키 설정
export MLX_APIKEY="your-api-key-here"
```

## 🏃‍♂️ 빠른 시작

### 기본 사용법

```python
from mlx.sdk.data import load_dataset, login
from datasets import concatenate_datasets

# ML expert Platform Data Manager에 로그인
login("your-api-key")

# 로컬 데이터셋 로드
local_dataset = load_dataset("./path/to/your/data")

# ML expert Platform Data Manager에서 데이터셋 로드
remote_dataset = load_dataset("mlx-data-manager/dataset-name")

# 데이터셋 결합
combined_dataset = concatenate_datasets([
    local_dataset["train"], 
    remote_dataset["train"]
])

# ML expert Platform Data Manager에 업로드
combined_dataset.push_to_hub("mlx-data-manager/new-dataset")
```

### 스트리밍 모드

대용량 데이터셋을 효율적으로 처리하려면 스트리밍 모드를 사용하세요:

```python
from mlx.sdk.data import load_dataset

# 스트리밍 모드로 데이터셋 로드
dataset = load_dataset("mlx-data-manager/large-dataset", streaming=True)

# 데이터를 즉시 반복 처리
for example in dataset["train"]:
    print(example)
    break  # 첫 번째 예제만 출력
```

### 데이터 전처리

```python
from mlx.sdk.data import load_dataset
from transformers import AutoTokenizer

# 데이터셋 로드
dataset = load_dataset("mlx-data-manager/text-dataset")

# 텍스트 길이 추가
dataset_with_length = dataset.map(
    lambda x: {"length": len(x["text"])}
)

# 토크나이제이션
tokenizer = AutoTokenizer.from_pretrained('bert-base-cased')
tokenized_dataset = dataset.map(
    lambda x: tokenizer(x['text']), 
    batched=True
)
```

## 📖 지원하는 데이터 형식

ML expert Platform Data Manager SDK는 다양한 데이터 형식을 지원합니다:

- **텍스트**: CSV, JSON, TXT, Parquet
- **이미지**: JPEG, PNG, WebP, TIFF
- **오디오**: WAV, MP3, FLAC
- **비디오**: MP4, AVI, MOV
- **기타**: Arrow, Feather, Excel

## 🔧 고급 기능

### 데이터셋 설정 및 분할

```python
from datasets import get_dataset_config_names, get_dataset_split_names

# 사용 가능한 설정 확인
configs = get_dataset_config_names("mlx-data-manager/dataset-name")
print(f"Available configs: {configs}")

# 사용 가능한 분할 확인
splits = get_dataset_split_names("mlx-data-manager/dataset-name")
print(f"Available splits: {splits}")
```

### 태그 및 버전 관리

```python
from huggingface_hub import create_tag, list_repo_refs

# 태그 생성
create_tag(
    repo_id="mlx-data-manager/dataset-name",
    repo_type="dataset",
    tag="v1.0",
    tag_message="First stable release"
)

# 태그 목록 확인
refs = list_repo_refs(repo_id="mlx-data-manager/dataset-name", repo_type="dataset")
print([tag.name for tag in refs.tags])
```

### 대용량 파일 업로드

```python
from huggingface_hub import create_repo, upload_large_folder

# 저장소 생성
create_repo(
    repo_id="mlx-data-manager/large-dataset",
    repo_type="dataset"
)

# 대용량 폴더 업로드
upload_large_folder(
    repo_id="mlx-data-manager/large-dataset",
    repo_type="dataset",
    folder_path="./path/to/large/dataset"
)
```

## 🔍 데이터셋 검색

```python
from huggingface_hub import list_datasets

# 데이터셋 검색
datasets = list_datasets(search="keyword")
for dataset in datasets:
    print(f"Dataset: {dataset.id}")
```

## 📊 지원하는 ML 프레임워크

ML expert Platform Data Manager SDK는 다음 ML 프레임워크와 완벽하게 호환됩니다:

- **PyTorch** (2.0+)
- **TensorFlow** (2.6+)
- **JAX** (3.14+)
- **NumPy**
- **Pandas**
- **Polars**

```python
# PyTorch DataLoader와 함께 사용
from torch.utils.data import DataLoader

dataset = load_dataset("mlx-data-manager/dataset-name")
dataloader = DataLoader(dataset["train"], batch_size=32)

# Pandas DataFrame으로 변환
df = dataset["train"].to_pandas()
```

## 🛠️ 문제 해결

### 일반적인 문제들

1. **환경변수 설정 오류**
   ```bash
   # 환경변수가 제대로 설정되었는지 확인
   echo $MLX_ENDPOINT_URL
   echo $MLX_APIKEY
   ```

2. **캐시 정리**
   ```shell
   $ rm -rf ~/.cache
   ```

3. **네트워크 연결 문제**
   - 방화벽 설정 확인
   - ML expert Platform Data Manager 엔드포인트 접근 가능 여부 확인

## 📄 라이선스

이 프로젝트는 [Apache License 2.0](LICENSE) 하에 라이선스가 부여됩니다.

## 🔗 관련 프로젝트

- [Hugging Face Datasets](https://github.com/huggingface/datasets)
- [Hugging Face Hub](https://github.com/huggingface/huggingface_hub)

---

ML expert Platform Data Manager SDK로 더 효율적인 데이터셋 관리를 시작하세요! 🚀
