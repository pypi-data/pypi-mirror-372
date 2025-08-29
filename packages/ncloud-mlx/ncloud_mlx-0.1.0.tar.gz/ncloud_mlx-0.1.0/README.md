# ML expert Platform CLI

이 프로젝트는 ML expert Platform를 위한 Python CLI, SDK를 제공합니다.

## 설치

```sh
# ML expert Platform CLI만 설치 (기본)
pip install ncloud-mlx

# ML expert Platform CLI + Model Registry
pip install ncloud-mlx[model-registry]

# ML expert Platform CLI + Data Manager
pip install ncloud-mlx[data-manager]

# ML expert Platform CLI + 모든 확장 (Model Registry + Data Manager)
pip install ncloud-mlx[all]
```

## 기본 사용법

### 설정 관리

ML expert Platform CLI 설정을 구성하거나 확인할 수 있습니다:

```bash
# 설정 구성
$ mlx configure
Endpoint: https://clustername.mlxp.ncloud.com  # 사용하는 mlxp endpoint
Workspace name: my-workspace                   # 사용할 Workspace
Project name: my-project                       # 사용할 Project
API Key: your-api-key-here                     # 발급받은 API key

# 현재 설정 상태 확인
$ mlx status
```

### 도움말

```sh
# 전체 명령어 도움말
mlx --help

# 특정 명령어 도움말
mlx configure --help
mlx status --help
```

### 버전 확인

```sh
mlx --version
```

### 디버그 모드

문제가 발생했을 때 자세한 정보를 확인할 수 있습니다:

```sh
mlx --debug <명령어>
```
