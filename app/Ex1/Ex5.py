from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from app.model import model


class ActionItem(BaseModel):
    task: str = Field(
        description="The task that needs to be completed"
    )

    owner: str | None = Field(
        default=None,
        description="The person responsible for the task, or null if not specified"
    )

    deadline: str | None = Field(
        default=None,
        description="The deadline for the task, or null if not specified"
    )


class MeetingAnalysis(BaseModel):
    summary: str = Field(
        description="A concise summary of the meeting"
    )

    decisions: list[str] = Field(
        description="Decisions explicitly agreed upon during the meeting"
    )

    action_items: list[ActionItem] = Field(
        description="Tasks that were explicitly assigned or agreed upon"
    )

    open_questions: list[str] = Field(
        description="Questions that remain unresolved"
    )

    mentioned_people: list[str] = Field(
        description="People explicitly mentioned in the transcript"
    )

    mentioned_projects: list[str] = Field(
        description="Projects explicitly mentioned in the transcript"
    )

    next_steps: list[str] = Field(
        description="Explicitly stated next steps"
    )

    def __str__(self) -> str:

        width = 60
        lines: list[str] = []

        def section(title: str, items: list[str]) -> None:
            lines.append(title)
            if items:
                for i, item in enumerate(items, start=1):
                    lines.append(f"  {i}. {item}")
            else:
                lines.append("  (none)")
            lines.append("")

        lines.append("=" * width)
        lines.append("MEETING ANALYSIS")
        lines.append("=" * width)
        lines.append("")

        lines.append("SUMMARY")
        lines.append(f"  {self.summary}")
        lines.append("")

        section("DECISIONS", self.decisions)

        lines.append("ACTION ITEMS")
        if self.action_items:
            for i, item in enumerate(self.action_items, start=1):
                owner = item.owner or "unassigned"
                deadline = item.deadline or "no deadline"
                lines.append(f"  {i}. {item.task}")
                lines.append(f"     owner: {owner}  |  deadline: {deadline}")
        else:
            lines.append("  (none)")
        lines.append("")

        section("OPEN QUESTIONS", self.open_questions)

        lines.append("MENTIONED PEOPLE")
        lines.append(f"  {', '.join(self.mentioned_people) if self.mentioned_people else '(none)'}")
        lines.append("")

        lines.append("MENTIONED PROJECTS")
        lines.append(f"  {', '.join(self.mentioned_projects) if self.mentioned_projects else '(none)'}")
        lines.append("")

        section("NEXT STEPS", self.next_steps)

        lines.append("=" * width)
        return "\n".join(lines)


