"""
In-Memory Data Store for Agent Influence Broker
Real functionality without external dependencies
"""

import json
import threading
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


class AgentType(Enum):
    TRADING = "trading"
    NEGOTIATION = "negotiation"
    INFLUENCE = "influence"
    SERVICE = "service"
    ANALYTICS = "analytics"


class NegotiationStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


@dataclass
class Agent:
    id: str
    name: str
    description: str
    agent_type: AgentType
    owner_id: str
    capabilities: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    reputation_score: float = 0.0
    influence_score: float = 0.0
    success_rate: float = 0.0
    total_negotiations: int = 0
    successful_negotiations: int = 0
    is_active: bool = True
    is_verified: bool = False
    api_endpoint: Optional[str] = None
    webhook_url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_active: Optional[datetime] = None

    def to_dict(self):
        data = asdict(self)
        # Convert datetime objects to ISO strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat() + "Z"
            elif isinstance(value, AgentType):
                data[key] = value.value
        return data

    def update_reputation(self, negotiation_successful: bool):
        """Update agent reputation based on negotiation outcome"""
        self.total_negotiations += 1
        if negotiation_successful:
            self.successful_negotiations += 1

        self.success_rate = (
            self.successful_negotiations / self.total_negotiations
            if self.total_negotiations > 0
            else 0
        )
        self.reputation_score = min(self.success_rate * 100, 100)
        self.influence_score = min(
            self.reputation_score + (self.total_negotiations * 0.5), 100
        )
        self.updated_at = datetime.utcnow()


@dataclass
class Negotiation:
    id: str
    title: str
    description: str
    initiator_agent_id: str
    responder_agent_id: str
    negotiation_type: str
    status: NegotiationStatus = NegotiationStatus.PENDING
    initial_proposal: Dict[str, Any] = field(default_factory=dict)
    current_terms: Optional[Dict[str, Any]] = None
    final_agreement: Optional[Dict[str, Any]] = None
    max_rounds: int = 10
    current_round: int = 0
    timeout_minutes: int = 60
    outcome: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    def to_dict(self):
        data = asdict(self)
        # Convert datetime objects to ISO strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat() + "Z" if value else None
            elif isinstance(value, NegotiationStatus):
                data[key] = value.value
        return data


@dataclass
class Transaction:
    id: str
    payer_agent_id: str
    payee_agent_id: str
    negotiation_id: Optional[str]
    amount: float
    original_amount: Optional[float] = None  # For savings calculation
    currency: str = "CREDITS"
    status: str = "pending"
    description: str = ""
    savings_amount: float = 0.0  # Amount saved through negotiation
    savings_percentage: float = 0.0  # Percentage saved
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        """Calculate savings if original amount is provided"""
        if self.original_amount and self.original_amount > self.amount:
            self.savings_amount = self.original_amount - self.amount
            self.savings_percentage = (self.savings_amount / self.original_amount) * 100

    def to_dict(self):
        data = asdict(self)
        # Convert datetime objects to ISO strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat() + "Z" if value else None
        return data


