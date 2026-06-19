"""
Simple interactive command-line interface for the Document Q&A bot.

Run:
    python -m src.main
"""

import os
from . import config
from .query import query_rag_pipeline


def main():
    if not os.path.isdir(config.DB_DIR) or not os.listdir(config.DB_DIR):
        print("No index found. Run `python -m src.ingest` first to build the database.")
        return

    print("Document Q&A Bot — type your question, or 'exit' to quit.\n")

    while True:
        user_query = input("You: ").strip()
        if not user_query:
            continue
        if user_query.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        result = query_rag_pipeline(user_query)
        print(f"\nBot: {result['answer']}\n")
        if result["citations"]:
            print("Sources:")
            for c in result["citations"]:
                print(f"  - {c}")
        print()


if __name__ == "__main__":
    main()