# توی این ورژن مشکل اینه که کامل نتونسته بین نصمیم قطعی و تصمیمی که هنوز قطعی نشده تفاوت در نظر بگیره
def meeting_prompt_v1():
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                You are a technical meeting analysis assistant.

                Your task is to analyze a technical meeting transcript
                and extract useful information for the development team.

                Extract the following information:

                - summary
                - decisions
                - action_items
                - open_questions
                - mentioned_people
                - mentioned_projects
                - next_steps

                For each action item, extract:

                - task
                - owner
                - deadline

                IMPORTANT:

                Do not invent or guess information that is not explicitly
                present in the transcript.

                If the owner of a task is not specified, return null.

                If the deadline of a task is not specified, return null.

                Distinguish between decisions and suggestions.

                A suggestion is not necessarily a decision.

                Return the result using the provided structured output schema.
                """
            ),
            (
                "human",
                """
                Analyze the following technical meeting transcript.

                --- TRANSCRIPT START ---

                {transcript}

                --- TRANSCRIPT END ---
                """
            ),
        ]
    )

# توی این ورژن مشکل تصمیم هایی که هنوز قطعی نشدن و درست میکنه مثل redis که هنوز قطعی نیست استفاده ازش
# توی این ورژن چون هیچ تصمیم نهایی گرفته نشده به درستی هیچی برنمیگردونه تو تصمیمات
# ولی هنوز توی تفاوت بین next step و action مشکل داره مثلا  Update API documentation اشتباهی توی next step اومده و یه action هست
def meeting_prompt_v2():

    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are a technical meeting analysis assistant.

Your task is to analyze a technical meeting transcript
and extract useful information for the development team.

Extract the following information:

- summary
- decisions
- action_items
- open_questions
- mentioned_people
- mentioned_projects
- next_steps


ACTION ITEM RULES:

For each action item, extract:

- task
- owner
- deadline

Only extract an action item when the transcript indicates
that a task should actually be performed.

Never infer the owner of a task.

If the owner is not explicitly specified, return null.

Never infer a deadline.

If the deadline is not explicitly specified, return null.


DECISION RULES:

A decision must be an explicit and final agreement
made by the participants.

Do not classify a statement as a decision if the final
outcome still depends on a future investigation, test,
approval, discussion, or condition.

The following are NOT decisions:

- suggestions
- possibilities
- questions
- opinions
- tentative plans
- conditional agreements
- decisions that depend on future results

Examples:

"Maybe we should use Redis."
→ suggestion, NOT a decision.

"Let's use Redis."
→ decision.

"Let's use Redis if the performance investigation
confirms that caching is necessary."
→ conditional statement, NOT a final decision.

"We agreed to use Redis."
→ decision.


DECISIONS vs ACTION ITEMS:

A decision represents a chosen outcome, policy,
approach, or direction.

An action item represents work that a person needs
to perform.

Do not classify an action item as a decision merely
because participants agreed that someone should
perform the task.

Example:

"Sara will check the API performance before Thursday."
→ action item, NOT a decision.

"We will use Redis for caching."
→ decision.


HALLUCINATION RULE:

Do not invent, infer, or guess information that is not
explicitly supported by the transcript.

Every extracted owner and deadline must be directly
supported by the transcript.

Return the result using the provided structured output schema.
"""
            ),
            (
                "human",
                """
Analyze the following technical meeting transcript.

--- TRANSCRIPT START ---

{transcript}

--- TRANSCRIPT END ---
"""
            ),
        ]
    )

def meeting_prompt_v3():
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are a technical meeting analysis assistant.

Your task is to analyze a technical meeting transcript
and produce an accurate, evidence-based report for the team.

Extract the following information:

- summary
- decisions
- action_items
- open_questions
- mentioned_people
- mentioned_projects
- next_steps


==================================================
GENERAL EXTRACTION RULES
==================================================

Use only information supported by the transcript.

Do not invent, assume, infer, or add information that
is not explicitly supported by the transcript.

If information is missing, do not try to fill the gap.

For fields where no information is available, return
an empty list.

For action item owner and deadline:

- If the owner is explicitly specified, extract it.
- If the owner is not explicitly specified, return null.
- If the deadline is explicitly specified, extract it.
- If the deadline is not explicitly specified, return null.


==================================================
DECISION RULES
==================================================

A decision is a final outcome or explicit agreement
reached by the participants.

A decision must represent something that the team has
actually agreed to or finalized.

Do NOT classify the following as decisions:

- suggestions
- opinions
- questions
- possibilities
- tentative plans
- conditional agreements
- unresolved discussions
- future decisions that depend on investigation,
  testing, approval, or additional information

Examples:

"Maybe we should use Redis."
→ NOT a decision.

"I think Redis would be better."
→ NOT a decision.

"Should we use Redis?"
→ NOT a decision.

"Let's use Redis if the performance investigation
confirms that caching is necessary."
→ NOT a final decision because it is conditional.

"We will use Redis for caching."
→ decision.

"Everyone agreed to use Redis."
→ decision.


==================================================
ACTION ITEM RULES
==================================================

An action item represents a task that someone is expected
to perform.

Only extract an action item when the transcript explicitly
indicates that a task should be performed, assigned,
committed to, or agreed upon.

Do NOT create an action item from:

- a problem statement
- a general need
- a goal
- an observation
- a question
- missing information
- something that would merely be reasonable to do

Examples:

"We need more information before deciding."
→ NOT an action item.

"The authentication issue needs more investigation."
→ NOT necessarily an action item unless the transcript
   explicitly assigns or agrees to perform the investigation.

