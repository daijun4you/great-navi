import chromadb
import utils


class RAG:
    def __init__(self):
        self.client = utils.get_openai_client()
        self.db = chromadb.PersistentClient(path="./data/db/").get_or_create_collection(
            name='knowledge_db'
        )
        self._init_db_if_need()

    def rag(self, userPrompt, history=None) -> str:
        return userPrompt

    def _init_db_if_need(self):
        # db中有数据则不需要初始化
        if len(self.db.get()["ids"]) != 0:
            return
