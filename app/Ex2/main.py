from pathlib import Path

from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import (
    StrOutputParser,
    JsonOutputParser
)
from sqlalchemy.exc import SQLAlchemyError

from app.model import model
from app.Ex2.prompt import (
    SQL_GENERATION_PROMPT,
    SYNTACTIC_REFLECTION_PROMPT,
    SEMANTIC_REFLECTION_PROMPT
)


def clean_sql(sql: str) -> str:
    sql = sql.strip()

    if sql.startswith("```sql"):
        sql = sql[6:]

    elif sql.startswith("```"):
        sql = sql[3:]

    if sql.endswith("```"):
        sql = sql[:-3]

    return sql.strip()


def execute_sql_safely(
    db: SQLDatabase,
    query: str
):

    try:
        result = db.run(query)

        return {
            "success": True,
            "result": result,
            "error": None
        }

    except SQLAlchemyError as e:
        return {
            "success": False,
            "result": None,
            "error": str(e)
        }


def fix_sql_syntax(
    schema: str,
    question: str,
    sql: str,
    error: str
) -> str:


    syntactic_reflection_chain = (
        SYNTACTIC_REFLECTION_PROMPT
        | model
        | StrOutputParser()
    )

    corrected_sql = syntactic_reflection_chain.invoke(
        {
            "schema": schema,
            "question": question,
            "sql": sql,
            "error": error
        }
    )

    return clean_sql(corrected_sql)


def execute_with_syntactic_reflection(
    db: SQLDatabase,
    schema: str,
    question: str,
    sql: str,
    max_attempts: int = 3
):


    current_sql = sql

    for attempt in range(1, max_attempts + 1):

        print(f"\n--- SQL Attempt {attempt} ---")
        print(current_sql)

        execution = execute_sql_safely(
            db,
            current_sql
        )

        if execution["success"]:

            print("\nSQL executed successfully.")

            return {
                "success": True,
                "sql": current_sql,
                "result": execution["result"],
                "error": None,
                "attempts": attempt
            }

        print("\nSQL execution failed.")
        print(execution["error"])

        if attempt == max_attempts:

            return {
                "success": False,
                "sql": current_sql,
                "result": None,
                "error": execution["error"],
                "attempts": attempt
            }

        print("\nRunning syntactic reflection...")

        current_sql = fix_sql_syntax(
            schema=schema,
            question=question,
            sql=current_sql,
            error=execution["error"]
        )

    return {
        "success": False,
        "sql": current_sql,
        "result": None,
        "error": "Maximum attempts reached.",
        "attempts": max_attempts
    }


def reflect_and_fix_semantic_issue(
    schema: str,
    question: str,
    sql: str,
    result
):
    semantic_reflection_chain = (
        SEMANTIC_REFLECTION_PROMPT
        | model
        | JsonOutputParser()
    )

    reflection = semantic_reflection_chain.invoke(
        {
            "schema": schema,
            "question": question,
            "sql": sql,
            "result": result
        }
    )

    return reflection


def execute_with_semantic_reflection(
    db: SQLDatabase,
    schema: str,
    question: str,
    sql: str,
    result
):
    reflection = reflect_and_fix_semantic_issue(
        schema=schema,
        question=question,
        sql=sql,
        result=result
    )

    print("\n--- Semantic Reflection ---")
    print("Correct:", reflection["is_correct"])
    print("Reason:", reflection["reason"])

    if reflection["is_correct"]:

        return {
            "success": True,
            "sql": sql,
            "result": result,
            "corrected": False,
            "reason": reflection["reason"],
            "error": None
        }

    corrected_sql = reflection.get("corrected_sql")

    if not corrected_sql:

        return {
            "success": False,
            "sql": sql,
            "result": None,
            "corrected": False,
            "reason": reflection["reason"],
            "error": "Semantic reflection marked the SQL as incorrect but did not provide corrected SQL."
        }

    corrected_sql = clean_sql(corrected_sql)

    print("\nCorrected Semantic SQL:")
    print(corrected_sql)

    execution = execute_sql_safely(
        db,
        corrected_sql
    )

    if execution["success"]:

        return {
            "success": True,
            "sql": corrected_sql,
            "result": execution["result"],
            "corrected": True,
            "reason": reflection["reason"],
            "error": None
        }

    return {
        "success": False,
        "sql": corrected_sql,
        "result": None,
        "corrected": True,
        "reason": reflection["reason"],
        "error": execution["error"]
    }


