import chromadb
import os
import utils


def init_db_if_need():
    db = chromadb.PersistentClient(path="./data/db/").get_or_create_collection(
        name='knowledge_db'
    )
    if len(db.get()["ids"]) != 0:
        return

    id = 0
    for root, _, files in os.walk("./data/doc/"):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8') as file:
                data_ids = []
                data = []
                for line in file:
                    id += 1
                    data_ids.append(str(id))
                    data.append(line.strip())
                    if len(data) == 10:
                        db.upsert(
                            ids=data_ids,
                            embeddings=utils.get_embeddings(data),
                            documents=data,
                        )
                        data = []
                        data_ids = []

                if len(data) > 0:
                    db.upsert(
                        ids=data_ids,
                        embeddings=utils.get_embeddings(data),
                        documents=data,
                    )


init_db_if_need()
