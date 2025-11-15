# CLAUDE.md - AI Assistant Guide for Agent Shutton

## Project Overview

**Agent Shutton** is a multi-agent blog writing system built with Google Agent Development Kit (ADK). It automates the creation of technical blog posts through a modular, collaborative architecture where specialized AI agents handle different aspects of content creation.

**Key Purpose**: Streamline technical blog writing by automating research, outlining, writing, editing, and social media promotion while maintaining human oversight and feedback loops.

**Tech Stack**:
- Python 3.11.3+
- Google ADK 1.18.0
- Gemini 2.5 Pro/Flash models
- pytest for testing

## Architecture Overview

This is a **multi-agent system** with hierarchical delegation:

```
interactive_blogger_agent (orchestrator)
├── robust_blog_planner (LoopAgent)
│   ├── blog_planner (content strategist)
│   └── OutlineValidationChecker (validator)
├── robust_blog_writer (LoopAgent)
│   ├── blog_writer (technical writer)
│   └── BlogPostValidationChecker (validator)
├── blog_editor (editor)
└── social_media_writer (marketer)
```

**Agent Pattern**: The root agent (`interactive_blogger_agent`) acts as a project manager, delegating specialized tasks to sub-agents and maintaining an iterative workflow with user feedback loops.

## Directory Structure

```
/home/user/agent-shutton/
├── blogger_agent/              # Main Python package
│   ├── __init__.py            # Package exports (root_agent)
│   ├── agent.py               # Main orchestrator agent definition
│   ├── config.py              # Model configuration and settings
│   ├── tools.py               # Custom tools (file saving, codebase analysis)
│   ├── agent_utils.py         # Helper functions (output suppression)
│   ├── validation_checkers.py # Quality validation agents
│   └── sub_agents/            # Specialized sub-agents
│       ├── __init__.py        # Sub-agent exports
│       ├── blog_planner.py    # Outline generation agent
│       ├── blog_writer.py     # Content writing agent
│       ├── blog_editor.py     # Revision agent
│       └── social_media_writer.py  # Promotion content agent
├── tests/
│   └── test_agent.py          # Integration test
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── .gitignore                 # Git ignore patterns
└── LICENSE                    # Apache 2.0 license
```

## Key Components

### 1. Main Orchestrator Agent

**File**: `blogger_agent/agent.py`

**Agent**: `interactive_blogger_agent` (exported as `root_agent`)
- **Model**: `gemini-2.5-flash` (worker_model)
- **Role**: Coordinates the entire blog creation workflow
- **Tools**: `save_blog_post_to_file`, `analyze_codebase`
- **Sub-agents**: All four specialized agents
- **Output Key**: `blog_outline`

**Workflow**:
1. Plan → Refine outline with user feedback
2. Choose visual content strategy
3. Write → Present draft
4. Edit → Iterate based on feedback
5. Generate social media posts (optional)
6. Export to markdown file

### 2. Sub-Agents

#### Blog Planner (`blog_planner.py`)

**Base Agent**: `blog_planner`
- **Model**: `gemini-2.5-flash`
- **Role**: Content strategist - creates structured outlines
- **Tools**: `google_search`
- **Output Key**: `blog_outline`
- **Special Feature**: Reads `codebase_context` from session state

**Robust Wrapper**: `robust_blog_planner` (LoopAgent)
- **Max Iterations**: 3
- **Validation**: `OutlineValidationChecker`
- **Pattern**: Retries until valid outline is generated

#### Blog Writer (`blog_writer.py`)

**Base Agent**: `blog_writer`
- **Model**: `gemini-2.5-pro` (critic_model) - uses more powerful model
- **Role**: Expert technical writer for sophisticated audiences
- **Tools**: `google_search`
- **Output Key**: `blog_post`
- **Audience**: Similar to "Towards Data Science" and "freeCodeCamp" readers

**Robust Wrapper**: `robust_blog_writer` (LoopAgent)
- **Max Iterations**: 3
- **Validation**: `BlogPostValidationChecker`

#### Blog Editor (`blog_editor.py`)

**Agent**: `blog_editor`
- **Model**: `gemini-2.5-pro` (critic_model)
- **Role**: Professional technical editor
- **Output Key**: `blog_post`
- **Purpose**: Iterative revision based on user feedback

#### Social Media Writer (`social_media_writer.py`)

**Agent**: `social_media_writer`
- **Model**: `gemini-2.5-pro` (critic_model)
- **Role**: Social media marketing expert
- **Output Key**: `social_media_posts`
- **Platforms**: Twitter (short, engaging) and LinkedIn (professional)

### 3. Tools (`tools.py`)

**`save_blog_post_to_file(blog_post: str, filename: str) -> dict`**
- Exports final blog post to markdown file
- Returns: `{"status": "success"}`