def main():


    base_dir = Path(__file__).resolve().parent

    db_path = base_dir / "database" / "bank_database.db"

    db = SQLDatabase.from_uri(
        f"sqlite:///{db_path}"
    )


    schema = db.get_table_info()

    sql_generation_chain = (
        SQL_GENERATION_PROMPT
        | model
        | StrOutputParser()
    )

    question = "موجودی حساب‌های علی رضایی چقدر است؟"

    print("\n================ QUESTION ================")
    print(question)


    sql = sql_generation_chain.invoke(
        {
            "schema": schema,
            "question": question
        }
    )

    sql = clean_sql(sql)

    print("\n================ GENERATED SQL ================")
    print(sql)


    syntactic_result = execute_with_syntactic_reflection(
        db=db,
        schema=schema,
        question=question,
        sql=sql,
        max_attempts=3
    )

    if not syntactic_result["success"]:

        print("\n================ FINAL RESULT ================")
        print("Success:", False)
        print("Final SQL:", syntactic_result["sql"])
        print("Error:", syntactic_result["error"])
        print("Attempts:", syntactic_result["attempts"])

        return


    semantic_result = execute_with_semantic_reflection(
        db=db,
        schema=schema,
        question=question,
        sql=syntactic_result["sql"],
        result=syntactic_result["result"]
    )


    print("\n================ FINAL RESULT ================")

    print("Success:", semantic_result["success"])
    print("Final SQL:", semantic_result["sql"])
    print("Result:", semantic_result["result"])
    print("Corrected:", semantic_result["corrected"])
    print("Reason:", semantic_result["reason"])

    if not semantic_result["success"]:
        print("Error:", semantic_result["error"])


def get_database() -> SQLDatabase:
    base_dir = Path(__file__).resolve().parent
    db_path = base_dir / "database" / "bank_database.db"

    return SQLDatabase.from_uri(
        f"sqlite:///{db_path}"
    )



def ask_question(
    question: str,
    max_syntactic_attempts: int = 3
):

    db = get_database()

    schema = db.get_table_info()

    sql_generation_chain = (
        SQL_GENERATION_PROMPT
        | model
        | StrOutputParser()
    )

    sql = sql_generation_chain.invoke(
        {
            "schema": schema,
            "question": question
        }
    )

    sql = clean_sql(sql)

    syntactic_result = execute_with_syntactic_reflection(
        db=db,
        schema=schema,
        question=question,
        sql=sql,
        max_attempts=max_syntactic_attempts
    )

    if not syntactic_result["success"]:
        return {
            "success": False,
            "question": question,
            "sql": syntactic_result["sql"],
            "result": None,
            "error": syntactic_result["error"],
            "stage": "syntactic_reflection",
            "attempts": syntactic_result["attempts"],
            "corrected": False
        }

    semantic_result = execute_with_semantic_reflection(
        db=db,
        schema=schema,
        question=question,
        sql=syntactic_result["sql"],
        result=syntactic_result["result"]
    )

    return {
        "success": semantic_result["success"],
        "question": question,
        "sql": semantic_result["sql"],
        "result": semantic_result["result"],
        "error": semantic_result["error"],
        "stage": "semantic_reflection",
        "attempts": syntactic_result["attempts"],
        "corrected": semantic_result["corrected"],
        "reason": semantic_result["reason"]
    }

if __name__ == "__main__":
    main()