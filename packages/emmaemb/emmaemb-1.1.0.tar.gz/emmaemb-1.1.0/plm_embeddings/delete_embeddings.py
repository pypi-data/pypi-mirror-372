import os
import argparse


def find_and_delete_files(
    output_dir: str, protein_file_path: str, extension: str
):
    # Read protein names from the provided file
    with open(protein_file_path, "r") as f:
        protein_names = [line.strip() for line in f.readlines()]

    # Initialise storage for found files
    files_to_delete = {}

    # Traverse the output directory and its subdirectories
    for root, _, files in os.walk(output_dir):
        for file in files:
            for protein_name in protein_names:
                if file == f"{protein_name}.{extension}":
                    if root not in files_to_delete:
                        files_to_delete[root] = []
                    files_to_delete[root].append(file)

    # Display the results and ask for confirmation
    total_files = sum(len(files) for files in files_to_delete.values())
    if total_files == 0:
        print("No files found for deletion.")
        return

    print(f"Found {total_files} matching files in the following directories:")
    for directory, files in files_to_delete.items():
        print(f"- {directory}: ({len(files)} files)")

    # Ask the user for confirmation
    user_response = (
        input("Do you want to delete these files? (Y/N): ").strip().upper()
    )
    if user_response == "Y":
        for directory, files in files_to_delete.items():
            for file in files:
                os.remove(os.path.join(directory, file))
        print("Files deleted successfully.")
    elif user_response == "N":
        print("Files not deleted.")
    else:
        print("Invalid response. Exiting without making changes.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find and optionally delete files matching protein names \
            and extension."
    )
    parser.add_argument(
        "output_directory", help="Path to the output directory to search."
    )
    parser.add_argument(
        "protein_list_path",
        help="Path to the file containing the list of protein names.",
    )
    parser.add_argument(
        "file_extension", help="File extension to search for (e.g., .npy)."
    )

    args = parser.parse_args()

    find_and_delete_files(
        args.output_directory, args.protein_list_path, args.file_extension
    )
