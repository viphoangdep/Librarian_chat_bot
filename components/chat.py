import streamlit as st

def display_chat(conversation):
    for chat in conversation:
        if chat["sender"] == "user":
            st.markdown(f'<div style="text-align: right;"><span style="background-color: #d1e7dd; padding: 10px; border-radius: 10px; display: inline-block;">{chat["message"]}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="text-align: left;"><span style="background-color: #f8d7da; padding: 10px; border-radius: 10px; display: inline-block;">{chat["message"]}</span></div>', unsafe_allow_html=True)

def handle_user_question(question, df_books):
    from models.classification import classify_question, extract_title_from_question, extract_author_from_question
    from data.dataframe import query_book_by_title, query_book_by_author, search_books_by_description
    from components.download import generate_json_download

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
