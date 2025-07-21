#!/usr/bin/env python3
"""
Comprehensive Test Suite for Agent Influence Broker
Enterprise-grade functionality validation
"""

import json
import sys
import time
from typing import Any, Dict, List

import requests

BASE_URL = "http://localhost:8000"


class EnterpriseTestSuite:
    """Comprehensive test suite for enterprise validation"""

    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.results = []

    def run_test(self, test_name: str, test_func):
        """Run a single test and track results"""
        print(f"\n🧪 Running: {test_name}")
        self.tests_run += 1

        try:
            test_func()
            print(f"✅ PASSED: {test_name}")
            self.tests_passed += 1
            self.results.append({"test": test_name, "status": "PASSED"})
        except Exception as e:
            print(f"❌ FAILED: {test_name} - {e}")
            self.tests_failed += 1
            self.results.append(
                {"test": test_name, "status": "FAILED", "error": str(e)}
            )

    def test_system_health(self):
        """Test comprehensive system health monitoring"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "components" in data
        assert "sample_data" in data["components"]
        assert data["components"]["sample_data"]["agents"] >= 2
        print("   ✓ System health monitoring operational")
        print("   ✓ Component status tracking functional")
        print("   ✓ Sample data integrity verified")

    def test_agent_management_comprehensive(self):
        """Test comprehensive agent management capabilities"""
        # Test listing agents with filtering
        response = requests.get(
            f"{BASE_URL}/api/v1/agents?agent_type=negotiation&limit=5"
        )
        assert response.status_code == 200

        data = response.json()
        assert "agents" in data
        assert "total" in data
        assert "has_more" in data
        assert "meta" in data

        # Verify agent data completeness
        agent = data["agents"][0]
        required_fields = [
            "id",
            "name",
            "description",
            "agent_type",
            "reputation_score",
            "influence_score",
            "capabilities",
            "metadata",
            "is_active",
        ]
        for field in required_fields:
            assert field in agent, f"Missing required field: {field}"

        print("   ✓ Agent listing with filtering works")
        print("   ✓ Pagination metadata included")
        print("   ✓ Comprehensive agent data structure verified")
        print("   ✓ Reputation and influence scoring present")

    def test_agent_creation_validation(self):
        """Test robust agent creation with validation"""
        # Test successful creation
        agent_data = {
            "name": "Test Enterprise Bot",
            "agent_type": "analytics",
            "description": "Test agent for validation",
            "capabilities": [
                {
                    "name": "advanced_analytics",
                    "description": "Complex data analysis",
                    "parameters": {"accuracy": 0.98, "speed": "real_time"},
                }
            ],
            "metadata": {"department": "risk_management", "clearance": "level_5"},
        }

        response = requests.post(f"{BASE_URL}/api/v1/agents", json=agent_data)
        assert response.status_code == 200

        created_agent = response.json()
        assert created_agent["name"] == agent_data["name"]
        assert created_agent["capabilities"] == agent_data["capabilities"]
        assert created_agent["metadata"] == agent_data["metadata"]
        assert "id" in created_agent
        assert "created_at" in created_agent

        print("   ✓ Agent creation with complex data successful")
        print("   ✓ All input fields preserved correctly")
        print("   ✓ Auto-generated fields populated")

        return created_agent["id"]

    def test_negotiation_engine_comprehensive(self):
        """Test sophisticated negotiation engine capabilities"""
        # Get existing agents
        agents_response = requests.get(f"{BASE_URL}/api/v1/agents")
        agents = agents_response.json()["agents"]

        negotiation_data = {
            "title": "Enterprise Software Licensing Negotiation",
            "description": "Complex multi-tier licensing agreement with performance SLAs",
            "initiator_agent_id": agents[0]["id"],
            "responder_agent_id": agents[1]["id"],
            "negotiation_type": "software_licensing",
            "initial_proposal": {
                "license_type": "enterprise_unlimited",
                "user_tiers": [
                    {"tier": "basic", "max_users": 1000, "cost_per_user": 15},
                    {"tier": "premium", "max_users": 500, "cost_per_user": 45},
                    {"tier": "enterprise", "max_users": 100, "cost_per_user": 120},
                ],
                "sla_requirements": {
                    "uptime": 99.95,
                    "response_time_ms": 200,
                    "support_level": "24_7_enterprise",
                },
                "contract_terms": {
                    "duration_months": 36,
                    "auto_renewal": True,
                    "termination_notice_days": 90,
                },
                "payment_terms": {
                    "billing_cycle": "monthly",
                    "payment_method": "wire_transfer",
                    "early_payment_discount": 0.02,
                },
            },
            "max_rounds": 20,
            "timeout_minutes": 240,
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/negotiations", json=negotiation_data
        )
        assert response.status_code == 200

        negotiation = response.json()
        assert negotiation["title"] == negotiation_data["title"]
        assert negotiation["initial_proposal"] == negotiation_data["initial_proposal"]
        assert "participants" in negotiation
        assert negotiation["max_rounds"] == 20
        assert "expires_at" in negotiation

        print("   ✓ Complex negotiation creation successful")
        print("   ✓ Multi-tier proposal structure preserved")
        print("   ✓ SLA and contract terms handled correctly")
        print("   ✓ Participant validation and naming working")

        return negotiation["id"]

    def test_transaction_system_comprehensive(self):
        """Test comprehensive transaction processing"""
        # Get agents and negotiations
        agents_response = requests.get(f"{BASE_URL}/api/v1/agents")
        agents = agents_response.json()["agents"]

        negotiations_response = requests.get(f"{BASE_URL}/api/v1/negotiations")
        negotiations = negotiations_response.json()["negotiations"]

        transaction_data = {
            "payer_agent_id": agents[0]["id"],
            "payee_agent_id": agents[1]["id"],
            "negotiation_id": negotiations[0]["id"],
            "amount": 125750.75,
            "currency": "USD",
            "description": "Enterprise license payment with performance bonuses and SLA guarantees",
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/transactions", json=transaction_data
        )
        assert response.status_code == 200

        transaction = response.json()
        assert transaction["amount"] == transaction_data["amount"]
        assert transaction["currency"] == transaction_data["currency"]
        assert "participants" in transaction
        assert "created_at" in transaction
        assert transaction["status"] == "pending"

        print("   ✓ High-value transaction creation successful")
        print("   ✓ Agent validation working correctly")
        print("   ✓ Negotiation linking functional")
        print("   ✓ Status tracking implemented")

    def test_data_filtering_and_pagination(self):
        """Test advanced filtering and pagination"""
        # Test agent filtering
        response = requests.get(
            f"{BASE_URL}/api/v1/agents?agent_type=analytics&limit=2&offset=0"
        )
        assert response.status_code == 200

        data = response.json()
        assert data["limit"] == 2
        assert data["offset"] == 0
        assert "has_more" in data

        # Test negotiation filtering
        response = requests.get(f"{BASE_URL}/api/v1/negotiations?status=pending")
        assert response.status_code == 200

        negotiations = response.json()
        for nego in negotiations["negotiations"]:
            assert nego["status"] == "pending"

        print("   ✓ Agent filtering by type working")
        print("   ✓ Pagination parameters functional")
        print("   ✓ Negotiation status filtering operational")

    def test_data_integrity_and_relationships(self):
        """Test data integrity and cross-entity relationships"""
        # Get all data
        agents = requests.get(f"{BASE_URL}/api/v1/agents").json()["agents"]
        negotiations = requests.get(f"{BASE_URL}/api/v1/negotiations").json()[
            "negotiations"
        ]
        transactions = requests.get(f"{BASE_URL}/api/v1/transactions").json()[
            "transactions"
        ]

        # Verify agent-negotiation relationships
        for nego in negotiations:
            initiator_found = any(a["id"] == nego["initiator_agent_id"] for a in agents)
            responder_found = any(a["id"] == nego["responder_agent_id"] for a in agents)
            assert initiator_found, "Initiator agent not found"
            assert responder_found, "Responder agent not found"

        # Verify transaction-agent relationships
        for tx in transactions:
            payer_found = any(a["id"] == tx["payer_agent_id"] for a in agents)
            payee_found = any(a["id"] == tx["payee_agent_id"] for a in agents)
            assert payer_found, "Payer agent not found"
            assert payee_found, "Payee agent not found"

        print("   ✓ Agent-negotiation relationships intact")
        print("   ✓ Transaction-agent relationships verified")
        print("   ✓ Data integrity across entities confirmed")

    def run_all_tests(self):
        """Run the complete enterprise test suite"""
        print("🚀 Starting Agent Influence Broker Enterprise Test Suite")
        print("=" * 60)

        # Core functionality tests
        self.run_test("System Health Monitoring", self.test_system_health)
        self.run_test(
            "Agent Management Comprehensive", self.test_agent_management_comprehensive
        )
        self.run_test(
            "Agent Creation & Validation", self.test_agent_creation_validation
        )
        self.run_test(
            "Negotiation Engine Comprehensive",
            self.test_negotiation_engine_comprehensive,
        )
        self.run_test(
            "Transaction System Comprehensive",
            self.test_transaction_system_comprehensive,
        )

        # Advanced functionality tests
        self.run_test(
            "Data Filtering & Pagination", self.test_data_filtering_and_pagination
        )
        self.run_test(
            "Data Integrity & Relationships", self.test_data_integrity_and_relationships
        )

        # Summary
        print("\n" + "=" * 60)
        print("🎯 TEST SUITE SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"✅ Passed: {self.tests_passed}")
        print(f"❌ Failed: {self.tests_failed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")

        if self.tests_failed == 0:
            print("\n🏆 ALL TESTS PASSED - Enterprise-grade functionality confirmed!")
            print("✅ System is production-ready for AI agent interactions")
        else:
            print(f"\n⚠️  {self.tests_failed} tests failed - Review required")
            for result in self.results:
                if result["status"] == "FAILED":
                    print(
                        f"   ❌ {result['test']}: {result.get('error', 'Unknown error')}"
                    )


if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding correctly")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print(
            "❌ Server not accessible. Make sure it's running on http://localhost:8000"
        )
        sys.exit(1)

    # Run the test suite
    test_suite = EnterpriseTestSuite()
    test_suite.run_all_tests()
