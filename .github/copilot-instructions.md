<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Agent Influence Broker - Copilot Instructions

This is a sophisticated FastAPI application where AI agents can negotiate, influence, and transact with each other.

## Project Architecture
- **Backend**: FastAPI with async/await patterns
- **Database**: Supabase (PostgreSQL) with Row Level Security
- **Authentication**: JWT tokens with role-based access
- **Deployment**: Docker containers with GitHub Actions CI/CD
- **Testing**: pytest with async test support

## Key Components
1. **Agent Management**: Registration, capabilities, reputation scoring
2. **Negotiation Engine**: Real-time negotiation protocols between agents
3. **Influence Metrics**: Track and calculate agent influence scores
4. **Transaction System**: Secure value exchange between agents
5. **Webhook System**: Real-time notifications and integrations

## Code Standards
- Use async/await for all database operations
- Follow FastAPI best practices with dependency injection
- Implement comprehensive error handling with custom exceptions
- Use Pydantic models for request/response validation
- Follow RESTful API conventions
- Write comprehensive docstrings and type hints
- Implement proper logging throughout the application

## Security Considerations
- All endpoints require proper authentication
- Implement rate limiting for API endpoints
- Use parameterized queries to prevent SQL injection
- Validate all input data with Pydantic
- Implement proper CORS policies
- Use environment variables for sensitive configuration

## Testing Strategy
- Unit tests for all service functions
- Integration tests for API endpoints
- Mock external dependencies (Supabase, webhooks)
- Test both success and error scenarios
- Maintain high test coverage (>90%)
