import chromadb
from datetime import datetime

class TestMemory:
    def __init__(self, path="./test_memory_db"):
        # Veritabanını başlatır
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection(name="test_history")

    def save_failure(self, test_id, error_msg, ai_analysis):
        """AI analizini ve hatayı hafızaya kaydeder."""
        timestamp = datetime.now().isoformat()
        
        # Gelecekte arama yapacağımız ana metin bloğu
        document_content = f"Test: {test_id} | Hata: {error_msg} | Analiz: {ai_analysis}"

        print(f"\n🧠 [MEMORY SAVED]: {test_id} hatası vektör veritabanına işlendi.")
        
        self.collection.add(
            documents=[document_content],
            metadatas=[{
                "test_id": test_id,
                "timestamp": timestamp,
                "type": "test_failure"
            }],
            ids=[f"{test_id}_{timestamp}"]
        )

    def get_similar_cases(self, current_error, n=2):
        """Mevcut hataya benzeyen geçmiş kayıtları getirir (RAG için)."""
        print(f"🔍 [MEMORY SEARCH]: Benzer geçmiş hatalar sorgulanıyor...")
        results = self.collection.query(
            query_texts=[current_error],
            n_results=n
        )
        return results['documents']