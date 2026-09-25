from typing import Literal

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from app.model import model

class SupportTicket(BaseModel):
    category: Literal[
        "authentication",
        "payment",
        "technical",
        "account",
        "other",
    ] = Field(
        description="دسته‌بندی اصلی مشکل مشتری"
    )

    priority: Literal[
        "low",
        "medium",
        "high",
        "critical",
    ] = Field(
        description="اولویت رسیدگی به تیکت"
    )

    sentiment: Literal[
        "positive",
        "negative",
        "neutral",
    ] = Field(
        description="احساس کلی مشتری در پیام"
    )

    summary: str = Field(
        description="خلاصه کوتاه و دقیق مشکل مشتری"
    )

    customer_problem: str = Field(
        description="شرح دقیق مشکلی که مشتری گزارش کرده است"
    )

    suggested_action: str = Field(
        description="اقدام پیشنهادی برای حل یا بررسی مشکل"
    )

    needs_human_agent: bool = Field(
        description=(
            "آیا برای رسیدگی به این تیکت نیاز به دخالت "
            "اپراتور انسانی وجود دارد؟"
        )
    )

def support_ticket_prompt() :
        return ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    """
    You are an expert customer support ticket classifier.

    Your task is to analyze a customer's support message and
    convert it into a structured support ticket.

    Follow these steps:

    STEP 1 - IDENTIFY THE CATEGORY

    Choose exactly one category based only on the customer's message.

    Available categories:

    - authentication:
      Problems related to login, password, authentication,
      verification, or authentication errors.

    - payment:
      Problems related to payments, transactions, charges,
      refunds, invoices, or payment failures.

    - technical:
      Technical problems such as application errors,
      crashes, bugs, performance issues, or system failures.

    - account:
      Problems related to account information, profile,
      account settings, registration, or account management.

    - other:
      Use when the message does not clearly belong to
      any of the categories above.


    STEP 2 - DETERMINE PRIORITY

    Choose the priority based on the severity and urgency
    expressed in the customer's message.

    Use these criteria:

    - critical:
      Severe problems that completely prevent an essential
      service from working or may cause major immediate impact.
      Examples: complete system outage, security incident,
      critical business operation blocked.

    - high:
      Important problems that significantly affect the customer
      and require prompt attention.
      Examples: customer cannot access an important service,
      failed important payment, or a major technical failure.

    - medium:
      Problems that affect the customer but have a workaround
      or are not immediately blocking an important activity.

    - low:
      General questions, minor issues, requests for information,
      or problems with little impact.

    Do not assign priority based only on emotional language.
    Consider the actual impact and urgency described in the message.


    STEP 3 - DETERMINE SENTIMENT

    Choose exactly one:

    - positive
    - negative
    - neutral

    Base sentiment only on the customer's expressed attitude.


    STEP 4 - SUMMARIZE THE MESSAGE

    Create a short and accurate summary of the customer's issue.

    Do not add information that is not present in the message.


    STEP 5 - IDENTIFY THE CUSTOMER'S PROBLEM

    Describe exactly what problem the customer is experiencing.

    Use only evidence from the customer's message.


    STEP 6 - SUGGEST AN ACTION

    Suggest a reasonable first troubleshooting or support action
    based on the reported problem.

    Do not claim that an action has already been performed.

    Do not invent technical details that are not supported
    by the customer's message.


    STEP 7 - HUMAN AGENT

    Set needs_human_agent to true when the issue requires
    manual investigation, account-specific action, escalation,
    or when automated troubleshooting is unlikely to be sufficient.

    Otherwise set it to false.


    IMPORTANT RULES:

    - Use only information supported by the customer's message.
    - Do not invent missing information.
    - Do not assume facts that are not present.
    - Return exactly one category.
    - Return exactly one priority.
    - Return exactly one sentiment.
    - Return the output according to the provided schema.
    """
                ),
                HumanMessage(
                    """
                    Analyze the following customer message followed by triple backticks
                
                    ```
                        {message}
                    ```
                    """
                ),
            ]
        )


def create_support_ticket(message: str) -> SupportTicket:
    prompt = support_ticket_prompt()

    structured_model = model.with_structured_output(
        SupportTicket,
        method="function_calling",
    )

    chain = prompt | structured_model

    return chain.invoke(
        {
            "message": message
        }
    )


def main():
    message = """
    سلام، از صبح نمی‌تونم وارد حسابم بشم.
    هر بار رمزمو می‌زنم خطای Authentication failed میده.
    خیلی عجله دارم چون باید امروز گزارشمو ارسال کنم.
    """

    result = create_support_ticket(message)
    print(result)
    print(
        result.model_dump_json(
            indent=2,
            ensure_ascii=False
        )
    )

if __name__ == "__main__":
    main()