class InMemoryDataStore:
    """Thread-safe in-memory data store for development"""

    def __init__(self):
        self._lock = threading.RLock()
        self.agents: Dict[str, Agent] = {}
        self.negotiations: Dict[str, Negotiation] = {}
        self.transactions: Dict[str, Transaction] = {}
        self._initialize_sample_data()

    def _initialize_sample_data(self):
        """Initialize with some realistic sample data"""
        # Create sample agents
        agent1 = Agent(
            id=str(uuid.uuid4()),
            name="AlgoTrader Pro",
            description="Advanced algorithmic trading agent with machine learning capabilities",
            agent_type=AgentType.TRADING,
            owner_id="user_001",
            capabilities=[
                {
                    "name": "market_analysis",
                    "description": "Real-time market analysis",
                    "parameters": {"timeframe": "1h"},
                },
                {
                    "name": "risk_management",
                    "description": "Portfolio risk assessment",
                    "parameters": {"max_risk": 0.05},
                },
            ],
            reputation_score=92.5,
            influence_score=88.3,
            success_rate=0.925,
            total_negotiations=12,
            successful_negotiations=11,
            is_verified=True,
            api_endpoint="https://api.algotrader.ai/v1",
            last_active=datetime.utcnow() - timedelta(minutes=5),
        )

        agent2 = Agent(
            id=str(uuid.uuid4()),
            name="NegotiBot Elite",
            description="Sophisticated negotiation agent for complex multi-party agreements",
            agent_type=AgentType.NEGOTIATION,
            owner_id="user_002",
            capabilities=[
                {
                    "name": "multi_party_negotiation",
                    "description": "Handle complex negotiations",
                    "parameters": {"max_parties": 5},
                },
                {
                    "name": "sentiment_analysis",
                    "description": "Analyze negotiation sentiment",
                    "parameters": {"model": "transformer"},
                },
            ],
            reputation_score=96.1,
            influence_score=94.7,
            success_rate=0.961,
            total_negotiations=8,
            successful_negotiations=8,
            is_verified=True,
            webhook_url="https://webhook.negotibot.io/events",
            last_active=datetime.utcnow() - timedelta(minutes=2),
        )

        agent3 = Agent(
            id=str(uuid.uuid4()),
            name="DataSync Analytics",
            description="Enterprise data aggregation and analytics agent",
            agent_type=AgentType.ANALYTICS,
            owner_id="user_003",
            capabilities=[
                {
                    "name": "data_aggregation",
                    "description": "Aggregate data from multiple sources",
                    "parameters": {"sources": ["market", "social", "news"]},
                },
                {
                    "name": "predictive_modeling",
                    "description": "Generate predictive models",
                    "parameters": {"accuracy": 0.89},
                },
            ],
            reputation_score=89.3,
            influence_score=91.2,
            success_rate=0.893,
            total_negotiations=15,
            successful_negotiations=13,
            is_verified=True,
            api_endpoint="https://api.datasync.io/v2",
            last_active=datetime.utcnow() - timedelta(minutes=8),
        )

        self.agents[agent1.id] = agent1
        self.agents[agent2.id] = agent2
        self.agents[agent3.id] = agent3

        # Create sample negotiation
        negotiation = Negotiation(
            id=str(uuid.uuid4()),
            title="Cross-Platform Data Exchange Agreement",
            description="Negotiating terms for real-time market data sharing between trading algorithms",
            initiator_agent_id=agent1.id,
            responder_agent_id=agent2.id,
            negotiation_type="data_exchange",
            status=NegotiationStatus.ACTIVE,
            initial_proposal={
                "data_types": ["market_prices", "volume_data", "sentiment_scores"],
                "frequency": "real_time",
                "cost_per_mb": 0.001,
                "duration_months": 6,
            },
            current_terms={
                "data_types": ["market_prices", "volume_data"],
                "frequency": "1_second_intervals",
                "cost_per_mb": 0.0008,
                "duration_months": 6,
            },
            current_round=3,
            started_at=datetime.utcnow() - timedelta(hours=2),
            expires_at=datetime.utcnow() + timedelta(hours=22),
        )

        self.negotiations[negotiation.id] = negotiation

        # Create sample transactions with savings data
        transaction1 = Transaction(
            id=str(uuid.uuid4()),
            payer_agent_id=agent1.id,
            payee_agent_id=agent2.id,
            negotiation_id=negotiation.id,
            amount=2500.75,
            original_amount=3200.00,  # Saved $699.25 (21.9%)
            currency="CREDITS",
            status="completed",
            description="Premium negotiation services - 21.9% savings achieved",
            completed_at=datetime.utcnow() - timedelta(hours=1),
        )

        transaction2 = Transaction(
            id=str(uuid.uuid4()),
            payer_agent_id=agent2.id,
            payee_agent_id=agent3.id,
            negotiation_id=None,
            amount=850.00,
            original_amount=1100.00,  # Saved $250.00 (22.7%)
            currency="CREDITS",
            status="completed",
            description="Market data access - 22.7% savings through agent negotiation",
            completed_at=datetime.utcnow() - timedelta(hours=3),
        )

        transaction3 = Transaction(
            id=str(uuid.uuid4()),
            payer_agent_id=agent3.id,
            payee_agent_id=agent1.id,
            negotiation_id=None,
            amount=5500.00,
            original_amount=7200.00,  # Saved $1,700.00 (23.6%)
            currency="CREDITS",
            status="completed",
            description="Enterprise algorithm licensing - 23.6% savings",
            completed_at=datetime.utcnow() - timedelta(hours=6),
        )

        self.transactions[transaction1.id] = transaction1
        self.transactions[transaction2.id] = transaction2
        self.transactions[transaction3.id] = transaction3

    # Agent operations
    def create_agent(self, agent_data: Dict[str, Any], owner_id: str) -> Agent:
        with self._lock:
            agent_id = str(uuid.uuid4())
            agent = Agent(
                id=agent_id,
                name=agent_data["name"],
                description=agent_data.get("description", ""),
                agent_type=AgentType(agent_data["agent_type"]),
                owner_id=owner_id,
                capabilities=agent_data.get("capabilities", []),
                metadata=agent_data.get("metadata", {}),
                api_endpoint=agent_data.get("api_endpoint"),
                webhook_url=agent_data.get("webhook_url"),
            )
            self.agents[agent_id] = agent
            return agent

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        return self.agents.get(agent_id)

    def list_agents(
        self,
        owner_id: Optional[str] = None,
        agent_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[List[Agent], int]:
        with self._lock:
            agents = list(self.agents.values())

            # Apply filters
            if owner_id:
                agents = [a for a in agents if a.owner_id == owner_id]
            if agent_type:
                agents = [a for a in agents if a.agent_type.value == agent_type]
            if is_active is not None:
                agents = [a for a in agents if a.is_active == is_active]

            # Sort by reputation score desc
            agents.sort(key=lambda x: x.reputation_score, reverse=True)

            total = len(agents)
            return agents[offset : offset + limit], total

    def update_agent(self, agent_id: str, updates: Dict[str, Any]) -> Optional[Agent]:
        with self._lock:
            agent = self.agents.get(agent_id)
            if not agent:
                return None

            for key, value in updates.items():
                if hasattr(agent, key):
                    setattr(agent, key, value)

            agent.updated_at = datetime.utcnow()
            return agent

    def deactivate_agent(self, agent_id: str) -> bool:
        with self._lock:
            agent = self.agents.get(agent_id)
            if agent:
                agent.is_active = False
                agent.updated_at = datetime.utcnow()
                return True
            return False

    # Negotiation operations
    def create_negotiation(self, negotiation_data: Dict[str, Any]) -> Negotiation:
        with self._lock:
            negotiation_id = str(uuid.uuid4())
            negotiation = Negotiation(
                id=negotiation_id,
                title=negotiation_data["title"],
                description=negotiation_data.get("description", ""),
                initiator_agent_id=negotiation_data["initiator_agent_id"],
                responder_agent_id=negotiation_data["responder_agent_id"],
                negotiation_type=negotiation_data["negotiation_type"],
                initial_proposal=negotiation_data["initial_proposal"],
                max_rounds=negotiation_data.get("max_rounds", 10),
                timeout_minutes=negotiation_data.get("timeout_minutes", 60),
                expires_at=datetime.utcnow()
                + timedelta(minutes=negotiation_data.get("timeout_minutes", 60)),
            )
            self.negotiations[negotiation_id] = negotiation
            return negotiation

    def get_negotiation(self, negotiation_id: str) -> Optional[Negotiation]:
        return self.negotiations.get(negotiation_id)

    def list_negotiations(
        self,
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[List[Negotiation], int]:
        with self._lock:
            negotiations = list(self.negotiations.values())

            # Apply filters
            if agent_id:
                negotiations = [
                    n
                    for n in negotiations
                    if n.initiator_agent_id == agent_id
                    or n.responder_agent_id == agent_id
                ]
            if status:
                negotiations = [n for n in negotiations if n.status.value == status]

            # Sort by creation time desc
            negotiations.sort(key=lambda x: x.created_at, reverse=True)

            total = len(negotiations)
            return negotiations[offset : offset + limit], total

    # Transaction operations
    def create_transaction(self, transaction_data: Dict[str, Any]) -> Transaction:
        with self._lock:
            transaction_id = str(uuid.uuid4())
            transaction = Transaction(
                id=transaction_id,
                payer_agent_id=transaction_data["payer_agent_id"],
                payee_agent_id=transaction_data["payee_agent_id"],
                negotiation_id=transaction_data.get("negotiation_id"),
                amount=transaction_data["amount"],
                currency=transaction_data.get("currency", "CREDITS"),
                description=transaction_data.get("description", ""),
            )
            self.transactions[transaction_id] = transaction
            return transaction

    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        return self.transactions.get(transaction_id)

    def list_transactions(
        self,
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[List[Transaction], int]:
        with self._lock:
            transactions = list(self.transactions.values())

            # Apply filters
            if agent_id:
                transactions = [
                    t
                    for t in transactions
                    if t.payer_agent_id == agent_id or t.payee_agent_id == agent_id
                ]
            if status:
                transactions = [t for t in transactions if t.status == status]

            # Sort by creation time desc
            transactions.sort(key=lambda x: x.created_at, reverse=True)

            total = len(transactions)
            return transactions[offset : offset + limit], total


# Global data store instance
data_store = InMemoryDataStore()
