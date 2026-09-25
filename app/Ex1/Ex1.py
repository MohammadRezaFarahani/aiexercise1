from pydantic import BaseModel, Field
from typing import Literal
from app.model import model
from langchain_core.prompts import ChatPromptTemplate

class ReviewAnalysis(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"] = Field(
        description="احساس کلی مشتری نسبت به محصول"
    )

    rating: int | None = Field(
        ge=1,
        le=5,
        description=(
            "امتیاز تقریبی مشتری از 1 تا 5. "
        )
    )

    would_recommend: bool = Field(
        description=(
            "آیا مشتری احتمالاً محصول را پیشنهاد می‌کند. "
            "حتماً باید true یا false باشد و هرگز null نباشد."
        )
    )

    positive_points: list[str] = Field(
        description="مهم‌ترین نکات مثبت ذکرشده در Review"
    )

    negative_points: list[str] = Field(
        description="مهم‌ترین نکات منفی ذکرشده در Review"
    )

    summary: str = Field(
        description="خلاصه کوتاه و دقیق Review"
    )

def chat_prompt_template():
    return ChatPromptTemplate.from_messages(
                        [
                            (
                                    "system",
                                    """""
                        You are an expert e-commerce review analyst.
                    
                        Your task is to analyze the customer's Persian product review
                        and extract only information that is supported by the review.
                    
                        Follow these rules:
                    
                      1. Determine the overall sentiment.

                           The sentiment field is REQUIRED and must ALWAYS contain
                           exactly one of these values:
                        
                           - positive
                           - negative
                           - neutral
                        
                           NEVER return null for sentiment.
                        
                           If the review does not contain enough information to determine
                           a positive or negative sentiment, return neutral.
                                            
                      2. Assign an approximate rating from 1 to 5 only when the
                         review contains enough information to reasonably estimate
                         the customer's satisfaction.
                        
                         If there is not enough information to estimate the rating,
                         return null.
                        
                      3. Determine whether the customer would probably recommend
                           the product.
                        
                           This field is REQUIRED and must always be either true or false.
                        
                           If the customer explicitly recommends the product, return true.
                           If the customer explicitly says the product is not worth buying
                           or should not be recommended, return false.
                        
                           If there is no explicit recommendation:
                           infer the recommendation from the overall sentiment and
                           expressed satisfaction, but do not invent specific facts.
                                            
                        4. Extract the most important positive points mentioned in the review.
                    
                        5. Extract the most important negative points mentioned in the review.
                    
                        6. Write a short and accurate summary of the review.
                    
                        Important rules:
                        - Do not invent information.
                        - Do not assume facts that are not present in the review.
                        - If a specific positive or negative aspect is not mentioned,
                          do not create one.
                        - Keep the extracted points concise.
                        - The summary must only contain information supported by the review.
                        - The rating must be between 1 and 5.
                        - Return the requested structured output only.
                        """
                            ),
                            (
                                    "human",
                                    """
                        Analyze the following customer review followed by triple backticks
                        ```
                        {review}
                        ```
                        """
                            ),
                        ]
    )

old = [
]


reviews = [
    """
    گوشی فوق‌العاده‌ایه. کیفیت صفحه نمایش عالیه،
    باتری خیلی خوب دوام میاره و دوربینش هم عکس‌های باکیفیتی می‌گیره.
    کاملاً راضی هستم و حتماً خریدش رو پیشنهاد می‌کنم.
    """,

    """
    اصلاً از خرید این محصول راضی نیستم.
    باتری خیلی ضعیفه و بعد از چند ساعت استفاده خالی میشه.
    کیفیت بدنه هم نسبت به قیمتش اصلاً مناسب نیست.
    به نظرم ارزش خرید نداره.
    """,

    """
    محصول امروز به دستم رسید.
    ظاهرش مطابق تصاویر سایت است.
    هنوز فرصت نکردم از آن استفاده کنم و درباره کیفیتش نظری ندارم.
    """,

    """
    کیفیت صدای هدفون خیلی خوبه و باتری هم عملکرد قابل قبولی داره.
    اما گوشی‌های هدفون کمی اذیت می‌کنن و بعد از مدتی استفاده گوشم درد می‌گیره.
    در مجموع محصول خوبیه ولی طراحی ارگونومیکش می‌تونست بهتر باشه.
    """,
    """
    امروز به دستم رسید.
    فعلاً فقط بسته‌بندی رو دیدم و هنوز محصول رو باز نکردم.
    """
]



def main():
    prompt = chat_prompt_template()
    structured_model = model.with_structured_output(
        ReviewAnalysis,
        method="function_calling"
    )
    chain = prompt | structured_model

    for review in reviews:
        result = chain.invoke(
            {
                "review": review
            }
        )
        print("=" * 60)
        print(f"Review:\n{review.strip()}")
        print("\nAnalysis:")
        print(result.model_dump_json(indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

