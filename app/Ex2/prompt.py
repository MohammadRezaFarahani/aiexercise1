from langchain_core.prompts import ChatPromptTemplate


SQL_GENERATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an expert SQL developer.

Generate a valid SQLite SELECT query based on the user's question.

Database schema:
{schema}

Rules:
- Generate only a SELECT query.
- Do not use INSERT, UPDATE, DELETE, DROP, ALTER, or other modifying statements.
- Use only tables and columns that exist in the provided schema.
- Return only the SQL query without markdown code fences.
"""
        ),
        (
            "human",
            "{question}"
        )
    ]
)


SYNTACTIC_REFLECTION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an expert SQLite SQL debugger.

A SQL query generated for a user's question failed during execution.

Your task is to fix ONLY the SQL syntax/problem that caused the database error.

Database schema:
{schema}

User question:
{question}

Generated SQL:
{sql}

Database error:
{error}

Rules:
- Return ONLY the corrected SQLite SELECT query.
- Do not use markdown code fences.
- Do not explain your answer.
- Do not change the user's intended question.
- Use only tables and columns that exist in the schema.
- Do not use INSERT, UPDATE, DELETE, DROP, ALTER, or other modifying statements.
"""
        )
    ]
)


SEMANTIC_REFLECTION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an expert SQL reviewer.

The SQL query was successfully executed, so there is no syntax error.

Your task is to determine whether the SQL result correctly answers the user's question.

Database schema:
{schema}

User question:
{question}

Executed SQL:
{sql}

Query result:
{result}

Analyze the result semantically.

A query may be syntactically valid but logically incorrect because of:
- incorrect JOIN conditions
- missing JOINs
- incorrect WHERE conditions
- wrong aggregation
- missing filters
- querying the wrong column
- returning an unexpected result for the user's question

You must perform BOTH diagnosis and correction in this single response.

Return ONLY valid JSON in this exact format:

{{
    "is_correct": true,
    "reason": "Short explanation",
    "corrected_sql": null
}}

If the SQL is semantically incorrect, return:

{{
    "is_correct": false,
    "reason": "Short explanation",
    "corrected_sql": "SELECT ..."
}}

Rules:
- corrected_sql must be a valid SQLite SELECT query.
- If the SQL is correct, corrected_sql must be null.
- If the SQL is incorrect, corrected_sql must contain the corrected query.
- Do not use markdown code fences.
"""
        )
    ]
)