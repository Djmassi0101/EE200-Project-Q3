import os

from matcher import SongMatcher


# ==========================================================
# Main Recognition Function
# ==========================================================

def main():

    DATABASE_PATH = "data/fingerprints.pkl"

    matcher = SongMatcher()

    print("\nLoading fingerprint database...")

    matcher.load_database(DATABASE_PATH)

    print("Database loaded successfully.\n")

    while True:

        query_file = input(
            "Enter the path to the query MP3 file\n"
            "(or type 'exit' to quit): "
        ).strip()

        if query_file.lower() == "exit":

            print("\nGoodbye!")

            break

        if not os.path.exists(query_file):

            print("\nFile not found.\n")

            continue

        print("\nRecognizing song...\n")

        result = matcher.identify(
            query_path=query_file
        )

        matcher.print_results(result)

        if result["song"] is not None:

            show = input(
                "\nDisplay offset histogram? (y/n): "
            ).strip().lower()

            if show == "y":

                matcher.plot_histogram(
                    result["histogram"]
                )

        print("\n-----------------------------------\n")


# ==========================================================
# Entry Point
# ==========================================================

if __name__ == "__main__":

    main()
