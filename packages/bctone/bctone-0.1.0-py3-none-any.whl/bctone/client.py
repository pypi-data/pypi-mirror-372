class RAGClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def query(self, text: str) -> str:
        # 실제로는 SaaS API 호출 로직이 들어감
        return f"[bctone] answer to: {text}"
