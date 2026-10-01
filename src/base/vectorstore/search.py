from llm_rag.src.base.vectorstore.store import(
    create_client,
    get_collection,
)

if __name__ == "__main__":
    client = create_client()
    collection = get_collection(client)

    question = "K9 spell card"

    results = collection.query(
        query_texts=[question],
        n_results=1,
    )

    print("=== DOCUMENTOS ===")

    for document in results["documents"][0]:
        print(document)

    print("\n=== METADADOS ===")

    for metadata in results["metadatas"][0]:
        print(metadata)

    print("\n=== DISTÂNCIAS ===")

    for distance in results["distances"][0]:
        print(distance)


