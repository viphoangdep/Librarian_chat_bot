import streamlit as st
from components.chat import display_chat, handle_user_question
from data.database import fetch_books_to_dataframe

def main():
    st.title("Librarian Assistant Chatbot")
    
    # Fetch the books DataFrame
    df_books = fetch_books_to_dataframe()

    # Initialize session state to store the conversation
    if "conversation" not in st.session_state:
        st.session_state["conversation"] = []

    # User input field
    user_input = st.text_input("Ask about books:")
    if user_input:
        # Store user input in conversation history
        st.session_state["conversation"].append({"sender": "user", "message": user_input})
        
        # Get bot response
        bot_response = handle_user_question(user_input, df_books)
        
        # Store bot response in conversation history
        st.session_state["conversation"].append({"sender": "bot", "message": bot_response})

    # Display chat history with bubbles
    display_chat(st.session_state["conversation"])

if __name__ == "__main__":
    main()
