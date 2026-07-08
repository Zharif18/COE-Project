import streamlit as st
import pandas as pd
from utils.helpers import render_page_header
from ai.gemini import get_ai_response, has_api_key

def render_ai_assistant(
    inventory: pd.DataFrame,
    suppliers: pd.DataFrame,
    orders: pd.DataFrame,
    shipments: pd.DataFrame
) -> None:
    """
    Renders the interactive AI Assistant conversational agent page,
    supporting chat history and state management.
    """
    render_page_header("🤖 AI Supply Chain Assistant", "Consult the Gemini-powered agent on supply optimization.")

    # 1. API Key Config Section inside the assistant page
    if not has_api_key():
        with st.expander("🔑 Configure Gemini API Key", expanded=True):
            st.info(
                "Gemini API key not found in system environment or secrets. "
                "You can paste your API key below to enable full conversational AI. "
                "Otherwise, the assistant will run in local offline heuristic mode."
            )
            key_input = st.text_input("Enter Gemini API Key", type="password", key="gemini_api_key_input")
            if key_input and st.session_state.get("gemini_api_key") != key_input:
                st.session_state["gemini_api_key"] = key_input
                st.success("API key registered for this session!")
                st.rerun()

    # 2. Initialize chat messages session state
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {
                "role": "assistant",
                "content": (
                    "👋 Hello! I am your **SupplySense AI Assistant**.\n\n"
                    "I have parsed your live inventory, supplier rankings, orders ledger, and shipments list. "
                    "Ask me questions like:\n"
                    "- *'Which products have critical stock levels and need immediate reordering?'*\n"
                    "- *'Which supplier has the highest defect rate?'*\n"
                    "- *'Summarize our logistics delays by region.'*\n"
                    "- *'How can we optimize our safety stock?'*"
                )
            }
        ]

    # 3. Sidebar status
    st.sidebar.subheader("🤖 AI Assistant Status")
    if has_api_key():
        st.sidebar.success("Gemini API Connected ✅")
    else:
        st.sidebar.warning("Offline Heuristics Active ⚠️")
        
    if st.sidebar.button("Clear Chat History"):
        del st.session_state["messages"]
        st.rerun()

    # 4. Render Conversation History
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 5. Handle User Input
    user_prompt = st.chat_input("Ask a question about your Supply Chain...")
    
    if user_prompt:
        # Append and display user message
        st.session_state["messages"].append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Generate agent response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing datasets..."):
                response = get_ai_response(
                    prompt=user_prompt,
                    inventory=inventory,
                    suppliers=suppliers,
                    orders=orders,
                    shipments=shipments
                )
                st.markdown(response)
                
        # Append response to history
        st.session_state["messages"].append({"role": "assistant", "content": response})
