from base.vectorstore.store import (
    create_client,
    get_collection,
)

class YugiohRetriever:
    def __init__(self):
        self.client = create_client()
        self.collection = get_collection(self.client)

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:
        results = self.collection.query(
            query_texts=[query], 
            n_results=top_k,
        )

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        retrieved_cards = []

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):
            retrieved_cards.append(
                {
                    "document": document,
                    "metadata": metadata,
                    "distance": distance,
                }
            )

        return retrieved_cards

if __name__=="__main__":
    retriever = YugiohRetriever()

    query = (
        "Quais cartas podem ser"
        "invocadas especialmente do cemitério?"
    )

    results = retriever.search(
        query,
        top_k=5,
    )

    print("=== RESULTADOS ===")

    for index, result in enumerate(results, start=1):
        print()
        print(f"--- Resultado {index} ---")
        print(
            f"Nome: "
            f"{result['metadata']['name']}"
        )
        print(
            f"Distância: "
            f"{result['distance']:.4f}"
        )
        print(
            f"Documento:\n"
            f"{result['document']}"
        )