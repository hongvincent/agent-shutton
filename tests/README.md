# Blogger Agent Tests

This directory contains integration tests for the `blogger-agent`.

## How to Run

You can run the test from the root of the project using the following command:

```bash
python -m tests.test_agent
```

## Test Scenario

The `test_agent.py` script is an integration test that runs the `blogger-agent` through a predefined sequence of user queries. This test is designed to simulate a typical conversation with the agent and ensure that it can handle the flow without errors.

The script will print the agent's responses to the console for each query in the sequence.

---

# Blogger Agent 테스트

이 디렉토리는 `blogger-agent`의 통합 테스트를 포함합니다.

## 실행 방법

프로젝트 루트에서 다음 명령어를 사용하여 테스트를 실행할 수 있습니다:

```bash
python -m tests.test_agent
```

## 테스트 시나리오

`test_agent.py` 스크립트는 미리 정의된 사용자 쿼리 시퀀스를 통해 `blogger-agent`를 실행하는 통합 테스트입니다. 이 테스트는 에이전트와의 일반적인 대화를 시뮬레이션하고 오류 없이 흐름을 처리할 수 있는지 확인하도록 설계되었습니다.

스크립트는 시퀀스의 각 쿼리에 대한 에이전트의 응답을 콘솔에 출력합니다.