"We should investigate the authentication issue."
→ action item.

"Ali will investigate the authentication issue."
→ action item, owner = Ali.

"Someone should update the documentation."
→ action item, owner = null.


For every action item:

task:
Describe only the explicitly identified task.

owner:
Use the explicitly identified responsible person.
Never infer the owner from context.

deadline:
Use the explicitly stated deadline.
Never infer a deadline from context.


==================================================
ACTION ITEMS vs DECISIONS
==================================================

Do not classify an action item as a decision simply because
the participants agreed that someone should perform it.

A decision represents a chosen outcome, approach, policy,
or direction.

An action item represents work that needs to be performed.

Example:

"Sara will check the API performance before Thursday."
→ action item, NOT a decision.

"We will use Redis for caching."
→ decision.


==================================================
OPEN QUESTIONS
==================================================

Only extract questions that are explicitly asked in the
transcript or are explicitly identified as unresolved.

Do not create a question merely because some information
is missing.

Example:

"Someone should update the documentation."
→ Do NOT create:
   "Who should update the documentation?"

"Who should update the documentation?"
→ open question.


==================================================
NEXT STEPS
==================================================

Only include next steps that are explicitly stated or
clearly agreed upon by the participants.

Do not invent reasonable future steps.

Do not convert every problem or unresolved issue into
a next step.

Example:

"We need more information before deciding."
→ NOT a next step.

"Let's investigate the authentication issue."
→ next step.

"Let's review the performance results in our next meeting."
→ next step.


==================================================
MENTIONED PEOPLE
==================================================

Extract only people explicitly mentioned in the transcript.

Do not invent names.


==================================================
MENTIONED PROJECTS
==================================================

Extract projects, systems, products, or technical initiatives
explicitly mentioned in the transcript.

Do not invent projects.


==================================================
SUMMARY
==================================================

Provide a concise factual summary of the meeting.

Do not introduce conclusions, decisions, or actions that
are not supported by the transcript.


==================================================
OUTPUT
==================================================

Return the result using the provided structured output schema.

Do not add fields outside the schema.
"""
            ),
            (
                "human",
                """
Analyze the following technical meeting transcript.

--- TRANSCRIPT START ---

{transcript}

--- TRANSCRIPT END ---
"""
            ),
        ]
    )



def analyze_meeting_v1(
    transcript: str,
) -> MeetingAnalysis:

    prompt = meeting_prompt_v1()

    structured_model = model.with_structured_output(
        MeetingAnalysis,
        method="function_calling",
    )

    chain = prompt | structured_model

    return chain.invoke(
        {
            "transcript": transcript
        }
    )

def analyze_meeting_v2(
    transcript: str,
) -> MeetingAnalysis:

    prompt = meeting_prompt_v2()

    structured_model = model.with_structured_output(
        MeetingAnalysis,
        method="function_calling",
    )

    chain = prompt | structured_model

    return chain.invoke(
        {
            "transcript": transcript
        }
    )


def analyze_meeting_v3(
    transcript: str,
) -> MeetingAnalysis:

    prompt = meeting_prompt_v3()

    structured_model = model.with_structured_output(
        MeetingAnalysis,
        method="function_calling",
    )

    chain = prompt | structured_model

    return chain.invoke(
        {
            "transcript": transcript
        }
    )


transcript = """
Ali: Let's talk about the payment service.

Sara: The payment API is still slow in some cases.

Reza: Maybe we should use Redis for caching.

Ali: That could help, but I'm not sure yet.
Let's investigate it first.

Sara: I can check the current API performance.

Ali: Good. Please check it before Thursday.

Reza: We also need to update the API documentation.

Sara: Yes, someone should take care of that.

Ali: Let's use Redis for caching if the performance
investigation confirms that caching is necessary.

Reza: What should we do about the authentication issue?

Ali: We need more information before deciding.

Sara: I'll send the performance results to the team
on Thursday.

Ali: Great. Let's review the results in our next meeting.
"""


def main():
    result = analyze_meeting_v3(transcript)
    print(result)


if __name__ == "__main__":
    main()