**`analyze_codebase(directory: str) -> dict`**
- Recursively scans directory for all files
- Concatenates content into `codebase_context` string
- Handles encoding issues (UTF-8 fallback to latin-1)
- Returns: `{"codebase_context": <string>}`

### 4. Validation System (`validation_checkers.py`)

**Pattern**: Custom `BaseAgent` implementations that check session state

**`OutlineValidationChecker`**
- Checks for `blog_outline` in session state
- Escalates (exits loop) if valid, otherwise retries

**`BlogPostValidationChecker`**
- Checks for `blog_post` in session state
- Escalates if valid, otherwise retries

**Key Mechanism**: `EventActions(escalate=True)` signals LoopAgent to proceed

### 5. Configuration (`config.py`)

**`ResearchConfiguration` dataclass**:
```python
critic_model: str = "gemini-2.5-pro"      # High-quality tasks (writing, editing)
worker_model: str = "gemini-2.5-flash"    # Fast tasks (planning, orchestration)
max_search_iterations: int = 5
```

**Environment Variables**:
- `GOOGLE_CLOUD_PROJECT`: Auto-detected or set manually
- `GOOGLE_CLOUD_LOCATION`: Default "global"
- `GOOGLE_GENAI_USE_VERTEXAI`: Default "True"
- Optional: `GOOGLE_API_KEY` for AI Studio (requires `GOOGLE_GENAI_USE_VERTEXAI=FALSE`)

### 6. Utilities (`agent_utils.py`)

**`suppress_output_callback(callback_context: CallbackContext) -> Content`**
- Used in `after_agent_callback` for sub-agents
- Prevents intermediate agent outputs from showing to user
- Returns empty `Content()` object

## Development Workflows

### Running the Agent

**ADK Web Mode** (Interactive UI):
```bash
adk web
```
This starts the ADK web interface for interactive testing.

**Integration Test**:
```bash
python -m tests.test_agent
```

### Test Workflow (`tests/test_agent.py`)

The integration test simulates a complete blog creation workflow:
1. "I want to write a blog post about the new features in the latest version of the ADK."
2. "looks good, write it" (approve outline)
3. "1" (choose visual content option: placeholders)
4. "looks good, I approve" (approve draft)
5. "yes" (generate social media posts)
6. "my_new_blog_post.md" (save with filename)

**Key Components**:
- Uses `InMemorySessionService` for state management
- `Runner` class executes agent with session context
- Processes events asynchronously

### Installation

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt
```

## Code Conventions

### 1. Agent Definition Pattern

```python
from google.adk.agents import Agent
from .config import config

my_agent = Agent(
    name="agent_name",
    model=config.worker_model,  # or config.critic_model
    description="Brief agent description",
    instruction="""
    Detailed multi-line instructions for agent behavior.
    Include role, task, output format, and special considerations.
    """,
    tools=[...],  # Optional tools
    sub_agents=[...],  # Optional sub-agents
    output_key="state_key_name",  # Where to store output in session state
    after_agent_callback=suppress_output_callback,  # Optional
)
```

### 2. LoopAgent Pattern (Robust Retry)

```python
from google.adk.agents import LoopAgent

robust_agent = LoopAgent(
    name="robust_agent_name",
    description="Description of retry behavior",
    sub_agents=[
        base_agent,
        ValidationChecker(name="validation_checker"),
    ],
    max_iterations=3,
    after_agent_callback=suppress_output_callback,
)
```

**How it works**:
1. LoopAgent runs `base_agent`
2. Runs `ValidationChecker`
3. If validator escalates → exit loop
4. If validator doesn't escalate → retry (up to max_iterations)

### 3. Validation Checker Pattern

```python
from google.adk.agents import BaseAgent
from google.adk.events import Event, EventActions

class MyValidationChecker(BaseAgent):
    async def _run_async_impl(self, context: InvocationContext) -> AsyncGenerator[Event, None]:
        if context.session.state.get("expected_key"):
            # Valid - escalate to exit loop
            yield Event(author=self.name, actions=EventActions(escalate=True))
        else:
            # Invalid - don't escalate, LoopAgent will retry
            yield Event(author=self.name)
```

### 4. Tool Definition Pattern

```python
def my_tool(param1: str, param2: int) -> dict:
    """Tool description for agent to understand usage."""
    # Tool implementation
    return {"key": "value"}  # Return dict for session state
```

Wrap with `FunctionTool`:
```python
from google.adk.tools import FunctionTool

tools=[FunctionTool(my_tool)]
```

### 5. Session State Usage

**Writing to state**: Use `output_key` parameter in Agent definition
```python
output_key="blog_outline"  # Agent output stored in session.state["blog_outline"]
```

**Reading from state**: Reference in instructions
```python
instruction="""
The outline is available in the `blog_outline` state key.
The codebase context is in the `codebase_context` state key.
"""
```

### 6. Copyright Headers

All Python files include Apache 2.0 copyright header:
```python
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License")
# ...
```

## Model Selection Strategy

| Task Type | Model | Rationale |
|-----------|-------|-----------|
| Orchestration | `gemini-2.5-flash` | Fast decision-making, cost-effective |
| Planning | `gemini-2.5-flash` | Quick outline generation with retries |
| Writing | `gemini-2.5-pro` | High-quality technical content |
| Editing | `gemini-2.5-pro` | Nuanced revision and refinement |
| Social Media | `gemini-2.5-pro` | Marketing requires quality copywriting |

**Principle**: Use Flash for speed, Pro for quality.

## Extension Points

### Adding a New Sub-Agent

1. **Create agent file** in `blogger_agent/sub_agents/my_new_agent.py`:
```python
from google.adk.agents import Agent
from ..config import config

my_new_agent = Agent(
    name="my_new_agent",
    model=config.worker_model,
    description="Agent description",
    instruction="...",
    output_key="my_output",
)
```

2. **Export in** `blogger_agent/sub_agents/__init__.py`:
```python
from .my_new_agent import my_new_agent
```

3. **Import and add to main agent** in `blogger_agent/agent.py`:
```python
from .sub_agents import (..., my_new_agent)

interactive_blogger_agent = Agent(
    ...
    sub_agents=[..., my_new_agent],
)
```

4. **Update workflow instructions** to include when to delegate to new agent

### Adding a New Tool

1. **Define function** in `blogger_agent/tools.py`:
```python
def my_new_tool(param: str) -> dict:
    """Tool description."""
    # Implementation
    return {"result": "value"}
```

2. **Import and wrap in agent**:
```python
from .tools import my_new_tool
from google.adk.tools import FunctionTool

tools=[FunctionTool(my_new_tool)]
```

### Adding Google Search to New Agents

```python
from google.adk.tools import google_search

my_agent = Agent(
    ...
    tools=[google_search],
)
```

## Common AI Assistant Tasks

### When Modifying Agent Instructions

1. **Read the current agent file** to understand existing behavior
2. **Preserve the workflow structure** unless explicitly asked to change it
3. **Maintain consistency** in tone and instruction format
4. **Update related agents** if changes affect workflow dependencies
5. **Test with integration test** after changes

### When Debugging Agent Behavior

1. **Check session state keys** - ensure output_key matches references in other agents
2. **Verify LoopAgent validation** - ensure validators check correct state keys
3. **Review agent instructions** - confirm they reference available tools and state
4. **Check model selection** - ensure appropriate model for task complexity
5. **Test workflow sequence** - ensure agents are called in correct order

### When Adding Features

1. **Determine placement**:
   - New capability → new sub-agent
   - New data source → new tool
   - New validation → new checker
2. **Follow existing patterns** (see Code Conventions)
3. **Update main agent instructions** to incorporate new feature in workflow
4. **Add to integration test** if it changes the workflow
5. **Update README.md** with user-facing documentation

### When Refactoring

1. **Preserve public interface** - `root_agent` export must remain
2. **Maintain session state keys** - other agents depend on these
3. **Keep agent names consistent** - ADK uses names for routing
4. **Test thoroughly** - multi-agent systems have complex dependencies
5. **Update this CLAUDE.md** to reflect changes

## Session State Reference

| Key | Set By | Used By | Type |
|-----|--------|---------|------|
| `codebase_context` | `analyze_codebase` tool | `blog_planner`, `blog_writer` | str |
| `blog_outline` | `blog_planner` | `blog_writer`, user review | str (markdown) |
| `blog_post` | `blog_writer`, `blog_editor` | User review, export | str (markdown) |
| `social_media_posts` | `social_media_writer` | User review | str (markdown) |

## Testing Strategy

### Integration Test Pattern

```python
async def main():
    # 1. Create session service
    session_service = InMemorySessionService()
    await session_service.create_session(...)

    # 2. Create runner
    runner = Runner(agent=root_agent, ...)

    # 3. Simulate conversation
    queries = ["query1", "query2", ...]
    for query in queries:
        async for event in runner.run_async(...):
            if event.is_final_response():
                # Process response
```

### What to Test

- **Happy path**: Complete workflow from topic to exported file
- **User feedback**: Revision cycles work correctly
- **Edge cases**: Empty codebase, invalid directories, encoding errors
- **State persistence**: Session state maintains across turns

## Dependencies

### Core Dependencies
- `google-adk==1.18.0` - Agent Development Kit
- `pytest==8.4.2` - Testing framework
- `pytest-asyncio==1.2.0` - Async test support

### Optional Dependencies
- `deprecated` - Deprecation warnings
- `pandas` - Data manipulation (for future eval framework)
- `tabulate` - Table formatting
- `tqdm` - Progress bars
- `scikit-learn` - ML utilities (for future eval framework)

## Git Workflow

### Branch Naming
- Use descriptive branch names: `feature/new-agent`, `fix/validation-bug`

### Commit Messages
- Follow conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`
- Reference issue numbers when applicable

### Ignored Files (`.gitignore`)
- Python cache files (`__pycache__`, `*.pyc`)
- Virtual environments (`.venv`, `venv/`)
- Environment files (`.env`)
- Distribution files (`dist/`, `build/`)
- IDE configs (`.idea/`, `.vscode/*`)
- Generated blog posts (`*.md` outputs)

## Troubleshooting

### Common Issues

**Agent not found**: Check `sub_agents/__init__.py` exports
**State key missing**: Verify `output_key` matches references
**Validation loop infinite**: Ensure validator uses `EventActions(escalate=True)`
**Encoding errors**: `analyze_codebase` handles UTF-8 and latin-1 fallback
**Model errors**: Check `GOOGLE_CLOUD_PROJECT` and authentication

### Environment Setup Issues

1. **Vertex AI (default)**:
   - Ensure `gcloud auth application-default login`
   - Project ID auto-detected from credentials

2. **AI Studio**:
   - Create `.env` file with `GOOGLE_API_KEY=...`
   - Set `GOOGLE_GENAI_USE_VERTEXAI=FALSE`

## Future Enhancement Ideas

Based on README.md value statement:
- **Trending topic scanner**: Agent to research trending topics across sites
- **MCP server integration**: Connect to Model Context Protocol servers
- **SEO optimization agent**: Analyze and optimize for search engines
- **Multi-format export**: Support for HTML, PDF, Medium format
- **Content calendar**: Scheduling and planning agent
- **Performance analytics**: Track engagement metrics

## Quick Reference

### File Locations
- Main agent: `blogger_agent/agent.py:30` (`interactive_blogger_agent`)
- Root export: `blogger_agent/__init__.py:1` (`root_agent`)
- Configuration: `blogger_agent/config.py:46` (`config`)
- Tools: `blogger_agent/tools.py`
- Tests: `tests/test_agent.py`

### Running Commands
```bash
# Interactive mode
adk web

# Integration test
python -m tests.test_agent

# Install deps
pip install -r requirements.txt
```

### Key Design Patterns
1. **LoopAgent + Validator**: Robust retry with quality checks
2. **Session State**: Agents communicate via state keys
3. **Hierarchical Delegation**: Main agent delegates to specialists
4. **User-in-the-Loop**: Iterative feedback at each stage
5. **Tool Abstraction**: Tools handle external operations

---

**Last Updated**: 2025-11-15
**ADK Version**: 1.18.0
**Python Version**: 3.11.3+

For questions or contributions, refer to the [README.md](README.md) and [LICENSE](LICENSE).

---

# CLAUDE.md - Agent Shutton을 위한 AI 어시스턴트 가이드

## 프로젝트 개요

**Agent Shutton**은 Google Agent Development Kit(ADK)로 구축된 멀티 에이전트 블로그 작성 시스템입니다. 전문화된 AI 에이전트들이 콘텐츠 제작의 다양한 측면을 처리하는 모듈형 협업 아키텍처를 통해 기술 블로그 게시물 작성을 자동화합니다.

**핵심 목적**: 연구, 개요 작성, 글쓰기, 편집 및 소셜 미디어 홍보를 자동화하면서 인간의 감독과 피드백 루프를 유지하여 기술 블로그 작성을 간소화합니다.

**기술 스택**:
- Python 3.11.3+
- Google ADK 1.18.0
- Gemini 2.5 Pro/Flash 모델
- pytest (테스팅용)

## 아키텍처 개요

이것은 계층적 위임을 갖춘 **멀티 에이전트 시스템**입니다:

```
interactive_blogger_agent (orchestrator)
├── robust_blog_planner (LoopAgent)
│   ├── blog_planner (content strategist)
│   └── OutlineValidationChecker (validator)
├── robust_blog_writer (LoopAgent)
│   ├── blog_writer (technical writer)
│   └── BlogPostValidationChecker (validator)
├── blog_editor (editor)
└── social_media_writer (marketer)
```

**에이전트 패턴**: 루트 에이전트(`interactive_blogger_agent`)는 프로젝트 매니저 역할을 하며, 전문화된 작업을 하위 에이전트에 위임하고 사용자 피드백 루프와 함께 반복적인 워크플로를 유지합니다.

## 디렉토리 구조

