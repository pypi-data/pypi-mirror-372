# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]


## [0.3.3] - 2025-08-26
### Added
- Added Google Nano Banana image generation model to default models


## [0.3.2] - 2025-08-26

### Added
- Support for overriding model metadata in the YAML configuration file


## [0.3.1] - 2025-08-02

### Added
- GPT-5, GPT-OSS 120b, and Claude Opus 4.1 to package default models


## [0.2.2] - 2025-08-02

### Changed
- Updated Replicate model pricing for SDXL, Imagen 4, and Easel Advanced Face Swap models


## [0.2.1] - 2025-07-11

### Added
- Support for modality-specific service defaults in LocalTransformerClient


## [0.2.0] - 2025-07-10

### Added
- Image model support:
  - Support for image generation models with new modality-based model organization
  - Support for multiple modalities in model registry (text, image)
  - New image model schemas and endpoints
  - Image model integration in client implementations
- Grok 4 language model in default models configuration

### Changed
- Refactored model registry to support multiple modalities
- Updated protocols and client implementations for multi-modality handling
- Restructured configuration to categorize models by modality
- Updated `ModelConfig` to include optional `modality` field
- Modified `ConfigSchema` to store models as dictionary keyed by modality
- Enhanced model processing methods in `RegistryConfig` and `LocalTransformerClient`
- Updated example notebooks to include image usage and new Generic signature
- Updated READMEs with image model documentation


## [0.1.9] - 2025-07-03

### Added
- Support for updating default model provider metadata in YAML mappings


## [0.1.7] - 2025-07-01

### Added
- Aded MiniMax 01 and M1 models to package default models
- Add OpenAI o3 Pro to package default models

### Fixed
- Remove `supports_tools` from MiniMax M1 on OpenRouter - OpenRouter erroneously marks the MiniMax service API as not supporting tools


## [0.1.6] - 2025-06-24

### Added
- Models merge mode support for user-defined models JSON file


## [0.1.5] - 2025-06-18

### Added
- Reasoning support to model capabilities with updated model metadata
- Service provider API format inclusion when returning transformed parameters

### Changed
- Updated default LLMs and improved configuration validation checks
- Updated default registry config with additional model configurations for reasoning variants

### Removed
- Deprecated LLMs form the default config
- Mdels that are no longer supported from the default registry JSON file


## [0.1.3] - 2025-04-09

## Fixed
- Update version bump script to include dependency constraints between the monorepo's packages


## [0.1.2] - 2025-04-09

### Added
- Version bump script and corresponding Makefile targets

### Fixed
- Load environment variables from .env file in `LocalTransformerClient` initialisation - necessary when the registry and transformer clients are running in separate processes


## [0.1.1] - 2025-04-09

### Changed
- Synchronized published package versions with the current repository state.
- Validated and tested automated release workflows (PyPI, Docker, Helm).


## [0.1.0] - 2025-04-08

### Added
- Initial public release of LangGate
- Core functionality for LLM proxy and transformation
- Python client SDK for interacting with LangGate
- Processor service for Envoy integration (incomplete)
- Envoy configuration for routing and transformation
- Server API for registry management
- Helm charts for Kubernetes deployment
- Docker images for all components

### Changed
- Migrated from private repository to open source
