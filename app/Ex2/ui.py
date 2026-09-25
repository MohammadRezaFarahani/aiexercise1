import streamlit as st

from main import ask_question

st.set_page_config(
    page_title="Bank SQL Assistant",
    layout="centered"
)


st.title("Bank SQL Assistant")

st.write(
    "سؤال خود را درباره اطلاعات بانکی به زبان طبیعی بپرسید."
)


question = st.text_area(
    "سؤال شما",
    placeholder="مثلاً: موجودی حساب‌های علی رضایی چقدر است؟",
    height=100
)


ask_button = st.button(
    "پرسیدن سؤال",
    type="primary",
    use_container_width=True
)


if ask_button:

    if not question.strip():
        st.warning("لطفاً یک سؤال وارد کنید.")

    else:

        with st.spinner("در حال پردازش سؤال..."):

            result = ask_question(
                question.strip()
            )

        if result["success"]:

            st.success("سؤال با موفقیت پردازش شد.")

            st.subheader("نتیجه")

            st.write(result["result"])

            st.subheader("SQL Generated")

            st.code(
                result["sql"],
                language="sql"
            )

            with st.expander("جزئیات Reflection"):

                st.write(
                    f"**Syntactic Attempts:** "
                    f"{result['attempts']}"
                )

                st.write(
                    f"**Semantic Correction:** "
                    f"{result['corrected']}"
                )

                if result["reason"]:
                    st.write(
                        f"**Reason:** "
                        f"{result['reason']}"
                    )

        else:

            st.error(
                "پردازش سؤال با خطا مواجه شد."
            )

            if result["error"]:
                st.error(
                    result["error"]
                )

            with st.expander("SQL تولید شده"):

                st.code(
                    result["sql"],
                    language="sql"
                )