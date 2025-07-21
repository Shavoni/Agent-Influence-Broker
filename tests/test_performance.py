"""Performance and load testing for the Agent Influence Broker."""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

import pytest

from app.services.agent_service import AgentService
from app.services.negotiation_service import NegotiationService


class TestPerformanceMetrics:
    """Test performance characteristics of core services."""

    @pytest.mark.asyncio
    async def test_agent_creation_performance(self):
        """Test agent creation performance under load."""
        agent_service = AgentService()

        async def create_test_agent(index: int):
            """Create a single test agent."""
            with patch.object(agent_service, "db") as mock_db:
                mock_db.create_agent.return_value = {
                    "id": f"agent-{index}",
                    "name": f"Agent{index}",
                    "status": "active",
                }
                return await agent_service.create_agent(
                    {
                        "name": f"Agent{index}",
                        "description": f"Test agent {index}",
                        "capabilities": ["negotiation"],
                    }
                )

        # Test creating 50 agents concurrently
        start_time = time.time()
        tasks = [create_test_agent(i) for i in range(50)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        # Performance assertions
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) == 50
        assert (end_time - start_time) < 10.0  # Should complete within 10 seconds

    @pytest.mark.asyncio
    async def test_negotiation_throughput(self):
        """Test negotiation creation throughput."""
        negotiation_service = NegotiationService()

        async def create_test_negotiation(index: int):
            """Create a single test negotiation."""
            with patch.object(negotiation_service, "db") as mock_db:
                mock_db.create_negotiation.return_value = {
                    "id": f"neg-{index}",
                    "status": "pending",
                }
                return await negotiation_service.create_negotiation(
                    {
                        "initiator_id": f"agent-{index}",
                        "respondent_id": "agent-target",
                        "terms": {"price": 1000 + index},
                    }
                )

        # Test creating 100 negotiations with controlled concurrency
        semaphore = asyncio.Semaphore(10)  # Limit to 10 concurrent operations

        async def limited_create(index: int):
            async with semaphore:
                return await create_test_negotiation(index)

        start_time = time.time()
        tasks = [limited_create(i) for i in range(100)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        # Throughput assertions
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) >= 90  # At least 90% success rate
        throughput = len(successful_results) / (end_time - start_time)
        assert throughput > 5.0  # At least 5 negotiations per second

    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self):
        """Test memory usage during high-load operations."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Simulate high load
        agent_service = AgentService()

        async def memory_intensive_operation():
            """Perform memory-intensive operations."""
            with patch.object(agent_service, "db") as mock_db:
                # Simulate large data processing
                large_data = [
                    {"id": f"agent-{i}", "data": "x" * 1000} for i in range(1000)
                ]
                mock_db.bulk_create_agents.return_value = large_data
                return await agent_service.bulk_create_agents(large_data)

        # Run multiple memory-intensive operations
        tasks = [memory_intensive_operation() for _ in range(10)]
        await asyncio.gather(*tasks, return_exceptions=True)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory usage should not increase by more than 100MB
        assert memory_increase < 100, f"Memory increased by {memory_increase:.2f}MB"
