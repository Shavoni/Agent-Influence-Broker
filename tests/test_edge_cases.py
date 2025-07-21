"""Edge case and error handling tests."""

from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest

from app.core.exceptions import BusinessLogicError, DatabaseError, ValidationError
from app.services.agent_service import AgentService
from app.services.negotiation_service import NegotiationService


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_agent_with_extremely_long_name(self):
        """Test agent creation with extremely long name."""
        agent_service = AgentService()

        # Test with name at the boundary (255 characters)
        long_name = "A" * 255

        with patch.object(agent_service, "db") as mock_db:
            mock_db.create_agent.side_effect = ValidationError("Name too long")

            with pytest.raises(ValidationError, match="Name too long"):
                await agent_service.create_agent(
                    {"name": long_name, "description": "Test", "capabilities": []}
                )

    @pytest.mark.asyncio
    async def test_negotiation_with_circular_reference(self):
        """Test negotiation where agent tries to negotiate with itself."""
        negotiation_service = NegotiationService()

        with patch.object(negotiation_service, "db") as mock_db:
            mock_db.create_negotiation.side_effect = BusinessLogicError(
                "Agent cannot negotiate with itself"
            )

            with pytest.raises(
                BusinessLogicError, match="cannot negotiate with itself"
            ):
                await negotiation_service.create_negotiation(
                    {
                        "initiator_id": "agent-123",
                        "respondent_id": "agent-123",  # Same agent
                        "terms": {"price": 1000},
                    }
                )

    @pytest.mark.asyncio
    async def test_influence_calculation_with_no_data(self):
        """Test influence calculation for agent with no activity."""
        from app.services.influence_service import InfluenceService

        influence_service = InfluenceService()

        with patch.object(influence_service, "db") as mock_db:
            mock_db.get_agent_metrics.return_value = {
                "successful_negotiations": 0,
                "total_negotiations": 0,
                "average_deal_value": 0.0,
                "network_connections": 0,
            }

            result = await influence_service.calculate_influence_score("agent-new")

            # New agent should have base influence score
            assert result["influence_score"] == 0.0
            assert result["metrics"]["total_negotiations"] == 0

    @pytest.mark.asyncio
    async def test_concurrent_agent_updates_race_condition(self):
        """Test race condition in concurrent agent updates."""
        agent_service = AgentService()

        async def update_reputation(score: float):
            """Update agent reputation score."""
            with patch.object(agent_service, "db") as mock_db:
                # Simulate race condition
                if score > 90.0:
                    mock_db.update_agent.side_effect = DatabaseError(
                        "Concurrent update conflict"
                    )
                else:
                    mock_db.update_agent.return_value = {"reputation_score": score}

                return await agent_service.update_agent_reputation("agent-123", score)

        # Test concurrent updates
        tasks = [
            update_reputation(85.0),
            update_reputation(92.0),  # This should fail
            update_reputation(88.0),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check that some operations succeeded and some failed
        successful_results = [r for r in results if not isinstance(r, Exception)]
        failed_results = [r for r in results if isinstance(r, Exception)]

        assert len(successful_results) >= 1
        assert len(failed_results) >= 1

    @pytest.mark.asyncio
    async def test_database_timeout_handling(self):
        """Test handling of database timeout scenarios."""
        agent_service = AgentService()

        with patch.object(agent_service, "db") as mock_db:
            import asyncio

            async def slow_operation():
                await asyncio.sleep(5)  # Simulate slow query
                return {"id": "agent-123"}

            mock_db.get_agent_by_id.side_effect = slow_operation

            # Test with timeout
            with pytest.raises(asyncio.TimeoutError):
                await asyncio.wait_for(
                    agent_service.get_agent_by_id("agent-123"), timeout=2.0
                )

    @pytest.mark.asyncio
    async def test_malformed_json_in_terms(self):
        """Test handling of malformed JSON in negotiation terms."""
        negotiation_service = NegotiationService()

        with patch.object(negotiation_service, "db") as mock_db:
            mock_db.create_negotiation.side_effect = ValidationError(
                "Invalid terms format"
            )

            with pytest.raises(ValidationError, match="Invalid terms format"):
                await negotiation_service.create_negotiation(
                    {
                        "initiator_id": "agent-123",
                        "respondent_id": "agent-456",
                        "terms": "invalid_json_string",  # Should be dict
                    }
                )
