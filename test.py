import streamlit as st
from openai import AzureOpenAI
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from the .env file

azure_endpoint = os.getenv("AZURE_ENDPOINT")
api_key = os.getenv("API_KEY")
api_version = os.getenv("API_VERSION")
model = os.getenv("MODEL")

client = AzureOpenAI(
    azure_endpoint=azure_endpoint,
    api_key=api_key,
    api_version=api_version,
)

st.title("Hyiuske")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Create a placeholder to update as tokens are streamed in
        assistant_response_placeholder = st.empty()

        stream = client.chat.completions.create(
            model=model,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        # Initialize a variable to collect the full response
        full_response = ""

        for chunk in stream:
            print("Chunk received:", chunk)  # To understand the structure of the chunk
            if chunk.choices and len(chunk.choices) > 0:
                delta_content = chunk.choices[0].delta.content
                print(
                    "Delta content:", delta_content
                )  # Check the content before concatenation
                if delta_content is not None:
                    full_response += delta_content
                    assistant_response_placeholder.markdown(full_response)

        # Append the final response to the session state
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )
