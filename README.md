## Project Overview - Agent Shutton

NOTE: This is a **sample submssion** for the [Kaggle Agents Intensive Capstone project](https://www.kaggle.com/competitions/agents-intensive-course-capstone-2025/). Use this as a point of reference for structuring your submission. Avoid simply copying and reusing logic and or concepts.

NOTE: This sample submssion was inspired and lifted from the official [ADK-Samples](https://github.com/google/adk-samples/tree/main/python/agents/blog-writer) repository. Special thanks to Pier Paolo Ippolito for his contributions. 

This project contains the core logic for Agent Shutton, a multi-agent system designed to assist users in creating various types of blog posts. The agent is built using Google Agent Development Kit (ADK) and follows a modular architecture.

![Architecture](./thumbnail.png "Optional Title")

### Problem Statement

Writing blogs manually is laborious because it requires significant time investment in research, drafting, editing, and formatting each piece of content from scratch. The repetitive nature of structuring posts and maintaining consistent tone across multiple articles can quickly become mentally exhausting and drain creative energy. Manual blog writing also struggles to scale when content demands increase, forcing writers to choose between quality and quantity or invest in hiring additional staff. Automation can streamline research gathering, generate initial drafts, handle formatting consistency, and maintain publishing schedules, allowing human writers to focus their expertise on strategic direction, creative refinement, and adding unique insights that truly require human judgment.

### Solution Statement

Agents can automatically research topics by gathering information from multiple sources, synthesizing key insights, and identifying trending themes relevant to your target audience. They can generate initial draft outlines or full articles based on specific parameters like tone, length, significantly reducing the time spent on the blank page problem. Additionally, agents can manage the entire publishing workflow by scheduling posts, distributing content across multiple platforms, monitoring performance metrics, and even suggesting improvements based on engagement data—transforming blog management from a manual chore into a streamlined, data-driven process.

### Architecture
Core to Agent Shutton is the `blogger_agent` -- a prime example of a multi-agent system. It's not a monolithic application but an ecosystem of specialized agents, each contributing to a different stage of the blog creation process. This modular approach, facilitated by Google's Agent Development Kit, allows for a sophisticated and robust workflow. The central orchestrator of this system is the `interactive_blogger_agent`.

![Architecture](./flow_adk_web.png "Optional Title")

The `interactive_blogger_agent` is constructed using the `Agent` class from the Google ADK. Its definition highlights several key parameters: the `name`, the `model` it uses for its reasoning capabilities, and a detailed `description` and `instruction` set that governs its behavior. Crucially, it also defines the `sub_agents` it can delegate tasks to and the `tools` it has at its disposal.

The real power of the `blogger_agent` lies in its team of specialized sub-agents, each an expert in its domain.

**Content Strategist: `robust_blog_planner`**

This agent is responsible for creating a well-structured and comprehensive outline for the blog post. If a codebase is provided, it will intelligently incorporate sections for code snippets and technical deep dives. To ensure high-quality output, it's implemented as a `LoopAgent`, a pattern that allows for retries and validation. The `OutlineValidationChecker` ensures that the generated outline meets predefined quality standards.

**Technical Writer: `robust_blog_writer`**

Once the outline is approved, the `robust_blog_writer` takes over. This agent is an expert technical writer, capable of crafting in-depth and engaging articles for a sophisticated audience. It uses the approved outline and codebase summary to generate the blog post, with a strong emphasis on detailed explanations and illustrative code snippets. Like the planner, it's a `LoopAgent` that uses a `BlogPostValidationChecker` to ensure the quality of the written content.

**Editor: `blog_editor`**

The `blog_editor` is a professional technical editor that revises the blog post based on user feedback. This allows for an iterative and collaborative writing process, ensuring the final article meets the user's expectations.

**Social Media Marketer: `social_media_writer`**

To maximize the reach of the created content, the `social_media_writer` generates promotional posts for platforms like Twitter and LinkedIn. This agent is an expert in social media marketing, crafting engaging and platform-appropriate content to drive traffic to the blog post.

### Essential Tools and Utilities

The `blogger_agent` and its sub-agents are equipped with a variety of tools to perform their tasks effectively.

**File Saving (`save_blog_post_to_file`)**

A simple yet essential tool that allows the `interactive_blogger_agent` to export the final blog post to a Markdown file.

**Codebase Analysis (`analyze_codebase`)**

This tool is crucial for generating technically accurate and relevant content. It ingests a directory, traverses its files using `glob` and `os`, and creates a consolidated `codebase_context`. It even handles potential `UnicodeDecodeError` exceptions by attempting to read files with a different encoding, ensuring robustness.

**Validation Checkers (`OutlineValidationChecker`, `BlogPostValidationChecker`)**

These custom `BaseAgent` implementations are a key part of the system's robustness. They check for the presence and validity of the blog outline and post, respectively. If the validation fails, they do nothing, causing the `LoopAgent` to retry. If the validation succeeds, they escalate with `EventActions(escalate=True)`, which signals to the `LoopAgent` that it can proceed. This is a powerful mechanism for ensuring quality and controlling the flow of execution in a multi-agent system.

### Conclusion

The beauty of the `blogger_agent` lies in its iterative and collaborative workflow. The `interactive_blogger_agent` acts as a project manager, coordinating the efforts of its specialized team. It delegates tasks, gathers user feedback, and ensures that each stage of the content creation process is completed successfully. This multi-agent coordination, powered by the Google ADK, results in a system that is modular, reusable, and scalable.

The `blogger_agent` is a compelling demonstration of how multi-agent systems, built with powerful frameworks like Google's Agent Development Kit, can tackle complex, real-world problems. By breaking down the process of technical content creation into a series of manageable tasks and assigning them to specialized agents, it creates a workflow that is both efficient and robust.

### Value Statement

Agent Shutton reduced my blog development time by 6-8 hours per week, enabling me to produce more content at higher quality. I have also been producing blogs across new domains - as the agent drives research that I'd otherwise not be able to do given time constraints and subject matter expertise.

If I had more time I would add an additional agent to scan various sites for trending topics and use that research to inform my blog topics. This would require integrating applicable MCP servers or building custom tools. 

## Installation

This project was built against Python 3.11.3.

It is suggested you create a vitrual environment using your preferred tooling e.g. uv.

Install dependenies e.g. pip install -r requirements.txt

### Running the Agent in ADK Web mode

From the command line of the working directory execute the following command. 

```bash
adk web
```

**Run the integration test:**

```bash
python -m tests.test_agent
```

## Project Structure

The project is organized as follows:

*   `blogger_agent/`: The main Python package for the agent.
    *   `agent.py`: Defines the main `interactive_blogger_agent` and orchestrates the sub-agents.
    *   `sub_agents/`: Contains the individual sub-agents, each responsible for a specific task.
        *   `blog_planner.py`: Generates the blog post outline.
        *   `blog_writer.py`: Writes the blog post.
        *   `blog_editor.py`: Edits the blog post based on user feedback.
        *   `social_media_writer.py`: Generates social media posts.
    *   `tools.py`: Defines the custom tools used by the agents.
    *   `config.py`: Contains the configuration for the agents, such as the models to use.
*   `eval/`: Contains the evaluation framework for the agent.
*   `tests/`: Contains integration tests for the agent.



## Workflow

The `interactive_blogger_agent` follows this workflow:

1.  **Analyze Codebase (Optional):** If the user provides a directory, the agent analyzes the codebase to understand its structure and content.
2.  **Plan:** The agent delegates the task of generating a blog post outline to the `robust_blog_planner`.
3.  **Refine:** The user can provide feedback to refine the outline. The agent continues to refine the outline until it is approved by the user.
4.  **Visuals:** The agent asks the user to choose their preferred method for including visual content.
5.  **Write:** Once the user approves the outline, the agent delegates the task of writing the blog post to the `robust_blog_writer`.
6.  **Edit:** After the first draft is written, the agent presents it to the user and asks for feedback. The `blog_editor` revises the blog post based on the feedback. This process is repeated until the user is satisfied with the result.
7.  **Social Media:** After the user approves the blog post, the agent asks if they want to generate social media posts. If the user agrees, the `social_media_writer` is used.
8.  **Export:** When the user approves the final version, the agent asks for a filename and saves the blog post as a markdown file using the `save_blog_post_to_file` tool.

---

# 한국어 문서

## 프로젝트 개요 - Agent Shutton

참고: 이 프로젝트는 [Kaggle Agents Intensive Capstone 프로젝트](https://www.kaggle.com/competitions/agents-intensive-course-capstone-2025/)를 위한 **샘플 제출물**입니다. 제출물 구조화의 참고 자료로 사용하세요. 로직이나 개념을 단순히 복사하여 재사용하는 것은 피하세요.

참고: 이 샘플 제출물은 공식 [ADK-Samples](https://github.com/google/adk-samples/tree/main/python/agents/blog-writer) 저장소에서 영감을 받고 차용했습니다. Pier Paolo Ippolito의 기여에 특별히 감사드립니다.

이 프로젝트는 다양한 유형의 블로그 포스트 작성을 지원하는 멀티 에이전트 시스템인 Agent Shutton의 핵심 로직을 포함합니다. 이 에이전트는 Google Agent Development Kit(ADK)를 사용하여 구축되었으며 모듈식 아키텍처를 따릅니다.

![아키텍처](./thumbnail.png "선택적 제목")

### 문제 정의

블로그를 수동으로 작성하는 것은 각 콘텐츠에 대한 연구, 초안 작성, 편집 및 형식 지정에 상당한 시간 투자가 필요하기 때문에 힘든 작업입니다. 게시물 구조화와 여러 기사에 걸쳐 일관된 톤을 유지하는 반복적인 작업은 빠르게 정신적으로 지치게 하고 창의적 에너지를 소진시킬 수 있습니다. 수동 블로그 작성은 또한 콘텐츠 수요가 증가할 때 확장하기 어렵고, 작가들이 품질과 양 사이에서 선택하거나 추가 직원 고용에 투자해야 하는 상황을 초래합니다. 자동화는 연구 수집을 간소화하고, 초기 초안을 생성하며, 형식 일관성을 처리하고, 게시 일정을 유지할 수 있어, 인간 작가들이 전략적 방향, 창의적 개선, 그리고 진정으로 인간의 판단이 필요한 고유한 통찰력 추가에 전문성을 집중할 수 있게 합니다.

### 솔루션 설명

에이전트는 여러 소스에서 정보를 수집하고, 주요 통찰력을 종합하며, 타겟 독자와 관련된 트렌딩 주제를 식별함으로써 주제를 자동으로 연구할 수 있습니다. 톤, 길이 등의 특정 매개변수를 기반으로 초기 개요 초안이나 전체 기사를 생성하여 빈 페이지 문제에 소요되는 시간을 크게 줄일 수 있습니다. 또한 에이전트는 게시물 일정 관리, 여러 플랫폼에 걸친 콘텐츠 배포, 성능 메트릭 모니터링, 심지어 참여 데이터를 기반으로 개선 사항 제안까지 전체 게시 워크플로를 관리할 수 있어, 블로그 관리를 수동 작업에서 간소화된 데이터 기반 프로세스로 변환합니다.

### 아키텍처

Agent Shutton의 핵심은 `blogger_agent`입니다 -- 멀티 에이전트 시스템의 대표적인 예입니다. 단일 애플리케이션이 아니라 각각 블로그 생성 프로세스의 다른 단계에 기여하는 전문화된 에이전트의 생태계입니다. Google의 Agent Development Kit을 통해 촉진되는 이 모듈식 접근 방식은 정교하고 견고한 워크플로를 가능하게 합니다. 이 시스템의 중앙 오케스트레이터는 `interactive_blogger_agent`입니다.

![아키텍처](./flow_adk_web.png "선택적 제목")

`interactive_blogger_agent`는 Google ADK의 `Agent` 클래스를 사용하여 구성됩니다. 그 정의는 여러 주요 매개변수를 강조합니다: `name`, 추론 능력에 사용하는 `model`, 그리고 동작을 관리하는 상세한 `description`과 `instruction` 세트입니다. 중요하게도, 작업을 위임할 수 있는 `sub_agents`와 사용 가능한 `tools`도 정의합니다.

`blogger_agent`의 진정한 힘은 각 영역의 전문가인 전문화된 서브 에이전트 팀에 있습니다.

**콘텐츠 전략가: `robust_blog_planner`**

이 에이전트는 블로그 포스트의 잘 구조화되고 포괄적인 개요를 생성할 책임이 있습니다. 코드베이스가 제공되면 코드 스니펫과 기술적 심층 분석을 위한 섹션을 지능적으로 통합합니다. 고품질 출력을 보장하기 위해 재시도와 검증을 허용하는 패턴인 `LoopAgent`로 구현되었습니다. `OutlineValidationChecker`는 생성된 개요가 사전 정의된 품질 표준을 충족하는지 확인합니다.

**기술 작가: `robust_blog_writer`**

개요가 승인되면 `robust_blog_writer`가 인계받습니다. 이 에이전트는 정교한 독자를 위한 심도 있고 매력적인 기사를 작성할 수 있는 전문 기술 작가입니다. 승인된 개요와 코드베이스 요약을 사용하여 블로그 포스트를 생성하며, 상세한 설명과 예시 코드 스니펫에 중점을 둡니다. 계획자와 마찬가지로 `BlogPostValidationChecker`를 사용하여 작성된 콘텐츠의 품질을 보장하는 `LoopAgent`입니다.

**편집자: `blog_editor`**

`blog_editor`는 사용자 피드백을 기반으로 블로그 포스트를 수정하는 전문 기술 편집자입니다. 이를 통해 반복적이고 협업적인 작성 프로세스가 가능하며, 최종 기사가 사용자의 기대를 충족하도록 보장합니다.

**소셜 미디어 마케터: `social_media_writer`**

생성된 콘텐츠의 도달 범위를 극대화하기 위해 `social_media_writer`는 Twitter 및 LinkedIn과 같은 플랫폼용 홍보 게시물을 생성합니다. 이 에이전트는 블로그 포스트로 트래픽을 유도하기 위해 매력적이고 플랫폼에 적합한 콘텐츠를 작성하는 소셜 미디어 마케팅 전문가입니다.

### 필수 도구 및 유틸리티

`blogger_agent`와 그 서브 에이전트들은 작업을 효과적으로 수행하기 위한 다양한 도구를 갖추고 있습니다.

**파일 저장 (`save_blog_post_to_file`)**

`interactive_blogger_agent`가 최종 블로그 포스트를 Markdown 파일로 내보낼 수 있게 하는 간단하지만 필수적인 도구입니다.

**코드베이스 분석 (`analyze_codebase`)**

이 도구는 기술적으로 정확하고 관련성 있는 콘텐츠를 생성하는 데 중요합니다. 디렉토리를 수집하고, `glob`과 `os`를 사용하여 파일을 탐색하며, 통합된 `codebase_context`를 생성합니다. 다른 인코딩으로 파일을 읽으려고 시도하여 잠재적인 `UnicodeDecodeError` 예외를 처리하여 견고성을 보장합니다.

**검증 체커 (`OutlineValidationChecker`, `BlogPostValidationChecker`)**

이러한 커스텀 `BaseAgent` 구현은 시스템의 견고성의 핵심 부분입니다. 각각 블로그 개요와 포스트의 존재와 유효성을 확인합니다. 검증이 실패하면 아무 작업도 하지 않아 `LoopAgent`가 재시도하도록 합니다. 검증이 성공하면 `EventActions(escalate=True)`로 에스컬레이션하여 `LoopAgent`에게 진행할 수 있다는 신호를 보냅니다. 이는 품질을 보장하고 멀티 에이전트 시스템에서 실행 흐름을 제어하는 강력한 메커니즘입니다.

### 결론

`blogger_agent`의 아름다움은 반복적이고 협업적인 워크플로에 있습니다. `interactive_blogger_agent`는 프로젝트 관리자로서 전문화된 팀의 노력을 조정합니다. 작업을 위임하고, 사용자 피드백을 수집하며, 콘텐츠 생성 프로세스의 각 단계가 성공적으로 완료되도록 보장합니다. Google ADK로 구동되는 이 멀티 에이전트 조정은 모듈식이고, 재사용 가능하며, 확장 가능한 시스템을 만듭니다.

`blogger_agent`는 Google의 Agent Development Kit와 같은 강력한 프레임워크로 구축된 멀티 에이전트 시스템이 복잡한 실제 문제를 어떻게 해결할 수 있는지를 보여주는 설득력 있는 데모입니다. 기술 콘텐츠 생성 프로세스를 일련의 관리 가능한 작업으로 분해하고 이를 전문화된 에이전트에 할당함으로써 효율적이고 견고한 워크플로를 만듭니다.

### 가치 제안

Agent Shutton은 주당 블로그 개발 시간을 6-8시간 단축시켜 더 높은 품질의 콘텐츠를 더 많이 생산할 수 있게 했습니다. 또한 새로운 도메인에서도 블로그를 생산하고 있습니다 - 에이전트가 시간 제약과 주제 전문 지식 때문에 제가 할 수 없었던 연구를 수행하기 때문입니다.

더 많은 시간이 있다면 다양한 사이트에서 트렌딩 주제를 스캔하고 그 연구를 사용하여 블로그 주제를 알리는 추가 에이전트를 추가할 것입니다. 이를 위해서는 적용 가능한 MCP 서버를 통합하거나 커스텀 도구를 구축해야 합니다.

## 설치

이 프로젝트는 Python 3.11.3을 기준으로 구축되었습니다.

선호하는 도구(예: uv)를 사용하여 가상 환경을 만드는 것이 좋습니다.

의존성을 설치하세요. 예: pip install -r requirements.txt

### ADK 웹 모드에서 에이전트 실행

작업 디렉토리의 명령줄에서 다음 명령을 실행하세요.

```bash
adk web
```

**통합 테스트 실행:**

```bash
python -m tests.test_agent
```

## 프로젝트 구조

프로젝트는 다음과 같이 구성되어 있습니다:

*   `blogger_agent/`: 에이전트를 위한 메인 Python 패키지.
    *   `agent.py`: 메인 `interactive_blogger_agent`를 정의하고 서브 에이전트를 조율합니다.
    *   `sub_agents/`: 각각 특정 작업을 담당하는 개별 서브 에이전트를 포함합니다.
        *   `blog_planner.py`: 블로그 포스트 개요를 생성합니다.
        *   `blog_writer.py`: 블로그 포스트를 작성합니다.
        *   `blog_editor.py`: 사용자 피드백을 기반으로 블로그 포스트를 편집합니다.
        *   `social_media_writer.py`: 소셜 미디어 게시물을 생성합니다.
    *   `tools.py`: 에이전트가 사용하는 커스텀 도구를 정의합니다.
    *   `config.py`: 사용할 모델과 같은 에이전트의 구성을 포함합니다.
*   `eval/`: 에이전트를 위한 평가 프레임워크를 포함합니다.
*   `tests/`: 에이전트를 위한 통합 테스트를 포함합니다.

## 워크플로

`interactive_blogger_agent`는 다음 워크플로를 따릅니다:

1.  **코드베이스 분석 (선택사항):** 사용자가 디렉토리를 제공하면 에이전트는 코드베이스를 분석하여 구조와 내용을 이해합니다.
2.  **계획:** 에이전트는 블로그 포스트 개요 생성 작업을 `robust_blog_planner`에 위임합니다.
3.  **개선:** 사용자는 개요를 개선하기 위한 피드백을 제공할 수 있습니다. 에이전트는 사용자가 승인할 때까지 개요를 계속 개선합니다.
4.  **시각 자료:** 에이전트는 사용자에게 시각 콘텐츠 포함을 위한 선호 방법을 선택하도록 요청합니다.
5.  **작성:** 사용자가 개요를 승인하면 에이전트는 블로그 포스트 작성 작업을 `robust_blog_writer`에 위임합니다.
6.  **편집:** 첫 번째 초안이 작성되면 에이전트는 사용자에게 제시하고 피드백을 요청합니다. `blog_editor`는 피드백을 기반으로 블로그 포스트를 수정합니다. 이 프로세스는 사용자가 결과에 만족할 때까지 반복됩니다.
7.  **소셜 미디어:** 사용자가 블로그 포스트를 승인하면 에이전트는 소셜 미디어 게시물을 생성할지 물어봅니다. 사용자가 동의하면 `social_media_writer`가 사용됩니다.
8.  **내보내기:** 사용자가 최종 버전을 승인하면 에이전트는 파일명을 요청하고 `save_blog_post_to_file` 도구를 사용하여 블로그 포스트를 마크다운 파일로 저장합니다.

