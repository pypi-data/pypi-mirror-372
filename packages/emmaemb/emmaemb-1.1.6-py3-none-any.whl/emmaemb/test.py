import pandas as pd

from emmaemb.core import Emma
from emmaemb.vizualisation import plot_knn_alignment_scores_across_k_and_distance_metrics


fp_features = "/media/drive2/francesca/ema/examples/Pla2g2/Pla2g2_features.csv"
emb_dir = "/media/drive2/francesca/ema/examples/Pla2g2/embeddings/"
models = {
    "ESMC": emb_dir + "ESMC",
    "ProtT5": emb_dir + "ProtT5"
}

features = pd.read_csv(fp_features)
emma = Emma(features)

for model_name in models:
    emma.add_emb_space(
        embeddings_source=emb_dir + model_name,
        emb_space_name=model_name,
    )
    
num_samples = emma.metadata.shape[0]
for distance_metric in ['euclidean', 'cosine']:
    # check if already computed
    for model in emma.emb.keys():
        print(f"\nProcessing {model} with {distance_metric}...")

        emma.calculate_pairwise_distances(
                emb_space=model,
                metric=distance_metric,
            )

        pwd = emma.emb[model]["pairwise_distances"][distance_metric]
        ranks = emma.emb[model]["ranks"][distance_metric]

        # Validate shape before saving
        if pwd.shape != (num_samples, num_samples) or ranks.shape[0] != num_samples:
            raise ValueError(f"Calculated data has unexpected shape for {model} - {distance_metric}")
    
fig = plot_knn_alignment_scores_across_k_and_distance_metrics(
    emma=emma,
    feature="group",
    metrics= ["euclidean", "cosine"]
)

print(emma)