```
/home/user/agent-shutton/
├── blogger_agent/              # 메인 Python 패키지
│   ├── __init__.py            # 패키지 내보내기 (root_agent)
│   ├── agent.py               # 메인 오케스트레이터 에이전트 정의
│   ├── config.py              # 모델 구성 및 설정
│   ├── tools.py               # 커스텀 도구 (파일 저장, 코드베이스 분석)
│   ├── agent_utils.py         # 헬퍼 함수 (출력 억제)
│   ├── validation_checkers.py # 품질 검증 에이전트
│   └── sub_agents/            # 전문화된 하위 에이전트
│       ├── __init__.py        # 하위 에이전트 내보내기
│       ├── blog_planner.py    # 개요 생성 에이전트
│       ├── blog_writer.py     # 콘텐츠 작성 에이전트
│       ├── blog_editor.py     # 수정 에이전트
│       └── social_media_writer.py  # 홍보 콘텐츠 에이전트
├── tests/
│   └── test_agent.py          # 통합 테스트
├── requirements.txt           # Python 의존성
├── README.md                  # 프로젝트 문서
├── .gitignore                 # Git 무시 패턴
└── LICENSE                    # Apache 2.0 라이선스
```

## 주요 구성 요소

### 1. 메인 오케스트레이터 에이전트

**파일**: `blogger_agent/agent.py`

**에이전트**: `interactive_blogger_agent` (`root_agent`로 내보내짐)
- **모델**: `gemini-2.5-flash` (worker_model)
- **역할**: 전체 블로그 생성 워크플로 조정
- **도구**: `save_blog_post_to_file`, `analyze_codebase`
- **하위 에이전트**: 4개의 전문화된 에이전트 모두
- **출력 키**: `blog_outline`

**워크플로**:
1. 계획 → 사용자 피드백으로 개요 개선
2. 시각적 콘텐츠 전략 선택
3. 작성 → 초안 제시
4. 편집 → 피드백 기반 반복
5. 소셜 미디어 게시물 생성 (선택 사항)
6. 마크다운 파일로 내보내기

### 2. 하위 에이전트

#### Blog Planner (`blog_planner.py`)

**기본 에이전트**: `blog_planner`
- **모델**: `gemini-2.5-flash`
- **역할**: 콘텐츠 전략가 - 구조화된 개요 작성
- **도구**: `google_search`
- **출력 키**: `blog_outline`
- **특별 기능**: 세션 상태에서 `codebase_context` 읽기

**Robust Wrapper**: `robust_blog_planner` (LoopAgent)
- **최대 반복**: 3회
- **검증**: `OutlineValidationChecker`
- **패턴**: 유효한 개요가 생성될 때까지 재시도

#### Blog Writer (`blog_writer.py`)

**기본 에이전트**: `blog_writer`
- **모델**: `gemini-2.5-pro` (critic_model) - 더 강력한 모델 사용
- **역할**: 정교한 독자를 위한 전문 기술 작가
- **도구**: `google_search`
- **출력 키**: `blog_post`
- **대상 독자**: "Towards Data Science" 및 "freeCodeCamp" 독자와 유사

**Robust Wrapper**: `robust_blog_writer` (LoopAgent)
- **최대 반복**: 3회
- **검증**: `BlogPostValidationChecker`

#### Blog Editor (`blog_editor.py`)

**에이전트**: `blog_editor`
- **모델**: `gemini-2.5-pro` (critic_model)
- **역할**: 전문 기술 편집자
- **출력 키**: `blog_post`
- **목적**: 사용자 피드백 기반 반복적 수정

#### Social Media Writer (`social_media_writer.py`)

**에이전트**: `social_media_writer`
- **모델**: `gemini-2.5-pro` (critic_model)
- **역할**: 소셜 미디어 마케팅 전문가
- **출력 키**: `social_media_posts`
- **플랫폼**: Twitter (짧고 매력적) 및 LinkedIn (전문적)

### 3. 도구 (`tools.py`)

**`save_blog_post_to_file(blog_post: str, filename: str) -> dict`**
- 최종 블로그 게시물을 마크다운 파일로 내보내기
- 반환: `{"status": "success"}`

**`analyze_codebase(directory: str) -> dict`**
- 디렉토리의 모든 파일을 재귀적으로 스캔
- 콘텐츠를 `codebase_context` 문자열로 연결
- 인코딩 문제 처리 (UTF-8, latin-1로 폴백)
- 반환: `{"codebase_context": <string>}`

### 4. 검증 시스템 (`validation_checkers.py`)

**패턴**: 세션 상태를 확인하는 커스텀 `BaseAgent` 구현

**`OutlineValidationChecker`**
- 세션 상태에서 `blog_outline` 확인
- 유효하면 에스컬레이션 (루프 종료), 그렇지 않으면 재시도

**`BlogPostValidationChecker`**
- 세션 상태에서 `blog_post` 확인
- 유효하면 에스컬레이션, 그렇지 않으면 재시도

**핵심 메커니즘**: `EventActions(escalate=True)`는 LoopAgent에게 진행 신호를 보냄

### 5. 구성 (`config.py`)

**`ResearchConfiguration` 데이터클래스**:
```python
critic_model: str = "gemini-2.5-pro"      # 고품질 작업 (작성, 편집)
worker_model: str = "gemini-2.5-flash"    # 빠른 작업 (계획, 오케스트레이션)
max_search_iterations: int = 5
```

**환경 변수**:
- `GOOGLE_CLOUD_PROJECT`: 자동 감지 또는 수동 설정
- `GOOGLE_CLOUD_LOCATION`: 기본값 "global"
- `GOOGLE_GENAI_USE_VERTEXAI`: 기본값 "True"
- 선택 사항: `GOOGLE_API_KEY` (AI Studio용, `GOOGLE_GENAI_USE_VERTEXAI=FALSE` 필요)

### 6. 유틸리티 (`agent_utils.py`)

**`suppress_output_callback(callback_context: CallbackContext) -> Content`**
- 하위 에이전트의 `after_agent_callback`에서 사용
- 중간 에이전트 출력이 사용자에게 표시되지 않도록 방지
- 빈 `Content()` 객체 반환

## 개발 워크플로

### 에이전트 실행

**ADK 웹 모드** (인터랙티브 UI):
```bash
adk web
```
인터랙티브 테스팅을 위한 ADK 웹 인터페이스를 시작합니다.

**통합 테스트**:
```bash
python -m tests.test_agent
```

### 테스트 워크플로 (`tests/test_agent.py`)

통합 테스트는 완전한 블로그 작성 워크플로를 시뮬레이션합니다:
1. "I want to write a blog post about the new features in the latest version of the ADK."
2. "looks good, write it" (개요 승인)
3. "1" (시각적 콘텐츠 옵션 선택: placeholders)
4. "looks good, I approve" (초안 승인)
5. "yes" (소셜 미디어 게시물 생성)
6. "my_new_blog_post.md" (파일명으로 저장)

**주요 구성 요소**:
- 상태 관리를 위한 `InMemorySessionService` 사용
- `Runner` 클래스가 세션 컨텍스트로 에이전트 실행
- 이벤트를 비동기적으로 처리

### 설치

```bash
# 가상 환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows의 경우 `venv\Scripts\activate`

# 의존성 설치
pip install -r requirements.txt
```

## 코드 규칙

### 1. 에이전트 정의 패턴

```python
from google.adk.agents import Agent
from .config import config

my_agent = Agent(
    name="agent_name",
    model=config.worker_model,  # 또는 config.critic_model
    description="간단한 에이전트 설명",
    instruction="""
    에이전트 동작에 대한 상세한 여러 줄 지침.
    역할, 작업, 출력 형식 및 특별 고려 사항 포함.
    """,
    tools=[...],  # 선택 사항 도구
    sub_agents=[...],  # 선택 사항 하위 에이전트
    output_key="state_key_name",  # 세션 상태에 출력을 저장할 위치
    after_agent_callback=suppress_output_callback,  # 선택 사항
)
```

### 2. LoopAgent 패턴 (Robust 재시도)

```python
from google.adk.agents import LoopAgent

robust_agent = LoopAgent(
    name="robust_agent_name",
    description="재시도 동작 설명",
    sub_agents=[
        base_agent,
        ValidationChecker(name="validation_checker"),
    ],
    max_iterations=3,
    after_agent_callback=suppress_output_callback,
)
```

**작동 방식**:
1. LoopAgent가 `base_agent` 실행
2. `ValidationChecker` 실행
3. 검증기가 에스컬레이션하면 → 루프 종료
4. 검증기가 에스컬레이션하지 않으면 → 재시도 (최대 max_iterations까지)

### 3. 검증 체커 패턴

```python
from google.adk.agents import BaseAgent
from google.adk.events import Event, EventActions

class MyValidationChecker(BaseAgent):
    async def _run_async_impl(self, context: InvocationContext) -> AsyncGenerator[Event, None]:
        if context.session.state.get("expected_key"):
            # 유효함 - 루프 종료를 위해 에스컬레이션
            yield Event(author=self.name, actions=EventActions(escalate=True))
        else:
            # 무효함 - 에스컬레이션하지 않음, LoopAgent가 재시도
            yield Event(author=self.name)
```

### 4. 도구 정의 패턴

```python
def my_tool(param1: str, param2: int) -> dict:
    """에이전트가 사용법을 이해하기 위한 도구 설명."""
    # 도구 구현
    return {"key": "value"}  # 세션 상태를 위한 dict 반환
```

`FunctionTool`로 래핑:
```python
from google.adk.tools import FunctionTool

tools=[FunctionTool(my_tool)]
```

### 5. 세션 상태 사용

**상태에 쓰기**: Agent 정의에서 `output_key` 매개변수 사용
```python
output_key="blog_outline"  # 에이전트 출력이 session.state["blog_outline"]에 저장됨
```

**상태에서 읽기**: 지침에서 참조
```python
instruction="""
개요는 `blog_outline` 상태 키에서 사용할 수 있습니다.
코드베이스 컨텍스트는 `codebase_context` 상태 키에 있습니다.
"""
```

