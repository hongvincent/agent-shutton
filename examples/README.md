# MedResearch AI Usage Examples

This directory contains examples demonstrating how to use the advanced features of MedResearch AI.

## Files

### `usage_examples.py`
Comprehensive examples showing:

1. **Memory Bank Usage**
   - Storing research sessions
   - Retrieving past research
   - Searching memories
   - Getting summaries

2. **A2A Protocol Usage**
   - Agent-to-agent messaging
   - Request/response patterns
   - Status updates
   - Message statistics

3. **SessionManager Usage**
   - Creating research sessions
   - Pausing sessions
   - Resuming from checkpoints
   - Tracking progress

4. **Integrated Workflow**
   - All features working together
   - Complete research flow
   - End-to-end demonstration

## Running the Examples

```bash
# Run all examples
python examples/usage_examples.py

# Or run individual examples in Python:
python -c "from examples.usage_examples import example_memory_bank; example_memory_bank()"
```

## Example Output

The examples demonstrate real usage patterns and show:
- How agents communicate via A2A Protocol
- How research history is stored in Memory Bank
- How long-running sessions can be paused/resumed
- How all components integrate in a complete workflow

## Integration with Main System

These patterns are used throughout MedResearch AI:

- **API** (`api/main.py`): Uses SessionManager for pause/resume
- **Agents** (`medresearch_agent/agent.py`): Can use Memory Bank for context
- **Workflow**: A2A Protocol coordinates multi-agent research

See the main README for complete system documentation.
