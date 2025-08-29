from emma.embedding.get_embeddings import get_embeddings
import numpy as np

get_embeddings(
    model="esm1b_t33_650M_UR50S",
    input="data/sequences.fasta",
    output_dir="data/embeddings",
    dev=True,
    no_gpu=True,
    max_seq_length=100,
    chunk_overlap=50,
)

print()

fp = "data/embeddings/esm1b_t33_650M_UR50S/layer_33/chopped_100_overlap_50/CATSPER3_0.npy"
embeddings = np.load(fp)