### 6. 저작권 헤더

모든 Python 파일에는 Apache 2.0 저작권 헤더가 포함됩니다:
```python
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License")
# ...
```

## 모델 선택 전략

| 작업 유형 | 모델 | 근거 |
|-----------|-------|-----------|
| 오케스트레이션 | `gemini-2.5-flash` | 빠른 의사 결정, 비용 효율적 |
| 계획 | `gemini-2.5-flash` | 재시도를 통한 빠른 개요 생성 |
| 작성 | `gemini-2.5-pro` | 고품질 기술 콘텐츠 |
| 편집 | `gemini-2.5-pro` | 미묘한 수정 및 개선 |
| 소셜 미디어 | `gemini-2.5-pro` | 마케팅은 품질 높은 카피라이팅 필요 |

**원칙**: 속도를 위해 Flash, 품질을 위해 Pro 사용.

## 확장 포인트

### 새 하위 에이전트 추가

1. **에이전트 파일 생성** `blogger_agent/sub_agents/my_new_agent.py`에:
```python
from google.adk.agents import Agent
from ..config import config

my_new_agent = Agent(
    name="my_new_agent",
    model=config.worker_model,
    description="에이전트 설명",
    instruction="...",
    output_key="my_output",
)
```

2. **내보내기** `blogger_agent/sub_agents/__init__.py`에서:
```python
from .my_new_agent import my_new_agent
```

3. **메인 에이전트에 임포트 및 추가** `blogger_agent/agent.py`에서:
```python
from .sub_agents import (..., my_new_agent)

interactive_blogger_agent = Agent(
    ...
    sub_agents=[..., my_new_agent],
)
```

4. **워크플로 지침 업데이트**하여 새 에이전트로 위임할 시점 포함

### 새 도구 추가

1. **함수 정의** `blogger_agent/tools.py`에서:
```python
def my_new_tool(param: str) -> dict:
    """도구 설명."""
    # 구현
    return {"result": "value"}
```

2. **에이전트에서 임포트 및 래핑**:
```python
from .tools import my_new_tool
from google.adk.tools import FunctionTool

tools=[FunctionTool(my_new_tool)]
```

### 새 에이전트에 Google Search 추가

```python
from google.adk.tools import google_search

my_agent = Agent(
    ...
    tools=[google_search],
)
```

## 일반적인 AI 어시스턴트 작업

### 에이전트 지침 수정 시

1. **현재 에이전트 파일 읽기**로 기존 동작 이해
2. 명시적으로 변경 요청받지 않는 한 **워크플로 구조 보존**
3. 어조 및 지침 형식의 **일관성 유지**
4. 변경 사항이 워크플로 의존성에 영향을 주면 **관련 에이전트 업데이트**
5. 변경 후 **통합 테스트로 테스트**

### 에이전트 동작 디버깅 시

1. **세션 상태 키 확인** - output_key가 다른 에이전트의 참조와 일치하는지 확인
2. **LoopAgent 검증 확인** - 검증기가 올바른 상태 키를 확인하는지 확인
3. **에이전트 지침 검토** - 사용 가능한 도구와 상태를 참조하는지 확인
4. **모델 선택 확인** - 작업 복잡도에 적절한 모델인지 확인
5. **워크플로 시퀀스 테스트** - 에이전트가 올바른 순서로 호출되는지 확인

### 기능 추가 시

1. **배치 결정**:
   - 새 기능 → 새 하위 에이전트
   - 새 데이터 소스 → 새 도구
   - 새 검증 → 새 체커
2. **기존 패턴 따르기** (코드 규칙 참조)
3. **메인 에이전트 지침 업데이트**하여 워크플로에 새 기능 통합
4. 워크플로가 변경되면 **통합 테스트에 추가**
5. 사용자 대면 문서로 **README.md 업데이트**

### 리팩토링 시

1. **공개 인터페이스 보존** - `root_agent` 내보내기는 유지되어야 함
2. **세션 상태 키 유지** - 다른 에이전트가 이에 의존
3. **에이전트 이름 일관성 유지** - ADK가 라우팅에 이름 사용
4. **철저히 테스트** - 멀티 에이전트 시스템은 복잡한 의존성을 가짐
5. **이 CLAUDE.md 업데이트**하여 변경 사항 반영

## 세션 상태 참조

| 키 | 설정자 | 사용자 | 타입 |
|-----|--------|---------|------|
| `codebase_context` | `analyze_codebase` 도구 | `blog_planner`, `blog_writer` | str |
| `blog_outline` | `blog_planner` | `blog_writer`, 사용자 검토 | str (markdown) |
| `blog_post` | `blog_writer`, `blog_editor` | 사용자 검토, 내보내기 | str (markdown) |
| `social_media_posts` | `social_media_writer` | 사용자 검토 | str (markdown) |

