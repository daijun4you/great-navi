import chromadb
import utils
import json


class RAG:
    def __init__(self):
        self.client = utils.get_openai_client()
        self.db = chromadb.PersistentClient(path="./data/db/").get_or_create_collection(
            name='knowledge_db'
        )

    def rag(self, userPrompt, history=None) -> str:
        rs = self.db.query(
            query_embeddings=utils.get_embeddings([userPrompt]),
            n_results=10,
            include=['distances', 'documents'],
        )

        needDocsIndex = []
        for i, one in enumerate(rs['distances'][0]):
            if one < 0.3:
                needDocsIndex.append(i)

        docs = []
        for i in needDocsIndex:
            docs.append(rs['documents'][0][i])

        docs_str = str(docs)
        if len(docs) > 0:
            return f"请参考：'''{docs_str}'''，回答用户问题：'''{userPrompt}'''"

        return userPrompt
