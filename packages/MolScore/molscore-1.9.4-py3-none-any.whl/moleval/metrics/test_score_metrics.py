import pandas as pd
import json
from moleval.metrics.score_metrics import ScoreMetrics
from molscore import MockGenerator
mg = MockGenerator()

scores = pd.read_csv('/shared/morgan/SMILES-RNN/prompt/denovo/2023_11_20_SMILES-RNN_Aripiprazole_similarity/scores.csv', index_col=0)
print('Without budget')
metrics = ScoreMetrics(scores=scores, budget=None, n_jobs=4, reference_smiles=mg.sample(10))
results = metrics.get_metrics(endpoints=['single'], thresholds=[0.8], chemistry_filter_basic=True, extrapolate=True)
print(json.dumps(results, indent=2))

print('With budget of 1000 and no thresholds')
metrics = ScoreMetrics(scores=scores, budget=1000, n_jobs=4, reference_smiles=mg.sample(1000))
results = metrics.get_metrics(endpoints=['single'], thresholds=[], target_smiles=mg.sample(10), chemistry_filter_basic=True, chemistry_filter_target=True, extrapolate=True)
print(json.dumps(results, indent=2))