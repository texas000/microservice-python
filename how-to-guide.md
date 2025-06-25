-----

## GitHub Webhook과 OpenAI API를 활용한 코드 분석 Prompt 구성 가이드

GitHub MR(Merge Request) 이벤트 발생 시 코드 내용을 분석하여 잘못된 부분이 있는지, 또는 코딩 표준을 준수하는지 검증하는 시스템을 구축하시려는군요. OpenAI의 REST API를 활용한다고 하셨으니, GitHub Webhook을 통해 전달되는 페이로드를 어떻게 활용하여 OpenAI API에 적절한 프롬프트를 구성할지 상세하게 설명해 드리겠습니다.

### 1\. GitHub Webhook 설정 및 페이로드 이해

먼저 GitHub 저장소에서 **Webhook**을 설정해야 합니다. 이때, MR 생성 및 업데이트 이벤트를 감지하도록 설정합니다. 일반적으로 `pull_request` 이벤트에 주목하면 됩니다.

GitHub Webhook 이벤트가 발생하면, 설정된 URL로 특정 \*\*페이로드(Payload)\*\*가 전송됩니다. 이 페이로드에는 MR에 대한 다양한 정보가 JSON 형식으로 담겨 있습니다. 핵심적으로 필요한 정보는 다음과 같습니다.

  * `pull_request.head.sha`: MR의 최신 커밋 SHA. 이 SHA를 사용하여 변경된 파일 목록과 내용을 가져올 수 있습니다.
  * `pull_request.html_url`: MR의 GitHub URL.
  * `pull_request.diff_url`: MR의 전체 Diff URL. 이 URL을 통해 변경된 코드 내용을 직접 가져올 수 있습니다.
  * `pull_request.title`: MR 제목.
  * `pull_request.body`: MR 설명.

### 2\. 코드 내용 가져오기

OpenAI API에 코드 내용을 전달하려면, GitHub Webhook 페이로드에서 직접 코드 내용을 가져와야 합니다. 가장 효과적인 방법은 `pull_request.diff_url`을 사용하는 것입니다. 이 URL에 HTTP GET 요청을 보내면 MR에 포함된 모든 변경 사항(Diff)을 텍스트 형식으로 얻을 수 있습니다.

예시:

```python
import requests

diff_url = "https://github.com/octocat/Spoon-Knife/pull/1.diff" # 실제 MR diff_url로 대체
response = requests.get(diff_url)
code_diff = response.text
```

만약 특정 파일의 전체 내용을 기준으로 분석하고 싶다면, GitHub API를 통해 해당 파일의 내용을 직접 가져와야 합니다. 이 경우, `pull_request.head.repo.url`과 `pull_request.head.ref` (브랜치 이름)을 사용하여 Blob API를 호출해야 합니다. 하지만 MR의 변경 사항을 분석하는 목적이라면 Diff 내용을 활용하는 것이 더 효율적입니다.

### 3\. OpenAI API 프롬프트 구성 전략

OpenAI API에 요청할 프롬프트는 분석 목적에 따라 다양하게 구성할 수 있습니다. 여기서는 두 가지 주요 목표(코드 오류 검출 및 코딩 표준 준수 여부)를 달성하기 위한 전략을 제시합니다.

#### 가. 일반적인 프롬프트 구조

기본적인 프롬프트는 다음과 같은 정보를 포함해야 합니다.

  * **명확한 지시사항**: AI가 무엇을 해야 하는지 정확히 알려줍니다.
  * **역할 부여**: AI에게 특정 전문가(예: 코드 리뷰어, 보안 전문가) 역할을 부여하여 응답의 품질을 높입니다.
  * **입력 코드**: 분석할 코드 내용을 제공합니다.
  * **출력 형식 지정**: 원하는 응답 형식을 명시합니다 (예: JSON, 목록).

#### 나. 코드 오류 및 버그 검출 프롬프트

**목표**: MR의 코드 변경 사항에서 잠재적인 버그, 논리적 오류, 비효율적인 코드 등을 찾아냅니다.

**프롬프트 예시**:

