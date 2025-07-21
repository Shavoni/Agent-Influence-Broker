"""Database migration system for Agent Influence Broker."""

import asyncio
import logging
from typing import Any, Dict, List

from app.core.config import get_settings
from app.database.supabase import SupabaseClient

logger = logging.getLogger(__name__)


class Migration:
    """Base migration class."""

    def __init__(self, version: str, description: str):
        self.version = version
        self.description = description

    async def up(self, db: SupabaseClient) -> None:
        """Apply migration."""
        raise NotImplementedError

    async def down(self, db: SupabaseClient) -> None:
        """Reverse migration."""
        raise NotImplementedError


class CreateAgentsTable(Migration):
    """Create agents table migration."""

    def __init__(self):
        super().__init__("001", "Create agents table")

    async def up(self, db: SupabaseClient) -> None:
        """Create agents table."""
        sql = """
        CREATE TABLE IF NOT EXISTS agents (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            owner_id UUID NOT NULL,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            capabilities JSONB DEFAULT '[]'::jsonb,
            reputation_score DECIMAL(5,2) DEFAULT 0.0 CHECK (reputation_score >= 0 AND reputation_score <= 100),
            status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended', 'maintenance')),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            CONSTRAINT unique_agent_name UNIQUE (owner_id, name)
        );
        
        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_agents_owner_id ON agents(owner_id);
        CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
        CREATE INDEX IF NOT EXISTS idx_agents_reputation ON agents(reputation_score DESC);
        
        -- Enable RLS
        ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
        
        -- Create RLS policies
        CREATE POLICY agents_select_policy ON agents
            FOR SELECT USING (owner_id = auth.uid() OR status = 'active');
        
        CREATE POLICY agents_insert_policy ON agents
            FOR INSERT WITH CHECK (owner_id = auth.uid());
        
        CREATE POLICY agents_update_policy ON agents
            FOR UPDATE USING (owner_id = auth.uid());
        
        CREATE POLICY agents_delete_policy ON agents
            FOR DELETE USING (owner_id = auth.uid());
        """

        try:
            await db.execute_sql(sql)
            logger.info("Agents table created successfully")
        except Exception as e:
            logger.error(f"Failed to create agents table: {e}")
            raise


class CreateNegotiationsTable(Migration):
    """Create negotiations table migration."""

    def __init__(self):
        super().__init__("002", "Create negotiations table")

    async def up(self, db: SupabaseClient) -> None:
        """Create negotiations table."""
        sql = """
        CREATE TABLE IF NOT EXISTS negotiations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            initiator_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
            respondent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
            status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'accepted', 'rejected', 'completed', 'cancelled')),
            terms JSONB NOT NULL,
            metadata JSONB DEFAULT '{}'::jsonb,
            offer_count INTEGER DEFAULT 0,
            last_offer_by UUID,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            completed_at TIMESTAMP WITH TIME ZONE,
            CONSTRAINT different_agents CHECK (initiator_id != respondent_id)
        );
        
        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_negotiations_initiator ON negotiations(initiator_id);
        CREATE INDEX IF NOT EXISTS idx_negotiations_respondent ON negotiations(respondent_id);
        CREATE INDEX IF NOT EXISTS idx_negotiations_status ON negotiations(status);
        CREATE INDEX IF NOT EXISTS idx_negotiations_created_at ON negotiations(created_at DESC);
        
        -- Enable RLS
        ALTER TABLE negotiations ENABLE ROW LEVEL SECURITY;
        
        -- Create RLS policies
        CREATE POLICY negotiations_select_policy ON negotiations
            FOR SELECT USING (
                initiator_id IN (SELECT id FROM agents WHERE owner_id = auth.uid()) OR
                respondent_id IN (SELECT id FROM agents WHERE owner_id = auth.uid())
            );
        
        CREATE POLICY negotiations_insert_policy ON negotiations
            FOR INSERT WITH CHECK (
                initiator_id IN (SELECT id FROM agents WHERE owner_id = auth.uid())
            );
        
        CREATE POLICY negotiations_update_policy ON negotiations
            FOR UPDATE USING (
                initiator_id IN (SELECT id FROM agents WHERE owner_id = auth.uid()) OR
                respondent_id IN (SELECT id FROM agents WHERE owner_id = auth.uid())
            );
        """

        try:
            await db.execute_sql(sql)
            logger.info("Negotiations table created successfully")
        except Exception as e:
            logger.error(f"Failed to create negotiations table: {e}")
            raise


class CreateTransactionsTable(Migration):
    """Create transactions table migration."""

    def __init__(self):
        super().__init__("003", "Create transactions table")

    async def up(self, db: SupabaseClient) -> None:
        """Create transactions table."""
        sql = """
        CREATE TABLE IF NOT EXISTS transactions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            from_agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
            to_agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
            amount DECIMAL(15,2) NOT NULL CHECK (amount > 0),
            currency VARCHAR(3) DEFAULT 'USD',
            transaction_type VARCHAR(50) DEFAULT 'negotiation_payment',
            status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled', 'refunded')),
            description TEXT,
            metadata JSONB DEFAULT '{}'::jsonb,
            fee_amount DECIMAL(15,2) DEFAULT 0.0,
            net_amount DECIMAL(15,2),
            reference_id VARCHAR(255),
            negotiation_id UUID REFERENCES negotiations(id),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            completed_at TIMESTAMP WITH TIME ZONE,
            CONSTRAINT different_transaction_agents CHECK (from_agent_id != to_agent_id)
        );
        
        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_transactions_from_agent ON transactions(from_agent_id);
        CREATE INDEX IF NOT EXISTS idx_transactions_to_agent ON transactions(to_agent_id);
        CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
        CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_transactions_negotiation ON transactions(negotiation_id);
        
        -- Enable RLS
        ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
        
        -- Create RLS policies
        CREATE POLICY transactions_select_policy ON transactions
            FOR SELECT USING (
                from_agent_id IN (SELECT id FROM agents WHERE owner_id = auth.uid()) OR
                to_agent_id IN (SELECT id FROM agents WHERE owner_id = auth.uid())
            );
        
        CREATE POLICY transactions_insert_policy ON transactions
            FOR INSERT WITH CHECK (
                from_agent_id IN (SELECT id FROM agents WHERE owner_id = auth.uid())
            );
        """

        try:
            await db.execute_sql(sql)
            logger.info("Transactions table created successfully")
        except Exception as e:
            logger.error(f"Failed to create transactions table: {e}")
            raise


async def run_migrations() -> None:
    """Run all pending migrations."""
    settings = get_settings()

    # Skip migrations in testing environment if using mock
    if settings.ENVIRONMENT == "testing" and "test" in settings.DATABASE_URL:
        logger.info("Skipping migrations in test environment")
        return

    db = SupabaseClient()

    migrations = [
        CreateAgentsTable(),
        CreateNegotiationsTable(),
        CreateTransactionsTable(),
    ]

    for migration in migrations:
        try:
            logger.info(
                f"Running migration {migration.version}: {migration.description}"
            )
            await migration.up(db)
            logger.info(f"Migration {migration.version} completed successfully")
        except Exception as e:
            logger.error(f"Migration {migration.version} failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(run_migrations())
