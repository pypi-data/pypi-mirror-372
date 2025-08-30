"""Integration tests for the models endpoint."""

from pathlib import Path
from unittest import mock

import pytest
from httpx import AsyncClient

LLMS_URL = "/models/llms"
IMAGE_MODELS_URL = "/models/images"


@pytest.mark.asyncio
async def test_get_models(registry_api_client: AsyncClient) -> None:
    """Test retrieving all LLMs."""
    response = await registry_api_client.get(LLMS_URL)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    for llm in data:
        assert isinstance(llm, dict)
        assert "id" in llm
        assert "name" in llm
        assert "provider" in llm
        assert "costs" in llm
        assert "capabilities" in llm
        assert "context_window" in llm

        provider = llm["provider"]
        assert "id" in provider
        assert "name" in provider


@pytest.mark.asyncio
async def test_get_model_by_id(registry_api_client: AsyncClient) -> None:
    """Test retrieving a specific LLM by ID."""
    # First get all LLMs
    response = await registry_api_client.get(LLMS_URL)
    assert response.status_code == 200

    llms = response.json()
    assert len(llms) > 0
    test_llm = llms[0]

    # Test API response for specific LLM
    response = await registry_api_client.get(f"{LLMS_URL}/{test_llm['id']}")
    assert response.status_code == 200

    llm = response.json()
    assert llm["id"] == test_llm["id"]
    assert llm["name"] == test_llm["name"]
    assert llm["provider"]["id"] == test_llm["provider"]["id"]

    # Test with non-existent LLM
    response = await registry_api_client.get(f"{LLMS_URL}/non-existent-llm")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_model_schema(registry_api_client: AsyncClient) -> None:
    """Test that the LLM schema validation works correctly."""
    # Get LLMs to verify schema
    response = await registry_api_client.get(LLMS_URL)
    assert response.status_code == 200

    llms = response.json()
    assert len(llms) > 0

    # Attempt to validate LLM structure using Pydantic
    for llm_data in llms:
        # We can't directly validate here, but we should check key fields
        assert isinstance(llm_data["id"], str)
        assert isinstance(llm_data["name"], str)

        # Check costs structure
        costs = llm_data["costs"]
        assert any(k.startswith("input_") for k in costs)
        assert any(k.startswith("output_") for k in costs)

        # Check capabilities structure
        capabilities = llm_data["capabilities"]
        if capabilities:
            assert all(k.startswith("supports_") for k in capabilities)

        # Check context window
        context = llm_data["context_window"]
        assert "max_input_tokens" in context
        assert "max_output_tokens" in context


@pytest.mark.asyncio
async def test_models_api_works_without_env_file(
    registry_api_client: AsyncClient,
) -> None:
    """Test that the LLMs API endpoints work without env files."""
    # Make Path.exists return False for .env files
    with mock.patch.object(Path, "exists") as mock_exists:

        def side_effect(path):
            # Return False for .env files, True for everything else
            return ".env" not in str(path)

        mock_exists.side_effect = side_effect

        # Test the LLMs route still returns successfully
        response = await registry_api_client.get(LLMS_URL)
        assert response.status_code == 200

        # Test that we can get one of the LLMs by ID
        llms = response.json()
        assert llms, "No LLMs found in registry"
        test_llm = llms[0]
        llm_id = test_llm["id"]

        response = await registry_api_client.get(f"{LLMS_URL}/{llm_id}")
        assert response.status_code == 200
        assert response.json()["id"] == llm_id


# Image model tests


@pytest.mark.asyncio
async def test_get_image_models(registry_api_client: AsyncClient) -> None:
    """Test retrieving all image models."""
    response = await registry_api_client.get(IMAGE_MODELS_URL)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    for model in data:
        assert isinstance(model, dict)
        assert "id" in model
        assert "name" in model
        assert "provider" in model
        assert "costs" in model
        assert "updated_dt" in model

        provider = model["provider"]
        assert "id" in provider
        assert "name" in provider

        costs = model["costs"]
        assert "image_generation" in costs
        image_generation = costs["image_generation"]

        # Verify exactly one pricing model is set (as per validation)
        pricing_models = [
            image_generation.get("flat_rate"),
            image_generation.get("quality_tiers"),
            image_generation.get("cost_per_megapixel"),
            image_generation.get("cost_per_second"),
        ]
        assert sum(p is not None for p in pricing_models) == 1


@pytest.mark.asyncio
async def test_get_image_model_by_id(registry_api_client: AsyncClient) -> None:
    """Test retrieving a specific image model by ID."""
    # First get all image models
    response = await registry_api_client.get(IMAGE_MODELS_URL)
    assert response.status_code == 200

    models = response.json()
    assert len(models) > 0
    test_model = models[0]

    # Test API response for specific image model
    response = await registry_api_client.get(f"{IMAGE_MODELS_URL}/{test_model['id']}")
    assert response.status_code == 200

    model = response.json()
    assert model["id"] == test_model["id"]
    assert model["name"] == test_model["name"]
    assert model["provider"]["id"] == test_model["provider"]["id"]

    # Test with non-existent image model
    response = await registry_api_client.get(
        f"{IMAGE_MODELS_URL}/non-existent-image-model"
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_image_model_schema(registry_api_client: AsyncClient) -> None:
    """Test that the image model schema validation works correctly."""
    # Get image models to verify schema
    response = await registry_api_client.get(IMAGE_MODELS_URL)
    assert response.status_code == 200

    models = response.json()
    assert len(models) > 0

    # Attempt to validate image model structure
    for model_data in models:
        # Check required fields
        assert isinstance(model_data["id"], str)
        assert isinstance(model_data["name"], str)

        # Check costs structure
        costs = model_data["costs"]
        assert "image_generation" in costs

        image_generation = costs["image_generation"]
        # Verify exactly one pricing model (business rule validation)
        pricing_models = [
            image_generation.get("flat_rate"),
            image_generation.get("quality_tiers"),
            image_generation.get("cost_per_megapixel"),
            image_generation.get("cost_per_second"),
        ]
        non_null_models = [p for p in pricing_models if p is not None]
        assert len(non_null_models) == 1, (
            f"Expected exactly 1 pricing model, got {len(non_null_models)}"
        )

        # Check provider structure
        provider = model_data["provider"]
        assert "id" in provider
        assert "name" in provider


@pytest.mark.asyncio
async def test_image_models_api_works_without_env_file(
    registry_api_client: AsyncClient,
) -> None:
    """Test that the image models API endpoints work without env files."""
    # Make Path.exists return False for .env files
    with mock.patch.object(Path, "exists") as mock_exists:

        def side_effect(path):
            # Return False for .env files, True for everything else
            return ".env" not in str(path)

        mock_exists.side_effect = side_effect

        # Test the image models route still returns successfully
        response = await registry_api_client.get(IMAGE_MODELS_URL)
        assert response.status_code == 200

        # Test that we can get one of the image models by ID
        models = response.json()
        assert models, "No image models found in registry"
        test_model = models[0]
        model_id = test_model["id"]

        response = await registry_api_client.get(f"{IMAGE_MODELS_URL}/{model_id}")
        assert response.status_code == 200
        assert response.json()["id"] == model_id
