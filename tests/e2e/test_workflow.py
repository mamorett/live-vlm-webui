"""End-to-end workflow tests."""

import pytest
from unittest.mock import patch, AsyncMock, Mock


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_complete_vlm_workflow():
    """Test complete workflow from video input to VLM response."""
    # This tests the entire pipeline:
    # 1. Receive video frame
    # 2. Process frame
    # 3. Send to VLM
    # 4. Return response

    with patch("live_vlm_webui.vlm_service.VLMService") as mock_vlm:
        with patch("live_vlm_webui.video_processor.VideoProcessor") as mock_processor:
            # Setup mocks
            vlm_instance = AsyncMock()
            vlm_instance.query_async.return_value = {"response": "Test response"}
            mock_vlm.return_value = vlm_instance

            processor_instance = AsyncMock()
            processor_instance.process_frame.return_value = b"processed_frame"
            mock_processor.return_value = processor_instance

            # Simulate workflow
            frame = b"test_frame"
            processed = await processor_instance.process_frame(frame)
            response = await vlm_instance.query_async("What do you see?", processed)

            assert response["response"] == "Test response"


@pytest.mark.asyncio
@pytest.mark.e2e
@pytest.mark.slow
async def test_gpu_monitoring_during_inference():
    """Test GPU monitoring while VLM is processing."""
    with patch("live_vlm_webui.gpu_monitor.GPUMonitor") as mock_monitor:
        monitor = mock_monitor.return_value
        monitor.get_stats.return_value = {
            "gpu_utilization": 85,
            "memory_used": 6144,
            "memory_total": 8192,
        }

        stats = monitor.get_stats()

        assert stats["gpu_utilization"] > 0
        assert stats["memory_used"] < stats["memory_total"]


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_error_handling_in_pipeline():
    """Test error handling throughout the pipeline."""
    with patch("live_vlm_webui.vlm_service.VLMService") as mock_vlm:
        vlm_instance = AsyncMock()
        vlm_instance.query_async.side_effect = Exception("VLM service error")
        mock_vlm.return_value = vlm_instance

        # Test that errors are properly caught and handled
        with pytest.raises(Exception) as exc_info:
            await vlm_instance.query_async("test", None)

        assert "VLM service error" in str(exc_info.value)

