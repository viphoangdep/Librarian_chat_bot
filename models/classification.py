from transformers import pipeline
import re

# Initialize zero-shot classification model from Hugging Face
nlp = pipeline('zero-shot-classification', model="facebook/bart-large-mnli")

def classify_question(question):
    candidate_labels = ['search title', 'search author', 'get book details', 'search by description']
    result = nlp(question, candidate_labels)
    return result['labels'][0]

# Extract title and author from the user's question
def extract_title_from_question(question, df_books):
    titles_in_db = df_books['title'].tolist()
    for title in titles_in_db:
        if re.search(r"\b" + re.escape(title) + r"\b", question, re.IGNORECASE):
            return title
    return None

def extract_author_from_question(question, df_books):
    authors_in_db = df_books['author'].tolist()
    for author in authors_in_db:
        if re.search(r"\b" + re.escape(author) + r"\b", question, re.IGNORECASE):
            return author
    return None

def search_books_by_description(description, df_books):
    results = []
    for index, row in df_books.iterrows():
        if re.search(re.escape(description), row['description'], re.IGNORECASE):
            results.append(row)
    return results

def query_book_by_title(title, df_books):
    book_row = df_books[df_books['title'].str.lower() == title.lower()]
    if not book_row.empty:
        return book_row.iloc[0]
    return None

def query_book_by_author(author, df_books):
    books_by_author = df_books[df_books['author'].str.lower() == author.lower()]
    if not books_by_author.empty:
        return books_by_author
    return None
