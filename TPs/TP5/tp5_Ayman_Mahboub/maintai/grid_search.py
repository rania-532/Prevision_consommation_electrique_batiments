"""Grid search : 5 valeurs de C x 5 seuils = 25 entraînements, chacun enregistré comme un run MLflow.

Usage : python -m maintai.grid_search
Les résultats se comparent ensuite dans mlflow ui (expérience maintai).
"""
import contextlib
import io
import itertools

import mlflow

from maintai.tracking import EXPERIMENT
from maintai.train import main as train

C_VALUES = [0.01, 0.1, 1.0, 10.0, 100.0]
THRESHOLDS = [0.1, 0.2, 0.3, 0.4, 0.5]


def run_grid() -> list[dict]:
    """Lance les 25 entraînements et renvoie leurs résultats (run, C, seuil, métriques)."""
    results = []
    for C, threshold in itertools.product(C_VALUES, THRESHOLDS):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            metrics = train(["--C", str(C), "--threshold", str(threshold)])
        run_id = mlflow.last_active_run().info.run_id
        results.append({"run_id": run_id, "C": C, "threshold": threshold, **metrics["model"]})
        print(f"C={C:<6} seuil={threshold}  recall={metrics['model']['recall']:.3f}  "
              f"precision={metrics['model']['precision']:.3f}  run={run_id}", flush=True)
    return results


def main() -> None:
    mlflow.set_experiment(EXPERIMENT)
    results = run_grid()
    best = max(results, key=lambda r: (r["recall"], r["precision"]))
    print("\n| C | seuil | recall | precision | accuracy | run |")
    print("|---:|---:|---:|---:|---:|---|")
    for r in results:
        print(f"| {r['C']} | {r['threshold']} | {r['recall']:.3f} | {r['precision']:.3f} "
              f"| {r['accuracy']:.3f} | `{r['run_id']}` |")
    print(f"\nMeilleur recall : C={best['C']}, seuil={best['threshold']}, run {best['run_id']}")


if __name__ == "__main__":
    main()
