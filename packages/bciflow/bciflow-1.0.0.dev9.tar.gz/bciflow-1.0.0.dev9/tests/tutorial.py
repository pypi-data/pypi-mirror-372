from bciflow.datasets.cbcic import cbcic
from bciflow.modules.core.kfold import kfold
from bciflow.modules.tf.filterbank import filterbank
from bciflow.modules.sf.csp import csp
from bciflow.modules.fe.logpower import logpower
from bciflow.modules.fs.mibif import MIBIF
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as lda
import pandas as pd
from bciflow.modules.analysis.metric_functions import accuracy, kappa, logloss, rmse

dataset = cbcic(subject = 1)

pre_folding = {'tf': (filterbank, {'kind_bp':'chebyshevII'}),}

pos_folding = {'fe': (logpower, {'flating': True}),
               'clf': (lda(), {})}

sf = csp()
fe = logpower
fs = MIBIF(8, clf=lda())
clf = lda()

pos_folding = {'sf': (sf, {}),
               'fe': (fe, {}),
               'fs': (fs, {}),
               'clf': (clf, {})}
results = kfold(target=dataset, 
                start_window=dataset['events']['cue'][0]+0.5, 
                pre_folding=pre_folding, 
                pos_folding=pos_folding)

print(results)

df = pd.DataFrame(results)
# Calculate metrics
acc = accuracy(df)

# Display results
print(f"Accuracy: {acc:.4f}")
