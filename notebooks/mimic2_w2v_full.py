import pymysql
import medspacy
from gensim import utils
import gensim.models
import sys

MIMICHOST = "35.233.174.193"

def get_mimic_connection():
    conn = pymysql.connect(
        host=MIMICHOST, port=3306, user=sys.argv[1], passwd=sys.argv[2], db="mimic2"
    )
    return conn
print("creating db connection")
conn = get_mimic_connection()
cursor = conn.cursor()

print("loading i2b2 language model")

nlp = medspacy.load("en_info_3700_i2b2_2012", disable=["tagger", "parser", "ner"])

cursor.execute("""SELECT text FROM noteevents LIMIT 100""")
r = [r[0] for r in cursor.fetchall()]
docs = nlp.pipe(r, n_process=16, batch_size=64)
print("processed tokenization")
sents = [[line.string for line in doc.sents] for _,doc in enumerate(docs)]
print(sents)
sys.exit(0)


print('training model')
model = gensim.models.Word2Vec(sentences=sents, min_count=20, size=1000, workers=32)
print('saving model')
model.save("mimic2wv_b.gz")

