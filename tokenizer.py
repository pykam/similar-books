from mysql.connector import connect, Error
import nltk, re
from nltk.corpus import stopwords
from pymorphy2 import MorphAnalyzer

#nltk.download('stopwords')

def tokenizer():
    patterns = "[0-9!#$%&'()*+,./:;<=>?@[\]^_`{|}~—\"\-–«»©…]+"
    stopwords_ru = stopwords.words("russian")
    stopwords_en = stopwords.words("english")

    conn = connect(host="localhost", user="root", password="", database="dbname")
    cursor = conn.cursor()
    cursor.execute("Select id, name, description from book")
    book = cursor.fetchall()

    morph = MorphAnalyzer()

    cleaned_books = []

    for item in book:
        cleaned = re.sub(patterns, ' ', item[1] + ' ' + item[2])
        cleaned_books.append((item[0], item[1], item[2], cleaned))

    token_books = []

    for item in cleaned_books:
        tokens = []
        for token in item[3].split():
            if (token and token not in stopwords_ru) or (token and token not in stopwords_en):
                token = token.strip()
                token = morph.normal_forms(token)[0]
                tokens.append(token)
        token_books.append((item[0], item[1], item[2], item[3], tokens))
        print(item[0])
    token_books_cleaned = []

    for item in token_books:
        cleaned = []
        for pat in item[4]:
            res = re.sub(patterns, '', pat)
            if len(res) > 1:
                cleaned.append(res)
        token_books_cleaned.append((item[0], item[1], item[2], item[3], item[4], cleaned))

    update_query = """
    UPDATE book SET tokens=%s
    WHERE id=%s
    """

    records = []

    for item in token_books_cleaned:
        records.append((" ".join(item[5]), item[0]))

    cursor.executemany(update_query, records)

    conn.commit()

    # Press the green button in the gutter to run the script.
if __name__ == '__main__':
    tokenizer()
