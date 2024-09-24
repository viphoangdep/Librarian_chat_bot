import streamlit as st
import psycopg2
import pandas as pd
import re
import json
import base64
from transformers import pipeline

# Initialize zero-shot classification model from Hugging Face
nlp = pipeline('zero-shot-classification', model="facebook/bart-large-mnli")

# Connect to PostgreSQL database
def get_connection():
    return psycopg2.connect(
        dbname="library_management",
        user="postgres",
        password="1234",
        host="localhost",
        port="5432"
    )

# Query data from the database and return it as a DataFrame
@st.cache_data
def fetch_books_to_dataframe():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = "SELECT * FROM books;"
        cursor.execute(query)
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(results, columns=column_names)
    finally:
        cursor.close()
        conn.close()
    
    return df

# Get data from DataFrame
df_books = fetch_books_to_dataframe()
df_books = df_books[['title', 'author', 'description']]

# Classify the user's question using the Hugging Face model
def classify_question(question):
    candidate_labels = ['search title', 'search author', 'get book details', 'search by description']
    result = nlp(question, candidate_labels)
    return result['labels'][0]

# Function to extract the title from the user's question
def extract_title_from_question(question):
    titles_in_db = df_books['title'].tolist()
    for title in titles_in_db:
        if re.search(r"\b" + re.escape(title) + r"\b", question, re.IGNORECASE):
            return title
    return None

# Function to extract the author's name from the user's question
def extract_author_from_question(question):
    authors_in_db = df_books['author'].tolist()
    for author in authors_in_db:
        if re.search(r"\b" + re.escape(author) + r"\b", question, re.IGNORECASE):
            return author
    return None

# Search for books by description
def search_books_by_description(description):
    results = []
    for index, row in df_books.iterrows():
        if re.search(re.escape(description), row['description'], re.IGNORECASE):
            results.append(row)
    return results

# Query a book by title from the DataFrame
def query_book_by_title(title):
    book_row = df_books[df_books['title'].str.lower() == title.lower()]
    if not book_row.empty:
        return book_row.iloc[0]
    return None

# Query books by author
def query_book_by_author(author):
    books_by_author = df_books[df_books['author'].str.lower() == author.lower()]
    if not books_by_author.empty:
        return books_by_author
    return None

# Function to generate downloadable JSON
def generate_json_download(book):
    json_data = json.dumps({
        "title": book['title'],
        "author": book['author'],
        "description": book['description']
    }, indent=4)

    # Convert JSON data to base64 for download
    b64 = base64.b64encode(json_data.encode()).decode()
    href = f'<a href="data:application/json;base64,{b64}" download="{book["title"]}.json">Download JSON</a>'
    return href

# Handle the user's question
def handle_user_question(question):
    classification = classify_question(question)

    if classification == 'search author':
        title = extract_title_from_question(question)
        if title:
            book = query_book_by_title(title)
            if book is not None:
                download_link = generate_json_download(book)
                return f'Title: {book["title"]}, Author: {book["author"]}, Description: {book["description"]}. {download_link}'
            else:
                return f"Could not find a book with the title '{title}'."
        else:
            return "Sorry, I couldn't find any book title in your question."

    if classification == 'search title':
        author_name = extract_author_from_question(question)
        if author_name:
            books_by_author = query_book_by_author(author_name)
            if not books_by_author.empty:
                return "\n".join(books_by_author['title'].tolist())
            else:
                return f"Could not find books by the author '{author_name}'."
        else:
            return "Sorry, I couldn't find any author in your question."

    if classification == 'search by description':
        description = question  # Assuming the whole question is the description
        books_found = search_books_by_description(description)
        if books_found:
            response = "Books matching your description:\n"
            for book in books_found:
                response += f"Title: {book['title']}, Author: {book['author']}, Description: {book['description']}\n"
            return response
        else:
            return "No books matching the description found."

    return "Sorry, I didn't understand your question."

# Streamlit UI with chat bubbles
def main():
    st.title("Librarian Assistant Chatbot")

    # Initialize session state to store the conversation
    if "conversation" not in st.session_state:
        st.session_state["conversation"] = []

    # User input field
    with st.form(key="chat_form"):
        user_input = st.text_input("Ask about books:", "")
        submit_button = st.form_submit_button("Send")

    # Process user input and response
    if submit_button and user_input:
        # Store user input in conversation history
        st.session_state["conversation"].append({"sender": "user", "message": user_input})
        
        # Get bot response
        with st.spinner("Bot is thinking..."):
            bot_response = handle_user_question(user_input)
        
        # Store bot response in conversation history
        st.session_state["conversation"].append({"sender": "bot", "message": bot_response})
    
    # Display chat history with bubbles
    for chat in st.session_state["conversation"]:
        if chat["sender"] == "user":
            st.markdown(f'<div style="text-align: right;"><span style="background-color: #d1e7dd; padding: 10px; border-radius: 10px; display: inline-block;">{chat["message"]}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="text-align: left;"><span style="background-color: #f8d7da; padding: 10px; border-radius: 10px; display: inline-block;">{chat["message"]}</span></div>', unsafe_allow_html=True)

    # Display data in sidebar
    with st.sidebar:
        st.header("Books Data")
        st.write(df_books)

if __name__ == "__main__":
    main()