## 테스팅 전략

### 통합 테스트 패턴

```python
async def main():
    # 1. 세션 서비스 생성
    session_service = InMemorySessionService()
    await session_service.create_session(...)

    # 2. Runner 생성
    runner = Runner(agent=root_agent, ...)

    # 3. 대화 시뮬레이션
    queries = ["query1", "query2", ...]
    for query in queries:
        async for event in runner.run_async(...):
            if event.is_final_response():
                # 응답 처리
```

### 테스트할 항목

- **Happy path**: 주제에서 내보낸 파일까지의 완전한 워크플로
- **사용자 피드백**: 수정 사이클이 올바르게 작동하는지
- **엣지 케이스**: 빈 코드베이스, 잘못된 디렉토리, 인코딩 오류
- **상태 지속성**: 세션 상태가 턴 간에 유지되는지

## 의존성

### 핵심 의존성
- `google-adk==1.18.0` - Agent Development Kit
- `pytest==8.4.2` - 테스팅 프레임워크
- `pytest-asyncio==1.2.0` - 비동기 테스트 지원

### 선택적 의존성
- `deprecated` - 사용 중단 경고
- `pandas` - 데이터 조작 (향후 평가 프레임워크용)
- `tabulate` - 테이블 포맷팅
- `tqdm` - 진행 표시줄
- `scikit-learn` - ML 유틸리티 (향후 평가 프레임워크용)

## Git 워크플로

### 브랜치 명명

- 설명적인 브랜치 이름 사용: `feature/new-agent`, `fix/validation-bug`

### 커밋 메시지

- 기존 커밋 따르기: `feat:`, `fix:`, `docs:`, `refactor:`
- 해당되는 경우 이슈 번호 참조

### 무시된 파일 (`.gitignore`)

- Python 캐시 파일 (`__pycache__`, `*.pyc`)
- 가상 환경 (`.venv`, `venv/`)
- 환경 파일 (`.env`)
- 배포 파일 (`dist/`, `build/`)
- IDE 설정 (`.idea/`, `.vscode/*`)
- 생성된 블로그 게시물 (`*.md` 출력)

## 문제 해결

### 일반적인 문제

**에이전트를 찾을 수 없음**: `sub_agents/__init__.py` 내보내기 확인
**상태 키 누락**: `output_key`가 참조와 일치하는지 확인
**검증 루프 무한**: 검증기가 `EventActions(escalate=True)` 사용하는지 확인
**인코딩 오류**: `analyze_codebase`가 UTF-8 및 latin-1 폴백 처리
**모델 오류**: `GOOGLE_CLOUD_PROJECT` 및 인증 확인

### 환경 설정 문제

1. **Vertex AI (기본값)**:
   - `gcloud auth application-default login` 확인
   - 프로젝트 ID는 자격 증명에서 자동 감지

2. **AI Studio**:
   - `GOOGLE_API_KEY=...`가 포함된 `.env` 파일 생성
   - `GOOGLE_GENAI_USE_VERTEXAI=FALSE` 설정

## 향후 개선 아이디어

README.md 가치 선언을 기반으로:
- **트렌딩 주제 스캐너**: 사이트 전반의 트렌딩 주제를 연구하는 에이전트
- **MCP 서버 통합**: Model Context Protocol 서버에 연결
- **SEO 최적화 에이전트**: 검색 엔진에 맞게 분석 및 최적화
- **다중 형식 내보내기**: HTML, PDF, Medium 형식 지원
- **콘텐츠 캘린더**: 일정 관리 및 계획 에이전트
- **성능 분석**: 참여 지표 추적

## 빠른 참조

### 파일 위치
- 메인 에이전트: `blogger_agent/agent.py:30` (`interactive_blogger_agent`)
- 루트 내보내기: `blogger_agent/__init__.py:1` (`root_agent`)
- 구성: `blogger_agent/config.py:46` (`config`)
- 도구: `blogger_agent/tools.py`
- 테스트: `tests/test_agent.py`

### 실행 명령어
```bash
# 인터랙티브 모드
adk web

# 통합 테스트
python -m tests.test_agent

# 의존성 설치
pip install -r requirements.txt
```

### 주요 디자인 패턴
1. **LoopAgent + Validator**: 품질 검사를 통한 견고한 재시도
2. **Session State**: 에이전트가 상태 키를 통해 통신
3. **계층적 위임**: 메인 에이전트가 전문가에게 위임
4. **User-in-the-Loop**: 각 단계에서 반복적 피드백
5. **도구 추상화**: 도구가 외부 작업 처리

---

**최종 업데이트**: 2025-11-15
**ADK 버전**: 1.18.0
**Python 버전**: 3.11.3+

질문이나 기여에 대해서는 [README.md](README.md) 및 [LICENSE](LICENSE)를 참조하세요.
