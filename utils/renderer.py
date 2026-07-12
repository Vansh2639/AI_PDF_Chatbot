import re
import streamlit as st


def render_markdown(answer):

    pattern = r"```(\w+)?\n(.*?)```"

    parts = re.split(pattern, answer, flags=re.DOTALL)

    i = 0

    while i < len(parts):

        if i % 3 == 0:

            if parts[i].strip():
                st.markdown(parts[i])

        else:

            language = parts[i] if parts[i] else "text"

            code = parts[i + 1]

            st.code(code.strip(), language=language)

        i += 3
