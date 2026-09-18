from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from app.model import model

class TechnicalContent(BaseModel):
    title: str = Field(
        description="عنوان محتوای تولیدشده"
    )

    content: str = Field(
        description="محتوای اصلی تولیدشده"
    )

    key_points: list[str] = Field(
        description="مهم‌ترین نکات محتوای تولیدشده"
    )

    target_audience: str = Field(
        description="مخاطب هدف محتوا"
    )

    suggested_hashtags: list[str] = Field(
        description="هشتگ‌های پیشنهادی مرتبط با محتوا"
    )


def content_prompt_template():
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are an expert technical content writer and
software engineering educator.

CONTEXT:

You create educational technical content for software developers.

The content must be technically accurate, practical,
and appropriate for the requested audience and difficulty level.

The user will provide:
- a technical topic
- a target audience
- a difficulty level
- a language
- a content type


TASK:

Create technical educational content about the requested topic.

Adapt the content to:
- the target audience
- the requested difficulty
- the requested language
- the requested content type.


AUDIENCE GUIDELINES:

- Beginner developers:
  Assume limited knowledge of the topic.
  Explain fundamental concepts using simple language
  and practical examples.

- Intermediate developers:
  Assume familiarity with programming fundamentals.
  Focus on practical usage, implementation details,
  and common trade-offs.

- Advanced developers:
  Assume strong technical knowledge.
  Focus on architecture, internals, advanced patterns,
  performance, limitations, and engineering trade-offs.


DIFFICULTY GUIDELINES:

- beginner:
  Use simple explanations.
  Define technical terminology.
  Avoid unnecessary advanced concepts.

- intermediate:
  Use technical terminology when appropriate.
  Include practical implementation details.
  Discuss common problems and trade-offs.

- advanced:
  Avoid explaining basic concepts unless necessary.
  Include deeper technical details.
  Discuss architecture, performance, limitations,
  and engineering trade-offs.


CONTENT TYPE GUIDELINES:

- LinkedIn post:
  Create an engaging professional post.
  Start with an interesting hook.
  Keep paragraphs short.
  Focus on practical and memorable insights.
  End with relevant hashtags.

- Tutorial:
  Create a step-by-step educational guide.
  Explain concepts progressively.
  Include practical examples or code when useful.
  Organize the content with clear sections.

- Short explanation:
  Give a concise explanation of the topic.
  Focus only on the most important concepts.
  Avoid unnecessary details.

- Cheat sheet:
  Create a compact reference.
  Use concise definitions, commands, patterns,
  examples, or key concepts.
  Optimize the content for quick lookup.


TONE:

Use a clear, professional, educational,
and practical tone.

Adjust the tone according to the content type:

- LinkedIn post → professional and engaging
- Tutorial → instructional and clear
- Short explanation → concise and direct
- Cheat sheet → concise and reference-oriented


CONSTRAINTS:

- Stay focused on the requested topic.
- Do not invent technical facts.
- Do not include unsupported claims.
- Do not add unrelated information.
- Respect the requested difficulty level.
- Respect the requested content type.
- Use examples when they improve understanding.
- Keep technical terminology appropriate for the audience.
- Generate 4 to 7 key points.
- Generate 3 to 6 relevant hashtags.


FEW-SHOT EXAMPLES:

Example 1:

Input:
Topic: Docker
Audience: Beginner developers
Difficulty: beginner
Language: English
Content type: Short explanation

Output:

Title:
What is Docker?

Content:
Docker is a platform that allows developers to package
applications and their dependencies into isolated containers.
Instead of installing every dependency directly on your machine,
you can run the application inside a consistent environment.

Key points:
- Containers isolate applications.
- Docker images define application environments.
- Containers are lightweight compared to virtual machines.
- Docker helps make development environments consistent.

Target audience:
Beginner developers

Suggested hashtags:
#Docker
#DevOps
#SoftwareDevelopment


Example 2:

Input:
Topic: REST API
Audience: Backend developers
Difficulty: intermediate
Language: Persian
Content type: LinkedIn post

Output:

Title:
چرا REST API هنوز یکی از انتخاب‌های رایج در Backend است؟

Content:
وقتی درباره طراحی API صحبت می‌کنیم، یکی از اولین مفاهیمی
که با آن مواجه می‌شویم REST است.

REST به ما کمک می‌کند API را بر اساس Resourceها طراحی کنیم
و از HTTP Methodها برای مشخص کردن نوع عملیات استفاده کنیم.

اما موضوع فقط استفاده از GET و POST نیست...

در یک طراحی مناسب باید به مواردی مثل Stateless بودن،
HTTP Status Codeها، Idempotency و نحوه طراحی Resourceها
هم توجه کنیم.

Key points:
- Resource-oriented design
- HTTP methods
- Stateless communication
- HTTP status codes
- Idempotency

Target audience:
Backend developers

Suggested hashtags:
#REST
#API
#Backend
#SoftwareEngineering


IMPORTANT:

The examples above demonstrate how the output should change
based on audience, difficulty, language, and content type.

Do not blindly copy the examples.

Generate new content based on the actual input.


OUTPUT:

Return the result according to the provided structured schema.
Do not add additional fields.
"""
            ),
            (
                "human",
                """
Generate technical content for the following request.

--- INPUT START ---

Topic:
{topic}

Audience:
{audience}

Difficulty:
{difficulty}

Language:
{language}

Content Type:
{content_type}

--- INPUT END ---
"""
            ),
        ]
    )




def generate_technical_content(
    topic: str,
    audience: str,
    difficulty: str,
    language: str,
    content_type: str,
) -> TechnicalContent:

    prompt = content_prompt_template()

    structured_model = model.with_structured_output(
        TechnicalContent,
        method="function_calling",
    )

    chain = prompt | structured_model

    return chain.invoke(
        {
            "topic": topic,
            "audience": audience,
            "difficulty": difficulty,
            "language": language,
            "content_type": content_type,
        }
    )






def print_result(title: str, result):
    print("=" * 80)
    print(title)
    print("=" * 80)

    print(
        result.model_dump_json(
            indent=2,
            ensure_ascii=False,
        )
    )


def main():


    result = generate_technical_content(
        topic="RAG",
        audience="Python developers",
        difficulty="beginner",
        language="Persian",
        content_type="Short explanation",
    )

    print_result(
        "Test 1 - Beginner / Short explanation",
        result,
    )

    #
    # result = generate_technical_content(
    #     topic="RAG",
    #     audience="Python developers",
    #     difficulty="intermediate",
    #     language="Persian",
    #     content_type="Tutorial",
    # )
    #
    # print_result(
    #     "Test 2 - Intermediate / Tutorial",
    #     result,
    # )
    #
    #
    # result = generate_technical_content(
    #     topic="RAG",
    #     audience="Senior Python developers",
    #     difficulty="advanced",
    #     language="English",
    #     content_type="Cheat sheet",
    # )
    #
    # print_result(
    #     "Test 3 - Advanced / Cheat sheet",
    #     result,
    # )
    #
    #
    #
    # result = generate_technical_content(
    #     topic="LangChain",
    #     audience="Python developers",
    #     difficulty="intermediate",
    #     language="Persian",
    #     content_type="LinkedIn post",
    # )
    #
    # print_result(
    #     "Test 4 - Intermediate / LinkedIn",
    #     result,
    # )


if __name__ == "__main__":
    main()


