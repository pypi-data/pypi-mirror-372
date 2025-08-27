import logging


def read_fasta(file_path: str) -> dict:
    with open(file_path, "r") as f:
        lines = f.readlines()
        sequences = {}
        header = None
        for line in lines:
            line = line.strip()
            if line.startswith(">"):
                header = line[1:]  # Remove '>'
                sequences[header] = ""
            else:
                if header is not None:
                    sequences[header] += line
    return sequences


def read_fasta_names(file_path: str) -> list:
    with open(file_path, "r") as f:
        lines = f.readlines()
        proteins = []
        for line in lines:
            line = line.strip()
            if line.startswith(">"):
                proteins.append(line[1:])
    return proteins


def write_fasta(file_path: str, sequences: dict):
    with open(file_path, "w") as fasta_file:
        for header, sequence in sequences.items():
            fasta_file.write(f">{header}\n")
            for i in range(0, len(sequence), 80):
                fasta_file.write(sequence[i : i + 80] + "\n")
    return None


def setup_logger(name: str, log_file: str) -> logging.Logger:
    """
    Sets up and returns a logger with a stream handler (console)
    and file handler.

    Args:
        name (str): Name of the logger.
        log_file (str): Path to the log file.

    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger(name)

    # Avoid adding handlers multiple times in a Jupyter environment
    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)

        # Console handler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )

        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )

        # Add both handlers to the logger
        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)

    return logger