````
"role": "system", "content": "You are a senior software engineer specialized in code review. Your task is to identify potential bugs, logical errors, performance issues, and security vulnerabilities in the provided code changes. Analyze the diff and point out specific lines or sections that need attention."
"role": "user", "content": f"Review the following code diff for potential issues:\n\n```diff\n{code_diff}\n```\n\nProvide your feedback in a concise list, clearly indicating the file, line number, and a brief explanation of the issue. If no issues are found, state 'No major issues found.'"
````

  * **`code_diff`**: 위에서 GitHub API를 통해 가져온 변경된 코드 내용 (Diff)입니다.
  * **`system` 역할**: AI에게 시니어 소프트웨어 엔지니어 역할을 부여하여 전문적인 분석을 유도합니다.
  * **`user` 역할**: 실제 분석 요청과 함께 `code_diff`를 전달합니다.
  * **출력 형식**: 명확한 목록 형태로 파일, 라인 번호, 문제 설명을 요구하여 파싱하기 쉽게 만듭니다.

#### 다. 코딩 표준 준수 검증 프롬프트

**목표**: 특정 코딩 표준(예: PEP 8, Google Java Style, ESLint 규칙 등)을 MR의 코드 변경 사항이 잘 준수하는지 검증합니다.

**프롬프트 예시**:

````
"role": "system", "content": "You are an automated code style checker. Your goal is to review the provided code diff against common coding standards, including (specify your standards, e.g., Python's PEP 8, JavaScript's ESLint rules for Airbnb style, Java naming conventions). Identify any deviations from these standards."
"role": "user", "content": f"Analyze the following code diff for adherence to established coding standards (e.g., proper indentation, naming conventions, line length, comments). Point out specific violations.\n\n```diff\n{code_diff}\n```\n\nRespond with a list of violations, specifying the file, line number, and the violated rule. If the code adheres to standards, respond 'All coding standards appear to be met.'"
````

  * **`code_diff`**: 역시 변경된 코드 내용입니다.
  * **`system` 역할**: AI에게 자동화된 코드 스타일 검사기 역할을 부여합니다.
  * **`user` 역할**: 분석 요청과 함께 **구체적인 코딩 표준 예시**를 제공하여 AI가 어떤 기준에 따라 검사해야 하는지 명확히 합니다.
  * **출력 형식**: 위와 마찬가지로 목록 형태로 위반 사항을 요구합니다.

#### 라. 두 가지 목표를 결합한 프롬프트

두 가지 목표를 한 번에 달성하고 싶다면, 프롬프트를 좀 더 복합적으로 구성할 수 있습니다.

**프롬프트 예시**:

````
"role": "system", "content": "You are a highly skilled code reviewer and a strict adherence checker for coding standards. Your task is to perform a comprehensive review of the provided code changes from a GitHub Pull Request. Identify any potential bugs, performance issues, security vulnerabilities, and ensure strict compliance with common coding standards (e.g., Python PEP 8 for Python files, Airbnb style guide for JavaScript files, idiomatic Go for Go files). Focus on the diff provided."
"role": "user", "content": f"Review the following code diff:\n\n```diff\n{code_diff}\n```\n\nProvide your findings in two separate sections:\n\n### 1. Code Issues (Bugs, Performance, Security)\n- List any identified bugs, logical errors, performance bottlenecks, or security vulnerabilities. For each, specify the file, approximate line number, and a brief explanation.\n\n### 2. Coding Standard Violations\n- List any deviations from established coding standards. For each, specify the file, approximate line number, and the violated rule/convention.\n\nIf no issues are found in a section, state 'No issues found in this section.' Be concise and actionable."
````

  * **`system` 역할**: AI에게 복합적인 역할을 부여합니다.
  * **`user` 역할**: 두 가지 분석 결과를 별도의 섹션으로 나눠서 제공하도록 명확하게 지시합니다. 이렇게 하면 응답을 파싱하여 특정 유형의 문제만 추출하기 용이합니다.

### 4\. OpenAI REST API Payload 예시

