# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Code style
- Use modern python syntax (eg. `|` instead of `Optional` and pattern matching)
- For tests, don't write redundant docstrings
- Use relative imports as the repo is a python library

## Development Commands

**Setup and Installation:**
```bash
make install    # Install all dependencies and extras using uv
```

**Code Quality:**
```bash
make lint          # Run ruff check and format --check
make format        # Run ruff check --fix and format
```

**Testing:**
```bash
make test          # Run all tests
make test-verbose  # Run tests with verbose output
```

**Build:**
```bash
make build         # Build the package using uv
```

## Architecture Overview

This is the **OAGI Python SDK** - a client library for interacting with the OAGI API Gateway that provides vision-based task automation capabilities.

### Core Architecture

**Three-Layer Design:**
1. **API Client Layer** (`sync_client.py`) - HTTP client wrapping the OAGI API Gateway
2. **Task Orchestration** (`short_task.py`) - High-level task management and workflow
3. **Execution Layer** - Action handlers and image providers for automation

### Key Components

**SyncClient** (`src/oagi/sync_client.py`):
- httpx-based HTTP client with persistent connections
- Wraps `/v1/message` endpoint for vision-based task analysis
- Handles task initialization and continuation via task_id management
- Manages API authentication and error handling

**ShortTask** (`src/oagi/short_task.py`):
- Main orchestration class that coordinates the task execution workflow
- `init_task()` - starts new task with description
- `step()` - sends screenshots to API and gets action recommendations  
- `auto_mode()` - fully automated execution with action handlers
- Maintains task state across multiple API calls

**Type System** (`src/oagi/types/`):
- **Action** - Represents executable actions (click, type, scroll, etc.)
- **Step** - Contains reasoning, actions, and completion status
- **ActionHandler Protocol** - Interface for executing actions
- **ImageProvider Protocol** - Interface for capturing screenshots

**Default Implementations:**
- **PyautoguiActionHandler** - Stub implementation for PyAutoGUI-based automation
- **ScreenshotMaker** - Stub implementation for screen capture

### API Integration Pattern

The SDK follows a stateful conversation pattern with the OAGI API:

1. **Task Initialization**: First call to `/v1/message` with `task_description`, receives `task_id`
2. **Task Continuation**: Subsequent calls use `task_id` with new screenshots
3. **Action Execution**: API returns recommended actions based on screenshot analysis
4. **Completion Detection**: API indicates when task is complete via `is_complete` flag

### Usage Patterns

**Manual Control** (step-by-step):
```python
task = ShortTask(api_key="...", base_url="...")
task.init_task("Go to website and login")
screenshot = image_provider()
step = task.step(screenshot)  # Returns actions to take
executor(step.actions)       # Execute the actions
```

**Automated Mode**:
```python
task.auto_mode(
    "Complete booking process",
    executor=PyautoguiActionHandler(),
    image_provider=ScreenshotMaker()
)
```

### Important Implementation Details

- **HTTP Connection Reuse**: SyncClient uses a single httpx.Client instance for keep-alive connections
- **Task State Management**: task_id is automatically managed between API calls
- **Resource Cleanup**: Both SyncClient and ShortTask support context managers and explicit close() methods
- **Error Handling**: Custom exceptions for API errors with detailed error information
- **Type Safety**: Full Pydantic models for all API request/response structures