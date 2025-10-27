# Debate AI - TDD Test Plan

## Phase 1: Basic MCP Server Setup
- [x] Test: MCP server can be initialized
- [x] Test: MCP server responds to ping/health check
- [x] Test: MCP server can register tools

## Phase 2: Single Agent Communication
- [x] Test: Agent can receive a prompt and return a response
- [x] Test: Agent can use different LLM providers (via SDK)
- [x] Test: Agent response includes metadata (agent_id, timestamp)

## Phase 3: Multi-Agent Debate Structure
- [x] Test: System can initialize multiple agents with different roles
- [x] Test: First agent generates initial response to a query
- [x] Test: Second agent receives first agent's response and provides feedback
- [x] Test: First agent can revise based on feedback
- [x] Test: Debate continues for configurable number of rounds

## Phase 4: Consensus Mechanism
- [x] Test: Each agent can vote on agreement (agree/disagree/needs_revision)
- [x] Test: System detects when all agents agree
- [x] Test: System requests revisions when agents disagree
- [x] Test: System has maximum iteration limit to prevent infinite loops

## Phase 5: MCP Tool Integration
- [ ] Test: Expose debate_on_topic as MCP tool
- [ ] Test: Tool accepts topic/question as parameter
- [ ] Test: Tool returns final consensus result
- [ ] Test: Tool provides debate history/transcript

## Phase 6: Agent Configuration
- [ ] Test: Agents can have different personas/roles (critic, supporter, analyst)
- [ ] Test: Number of agents is configurable
- [ ] Test: Agent order can be specified
- [ ] Test: Consensus threshold is configurable

## Phase 7: Error Handling
- [ ] Test: Handle LLM API failures gracefully
- [ ] Test: Handle timeout scenarios
- [ ] Test: Handle cases where consensus cannot be reached
- [ ] Test: Validate input parameters

## Phase 8: Integration Testing
- [ ] Test: Full debate workflow end-to-end
- [ ] Test: MCP server can be discovered by Claude Desktop
- [ ] Test: Tool can be invoked from Claude Desktop
