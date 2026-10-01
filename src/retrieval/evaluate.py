from retrieval.retriever import YugiohRetriever

QUERIES = [
    "cartas que podem ser invocadas especialmente do cemitério",
    "monstros que destroem cartas do oponente",
    "cartas que compram outras cartas",
    "monsters k9",
    "monstros de atributo DARK com alto ATK",
    "cartas que negam efeitos de monstros",
]

def main() -> None:
    retriever = YugiohRetriever()

    for query in QUERIES:
        print("\n" + "=" * 70)
        print(f"CONSULTA: {query}")
        print("=" * 70)

        results = retriever.search(
            query,
            top_k=5,
        )

        for index, result in enumerate(
            results,
            start=1,
        ): 
            metadata = result["metadata"]

            print(
                f"{index}. "
                f"{metadata['name']} "
                f"| distância: "
                f"{result['distance']:.4f}"
            )

if __name__=="__main__":
    main()