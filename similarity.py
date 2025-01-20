from mysql.connector import connect, Error
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def text_similarity(text1, text2=""):
    vectors = TfidfVectorizer().fit_transform([text1, text2])
    similarity = cosine_similarity(vectors)

    return similarity[0,1]


def first_words(s):
    s = s.split(" ")[:20]
    return " ".join(s)


def similarity():

    conn = connect(host="localhost", user="root", password="", database="dbname")
    cursor = conn.cursor()
    cursor.execute("Select id, tokens from book")
    allbooks = cursor.fetchall()
    cursor.execute("Select id, tokens from book limit 40 offset 10")
    partial = cursor.fetchall()


    for item in partial:
        similarity = []
        current_id = item[0]
        current_text = first_words(item[1])
        print(current_text)

        cursor.execute("DELETE FROM similar_books WHERE book_id = " + str(current_id))

        for book in allbooks:
            if current_id == book[0]:
                continue
            sim = text_similarity(current_text, first_words(book[1]))
            similarity.append((current_id, book[0], sim))

        if similarity:
            similarity = sorted(similarity, key=lambda sim: sim[2], reverse=True)[:20]

            insert_query = """
            INSERT INTO similar_books (book_id, similar_id, similarity) VALUES (%s,%s,%s)
            """

            cursor.executemany(insert_query, similarity)
            conn.commit()

    print('done!')

if __name__ == '__main__':
    similarity()