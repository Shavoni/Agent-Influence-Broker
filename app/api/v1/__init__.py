"""
Agent Influence Broker - API v1

Version 1 of the Agent Influence Broker API with
comprehensive endpoint implementations.
"""

# Import routers (individual modules handle their own imports)
try:
    from . import agents
except ImportError:
    agents = None

try:
    from . import influence
except ImportError:
    influence = None

try:
    from . import negotiations
except ImportError:
    negotiations = None

try:
    from . import transactions
except ImportError:
    transactions = None

# TODO: Re-enable when webhook schemas are complete
# try:
#     from . import webhooks
# except ImportError:
#     webhooks = None

__all__ = ["agents", "influence", "negotiations", "transactions"]
