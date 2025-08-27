# Trainer Module

The `Trainer` module simplifies and automates the process of feature reduction, model training, and evaluation for various machine learning tasks, ensuring flexibility and efficiency.

## Key Features

1. Feature Reduction:
    - Supports methods such as `mrmr`, `variance_threshold`, `corr`, and `chi2` to identify and retain relevant features.

2. Automated Model Training:
    - Integrates with AutoGluon for model training, selection, and optimization.
    - Handles tasks such as binary classification, multiclass classification, regression, and survival.

## Example Usage

```python
from jarvais.trainer import TrainerSupervised

trainer = TrainerSupervised(
    output_dir="./outputs/trainer", 
    target_variable="death", 
    task="binary",
    k_folds=2
)

trainer.run(data)
```

## Example Output

```bash
12:50:37 [info     ] Training fold 1/2...           [jarvais] call=autogluon_trainer._train_autogluon_with_cv:192
12:51:06 [info     ] Fold 1/2 score: 0.7761862315751399 (roc_auc) [jarvais] call=autogluon_trainer._train_autogluon_with_cv:209
         [info     ] Training fold 2/2...           [jarvais] call=autogluon_trainer._train_autogluon_with_cv:192
12:51:31 [info     ] Fold 2/2 score: 0.750053611337183 (roc_auc) [jarvais] call=autogluon_trainer._train_autogluon_with_cv:209
...
```

### Model Leaderboard
Displays values in `mean [min, max]` format across training folds.

| **Model**               | **Score Test**               | **Score Val**                | **Score Train**              |
|-------------------------|------------------------------|------------------------------|------------------------------|
| **WeightedEnsemble_L2** | AUROC: 0.82 [0.82, 0.83]     | AUROC: 0.85 [0.85, 0.85]     | AUROC: 1.0 [1.0, 1.0]        |
|                         | F1: 0.13 [0.11, 0.14]        | F1: 0.09 [0.07, 0.12]        | F1: 0.95 [0.9, 1.0]          |
|                         | AUPRC: 0.48 [0.45, 0.52]     | AUPRC: 0.47 [0.44, 0.49]     | AUPRC: 0.96 [0.91, 1.0]      |
| **ExtraTreesGini**      | AUROC: 0.82 [0.82, 0.82]     | AUROC: 0.84 [0.84, 0.84]     | AUROC: 1.0 [1.0, 1.0]        |
|                         | F1: 0.21 [0.19, 0.22]        | F1: 0.16 [0.14, 0.18]        | F1: 1.0 [1.0, 1.0]           |
|                         | AUPRC: 0.45 [0.45, 0.45]     | AUPRC: 0.43 [0.41, 0.45]     | AUPRC: 1.0 [1.0, 1.0]        |
|...

## Output Files
**Binary/Regression/Multiclass**:

```bash
├── autogluon_models
│   ├── autogluon_models_best_fold
│   │   ├── learner.pkl
│   │   ├── models
│   │   ├── ...
│   ├── autogluon_models_fold_1
│   │   ├── learner.pkl
│   │   ├── models
│   │   ├── ...
│   ├── autogluon_models_fold_2
│   │   ├── learner.pkl
│   │   ├── models
│   │   ├── ...
│   ├── autogluon_models_fold_3
│   │   ├── learner.pkl
│   │   ├── models
│   │   ├── ...
│   ├── autogluon_models_fold_4
│   │   ├── learner.pkl
│   │   ├── models
│   │   ├── ...
│   └── autogluon_models_fold_5
│   │   ├── learner.pkl
│   │   ├── models
│   │   ├── ...
```

**Survival**:

```bash
└── survival_models
    ├── CoxPH.pkl
    ├── GradientBoosting.pkl
    ├── RandomForest.pkl
    └── SVM.pkl
    ├── lightning_logs
    │   ├── version_0
    │   ├── ...
    ├── DeepSurv.ckpt
    ├── MTLR.ckpt
```