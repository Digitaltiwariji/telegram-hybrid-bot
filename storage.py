class MemoryStore:
    def __init__(self):
        self.last_results = {}

    def set(self, user_id: int, results: list):
        self.last_results[user_id] = results

    def get(self, user_id: int):
        return self.last_results.get(user_id, [])