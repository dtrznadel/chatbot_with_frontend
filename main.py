import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

# Authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False


def login(password):
    # Use password from .env file
    return password == os.getenv("streamlit_password")


if not st.session_state.authenticated:
    st.title("Login")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login(password):
            st.session_state.authenticated = True
        else:
            st.error("Invalid password")
else:
    # Initialize chat history when not present in session
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # get respose from the chat
    def get_response(query, chat_history):
        template = """
        You are a helpful assistant. Answer the following questions.

        Chat history: {chat_history}

        User question: {user_question}
        """
        prompt = ChatPromptTemplate.from_template(template)

        llm = ChatOpenAI()

        chain = prompt | llm | StrOutputParser()

        return chain.stream(
            {"chat_history": chat_history, "user_question": query}
        )

    # conversation
    for message in st.session_state.chat_history:
        if isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.markdown(message.content)
        else:
            with st.chat_message("AI"):
                st.markdown(message.content)

    # Chat input box
    user_query = st.chat_input("This is a chat input")

    # Add user query to chat history (will be displayed above the input box)
    if user_query is not None:
        st.session_state.chat_history.append(HumanMessage(user_query))

        with st.chat_message("Human"):
            st.markdown(user_query)

        with st.chat_message("AI"):
            ai_response = st.write_stream(
                get_response(user_query, st.session_state.chat_history)
            )
        st.session_state.chat_history.append(AIMessage(ai_response))