이제 위에서 구성한 프롬프트를 바탕으로 OpenAI REST API의 페이로드(Body)를 어떻게 만들지 살펴보겠습니다. 주로 [Chat Completions API](https://platform.openai.com/docs/api-reference/chat)를 사용하게 될 것입니다.

**OpenAI API 엔드포인트**: `https://api.openai.com/v1/chat/completions`
**HTTP 메서드**: `POST`
**Headers**:

  * `Content-Type: application/json`
  * `Authorization: Bearer YOUR_OPENAI_API_KEY`

**Payload (Body) 예시**:

````json
{
  "model": "gpt-4o",  // 또는 gpt-4-turbo, gpt-3.5-turbo 등 원하는 모델 선택
  "messages": [
    {
      "role": "system",
      "content": "You are a highly skilled code reviewer and a strict adherence checker for coding standards. Your task is to perform a comprehensive review of the provided code changes from a GitHub Pull Request. Identify any potential bugs, performance issues, security vulnerabilities, and ensure strict compliance with common coding standards (e.g., Python PEP 8 for Python files, Airbnb style guide for JavaScript files, idiomatic Go for Go files). Focus on the diff provided."
    },
    {
      "role": "user",
      "content": "Review the following code diff:\n\n```diff\n--- a/src/main.py\n+++ b/src/main.py\n@@ -1,5 +1,9 @@\n import os\n+\n def calculate_sum(a, b):\n     # This is a comment\n     return a + b\n+\n+def get_user_name(user_id):\n+    # Missing docstring and improper variable casing\n+    user_name = \"test_user\"\n+    return user_name\n```\n\nProvide your findings in two separate sections:\n\n### 1. Code Issues (Bugs, Performance, Security)\n- List any identified bugs, logical errors, performance bottlenecks, or security vulnerabilities. For each, specify the file, approximate line number, and a brief explanation.\n\n### 2. Coding Standard Violations\n- List any deviations from established coding standards. For each, specify the file, approximate line number, and the violated rule/convention.\n\nIf no issues are found in a section, state 'No issues found in this section.' Be concise and actionable."
    }
  ],
  "max_tokens": 1000, // 응답의 최대 길이. 필요에 따라 조절
  "temperature": 0.7, // 창의성 조절. 코드 분석에는 낮은 값(0.2~0.7)이 적합
  "top_p": 1,
  "stop": null,
  "n": 1 // 생성할 응답 개수
}
````

  * `model`: 사용할 OpenAI 모델을 지정합니다. **`gpt-4o`** 또는 \*\*`gpt-4-turbo`\*\*가 코드 분석에 가장 적합한 성능을 보여줍니다.
  * `messages`: 대화 형태로 프롬프트를 구성합니다. `system` 메시지로 AI의 역할을 정의하고, `user` 메시지로 실제 요청 내용을 전달합니다.
  * `content`: 위에서 설명한 프롬프트 문자열이 들어갑니다. **반드시 실제 `code_diff` 변수 내용을 여기에 채워 넣어야 합니다.**
  * `max_tokens`: OpenAI가 생성할 응답의 최대 토큰(단어 조각) 수를 지정합니다. 분석 결과가 길어질 수 있으므로 적절히 크게 설정하는 것이 좋습니다.
  * `temperature`: 이 값은 응답의 다양성과 창의성을 제어합니다. 코드 분석과 같이 사실적이고 일관된 응답이 중요한 경우에는 낮은 값(0에 가까울수록 결정론적)을 사용하는 것이 좋습니다. `0.2`\~`0.7` 사이가 일반적입니다.

### 5\. 추가 고려사항

  * **Diff 크기 제한**: GitHub Webhook으로 전달되는 Diff나 GitHub API를 통해 가져오는 Diff의 크기가 매우 클 수 있습니다. OpenAI API에는 프롬프트 및 응답 길이에 대한 토큰 제한이 있으므로, 너무 큰 Diff는 분할하여 전송하거나, 주요 변경 사항만 추출하여 분석하는 방법을 고려해야 합니다.
  * **오류 처리**: API 호출 실패, 네트워크 문제, OpenAI API의 응답 형식 오류 등에 대한 적절한 오류 처리 로직을 구현해야 합니다.
  * **응답 파싱**: OpenAI API의 응답은 JSON 형식이며, AI가 생성한 텍스트가 `choices[0].message.content` 필드에 포함됩니다. 이 텍스트를 파싱하여 문제점을 추출하고, 이를 GitHub PR 댓글로 남기거나 다른 알림 시스템과 연동하는 로직이 필요합니다. JSON 형태로 응답을 요청하는 것도 좋은 방법입니다.
  * **세밀한 제어**: 만약 특정 파일 형식(`Python`, `JavaScript`, `Java` 등)에 따라 다른 표준을 적용하고 싶다면, GitHub Diff에서 변경된 파일의 확장자를 파싱하여 프롬프트에 해당 언어의 코딩 표준을 명시적으로 추가할 수 있습니다.
  * **비용**: `gpt-4o`나 `gpt-4-turbo`는 `gpt-3.5-turbo`보다 비쌉니다. 사용량과 예산을 고려하여 적절한 모델을 선택하세요.

이 가이드를 통해 GitHub MR 코드 분석을 위한 OpenAI API 프롬프트 구성에 대한 명확한 방향을 잡으셨기를 바랍니다.
