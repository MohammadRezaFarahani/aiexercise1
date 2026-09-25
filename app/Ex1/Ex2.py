from pydantic import Field, BaseModel
from langchain_core.prompts import ChatPromptTemplate
from app.model import model

class ResumeInfo(BaseModel):
    name: str | None = Field(
        default=None,
        description="نام کامل فرد. اگر در رزومه ذکر نشده، null باشد."
    )

    email: str | None = Field(
        default=None,
        description="آدرس ایمیل فرد. اگر در رزومه وجود ندارد، null باشد."
    )

    phone: str | None = Field(
        default=None,
        description="شماره تلفن فرد. اگر در رزومه وجود ندارد، null باشد."
    )

    location: str | None = Field(
        default=None,
        description="محل سکونت یا شهر محل زندگی فرد، در صورت ذکر شدن در رزومه."
    )

    education: list[str] = Field(
        default_factory=list,
        description=(
            "سوابق تحصیلی ذکرشده در رزومه، شامل مقطع، رشته و دانشگاه "
            "در صورت وجود. اگر وجود ندارد، لیست خالی باشد."
        )
    )

    skills: list[str] = Field(
        default_factory=list,
        description=(
            "مهارت‌های فرد که در رزومه ذکر شده‌اند. "
            "فقط مهارت‌های موجود در رزومه را استخراج کن."
        )
    )

    years_of_experience: float | None = Field(
        default=None,
        ge=0,
        description=(
            "تعداد تقریبی سال‌های سابقه کاری فرد. "
            "اگر اطلاعات کافی برای محاسبه وجود ندارد، null باشد."
        )
    )

    job_titles: list[str] = Field(
        default_factory=list,
        description=(
            "عنوان‌های شغلی فرد در سوابق کاری. "
            "فقط عناوین ذکرشده در رزومه را استخراج کن."
        )
    )

    programming_languages: list[str] = Field(
        default_factory=list,
        description=(
            "زبان‌های برنامه‌نویسی که فرد در رزومه ذکر کرده است. "
            "اگر هیچ زبان برنامه‌نویسی ذکر نشده، لیست خالی باشد."
        )
    )

    summary: str = Field(
        description=(
            "خلاصه‌ای کوتاه در چند جمله از سابقه کاری، تحصیلات و "
            "مهارت‌های مهم فرد. فقط بر اساس اطلاعات موجود در رزومه."
        )
    )




def resume_prompt_template():
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are an expert Resume Information Extractor.

Your task is to extract structured information from a resume.

Extract information ONLY from the provided resume.

IMPORTANT RULES:

1. Do not invent information.

2. Do not assume information that is not explicitly present
   in the resume.

3. If a field is not mentioned in the resume, return null
   for nullable fields.

4. For list fields, return an empty list when no information
   is available.

5. Keep extracted information faithful to the original resume.

6. Do not add information based on general knowledge or
   assumptions.

FIELD DEFINITIONS:

- name:
  Full name of the candidate.

- email:
  Candidate's email address.

- phone:
  Candidate's phone number.

- location:
  Candidate's city, country, or location if mentioned.

- education:
  Educational background including degree, field of study,
  university, and other relevant education information.

- skills:
  Skills explicitly mentioned in the resume.
  Return them as a list of strings.

- years_of_experience:
  Approximate total years of professional work experience.
  Calculate it only when the resume contains enough information.
  Otherwise return null.

- job_titles:
  Job titles mentioned in the candidate's work experience.
  Return them as a list of strings.

- programming_languages:
  Programming languages explicitly mentioned in the resume.
  Return them as a list of strings.
  Do not treat frameworks or libraries as programming languages.

- summary:
  Write a short summary in a few sentences describing the
  candidate's professional background, education, experience,
  and important skills.

The summary MUST be based only on information available
in the resume.

Do not hallucinate missing information.

Return only the requested structured output.
                """
            ),
            (
                "human",
                """
Extract information from the following resume followed by triple backticks

```
{resume}
```
                """
            ),
        ]
    )


def extract_resume_info(resume: str) -> ResumeInfo:
    prompt = resume_prompt_template()

    structured_model = model.with_structured_output(
        ResumeInfo,
        method="function_calling"
    )

    chain = prompt | structured_model

    return chain.invoke(
        {
            "resume": resume
        }
    )





persian_resume = """
علی رضایی

ایمیل: ali.rezaei@example.com
شماره تماس: 09121234567
محل سکونت: تهران

تحصیلات:
کارشناسی مهندسی کامپیوتر از دانشگاه تهران

سوابق کاری:

Senior Frontend Developer
شرکت فناوری پارس
1400 تا 1404

Frontend Developer
شرکت وب‌گستر
1397 تا 1400

مهارت‌ها:
Angular
React
TypeScript
JavaScript
HTML
CSS
Git
Docker

زبان‌های برنامه‌نویسی:
TypeScript
JavaScript
C#

"""



def main():
    print(extract_resume_info(persian_resume))

if __name__ == "__main__":
    main()

