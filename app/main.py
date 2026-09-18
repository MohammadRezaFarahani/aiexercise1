from langchain_core.prompts import ChatPromptTemplate

from app.model import model
from langchain_core.messages import (
    SystemMessage,
    HumanMessage
    )

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant."
        ),
        (
            "human",
            "{question}"
        ),
    ]
)

def main():
    chain = prompt | model
    response = chain.invoke(
        {
            "question": "میتونی یه جمله از علی شریعتی در باره سرمایه گذاری روی طلا در زمان جنگ بگی؟"
        }
    )
    print(response.content)


if __name__ == "__main__":
    main()