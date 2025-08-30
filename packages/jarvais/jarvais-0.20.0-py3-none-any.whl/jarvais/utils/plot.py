from itertools import combinations
import json
from pathlib import Path
import math
from typing import Any

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

import shap
from autogluon.tabular import TabularPredictor
from scipy.stats import f_oneway, ttest_ind
from sklearn.metrics import (
    confusion_matrix,
    r2_score,
    roc_auc_score,
    root_mean_squared_error,
)
from umap import UMAP
from statsmodels.stats.multicomp import pairwise_tukeyhsd

from lifelines.statistics import multivariate_logrank_test
from sksurv.nonparametric import kaplan_meier_estimator

from jarvais.loggers import logger
from .functional import auprc, ci_wrapper, bootstrap_metric
from ._plot_epic import plot_epic_copy
from ._design import config_plot

# ANALYZER
@config_plot(plot_type='multi')
def plot_one_multiplot(
        data: pd.DataFrame,
        umap_data: pd.DataFrame,
        var: str,
        continuous_columns: list,
        output_dir: Path,
        save_to_json: bool = False
    ) -> Path:

    def prep_for_pie(df, label):
        # Prepares data for pie plotting by grouping and sorting values.
        data = df.groupby(label, observed=False).size().sort_values(ascending=False)

        labels = data.index.tolist()
        values = data.values.tolist()

        return labels, values

    # only write % if big enough
    def autopct(pct):
        return ('%1.1f%%' % pct) if pct > 3.5 else ''

    def calculate_fontsize(num_categories):
        base_fontsize = 16
        min_fontsize = 8
        return max(base_fontsize - num_categories * 1.5, min_fontsize)

    num_categories = len(data[var].unique())

    labels, values = prep_for_pie(data, var)

    fontsize = calculate_fontsize(num_categories)

    # setting number of rows/columns for subplots
    n = len(continuous_columns) + 2
    if n < 21:
        cols = 4
    elif n < 36:
        cols = 5
    elif n < 49:
        cols = 6
    elif n < 71:
        cols = 7
    elif n < 89: 
        cols = 8
    else: # i hope it never gets to this
        cols = 9

    rows = int(np.ceil(n / cols))  # int(np.ceil(np.sqrt(n)))
    scaler = 6

    # create subplot grid
    fig, ax = plt.subplots(rows, cols, figsize=((cols-0.5)*scaler, rows*scaler), dpi=300)
    ax = ax.flatten()

    # Pie plot of categorical variable
    ax[0].pie(values,
              labels=labels,
              autopct=autopct,
              startangle=90,   # 90 = 12 o'clock, 0 = 3 o'clock, 180 = 9 o'clock
              counterclock=False,
              textprops={'fontsize': fontsize},
              colors=plt.cm.Set2.colors)
    ax[0].set_title(f"{var} Distribution. N: {data[var].count()}")

    if save_to_json:
        json_data = [{"name": l, "y": v} for l, v in zip(labels, values)]
        with open(output_dir / 'multiplots' / f"{var}_pie.json", "w") as f:
            json.dump(json_data, f)

        for col in continuous_columns:
            with (output_dir / 'multiplots' / f"{var}_{col}.json").open("w") as f:
                json.dump(data[[var, col]].to_dict(orient="records"), f, indent=2)

    # UMAP colored by variable
    sns.scatterplot(x=umap_data[:,0], y=umap_data[:,1], hue=data[var], alpha=.7, ax=ax[1])
    ax[1].set_title(f'UMAP of Continuous Variables with {var}')
    if data[var].nunique() > 5: # Puts legend under plot if there are too many categories
        ax[1].legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)

    # Calculate p-values
    p_values = {}
    for col in continuous_columns:
        unique_values = data[var].unique()
        if len(unique_values) > 1:
            if len(unique_values) == 2:
                group1 = data[data[var] == unique_values[0]][col]
                group2 = data[data[var] == unique_values[1]][col]
                _, p_value = ttest_ind(group1, group2, equal_var=False)
            else:
                groups = [data[data[var] == value][col] for value in unique_values]
                _, p_value = f_oneway(*groups)
            p_values[col] = p_value

    # Violin plots
    sorted_columns = sorted(p_values, key=p_values.get)
    for i, col in enumerate(sorted_columns):
        sns.violinplot(x=var, y=col, data=data, ax=ax[i+2], inner="point")
        
        # Add statistical annotations
        n_categories = len(unique_values)
        # Use bonferroni correction for multiple comparisons if >2 groups
        correction = 'bonferroni' if n_categories > 2 else None
        add_stat_annotation(ax[i+2], data, var, col, 
                          test='auto', 
                          comparisons_correction=correction,
                          text_format='star', 
                          loc='inside')
        
        ax[i+2].tick_params(axis='x', labelrotation=67.5)
        ax[i+2].set_title(f"{var} vs {col} (overall p={p_values[col]:.4f})")

    # Turn off unused axes
    for j in range(n, len(ax)):
        fig.delaxes(ax[j])

    multiplot_path = output_dir / 'multiplots' / f'{var}_multiplots.png'
    plt.savefig(multiplot_path)
    plt.close()

    return multiplot_path

@config_plot()
def plot_corr(
        corr: pd.DataFrame,
        size: float,
        output_dir: Path,
        file_name: str = 'correlation_matrix.png',
        title: str = "Correlation Matrix"
    ) -> None:
    """
    Plots a lower-triangle heatmap of the correlation matrix and saves it as an image file.

    Args:
        corr (pd.DataFrame): Correlation matrix to visualize.
        size (float): Size of the heatmap figure.
        output_dir (Path): Directory to save the output image.
        file_name (str): Name of the saved image file. Defaults to 'correlation_matrix.png'.

    Example:
        ```python
        import pandas as pd
        from pathlib import Path

        # Sample data
        df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': [5, 4, 3, 2, 1],
            'C': [2, 3, 4, 5, 6]
        })

        # Compute Spearman correlation
        corr_matrix = df.corr(method='spearman')

        # Plot and save the heatmap
        plot_corr(corr=corr_matrix, size=6, output_dir=Path('./output'))
        ```
    """
    fig, ax = plt.subplots(1, 1, figsize=(size*1.2, size))
    mask = np.triu(np.ones_like(corr, dtype=bool)) # Keep only lower triangle
    np.fill_diagonal(mask, False)
    sns.heatmap(corr, mask=mask, annot=True, cmap='coolwarm', vmin=-1, vmax=1, linewidth=.5, fmt="1.2f", ax=ax)
    plt.title(title)
    plt.tight_layout()

    figure_path = output_dir / file_name
    fig.savefig(figure_path)
    plt.close()

@config_plot(plot_type='ft')
def plot_frequency_table(
        data: pd.DataFrame,
        columns: list,
        output_dir: Path,
        save_to_json: bool = False
    ) -> None:
    """
    Generates and saves heatmap visualizations for frequency tables of all column pair combinations.

    Args:
        data (pd.DataFrame): Input dataset containing the columns to analyze.
        columns (list): List of column names to create frequency tables for.
        output_dir (Path): Directory to save the generated heatmaps.
        save_to_json (bool): Flag to indicate whether to save frequency table data as JSON files.
    """
    frequency_dir = Path(output_dir) / 'frequency_tables'
    frequency_dir.mkdir(parents=True, exist_ok=True)

    for column_1, column_2 in combinations(columns, 2):
        heatmap_data = pd.crosstab(data[column_1], data[column_2])
        plt.figure(figsize=(8, 6))
        sns.heatmap(heatmap_data, annot=True, cmap='coolwarm', fmt='d', linewidth=.5)
        plt.title(f'Frequency Table for {column_1} and {column_2}')
        plt.xlabel(column_2)
        plt.ylabel(column_1)
        plt.savefig(frequency_dir / f'{column_1}_vs_{column_2}.png')
        plt.close()

        if save_to_json:
            heatmap_data.to_json(frequency_dir / f'{column_1}_vs_{column_2}.json')

@config_plot()
def plot_pairplot(
        data: pd.DataFrame,
        continuous_columns: list,
        output_dir: Path,
        target_variable: str = None,
        n_keep: int = 10
    ) -> None:
    """
    Generates a pair plot of the specified continuous columns in the dataset.

    Args:
        data (pd.DataFrame): The input DataFrame containing the data to be visualized.
        continuous_columns (list): A list of column names corresponding to continuous variables.
        output_dir (Path): Directory where the resulting plot will be saved.
        target_variable (str, optional): The target variable to use as a hue for coloring the pair plot. Defaults to None.
        n_keep (int, optional): The maximum number of continuous columns to include in the plot. 
            If exceeded, the most correlated columns are selected. Defaults to 10.
    """
    if len(continuous_columns) > n_keep:
        spearman_corr = data[continuous_columns].corr(method="spearman") 
        corr_pairs = spearman_corr.abs().unstack().sort_values(
            kind="quicksort",
            ascending=False
        ).drop_duplicates()
        top_10_pairs = corr_pairs[corr_pairs < 1].nlargest(5)
        columns_to_plot = list({index for pair in top_10_pairs.index for index in pair})
    else:
        columns_to_plot = continuous_columns.copy()

    hue = target_variable
    if target_variable is not None:
        columns_to_plot += [target_variable]

    sns.set_theme(style="darkgrid")
    g = sns.pairplot(data[columns_to_plot], hue=hue)
    g.figure.suptitle("Pair Plot", y=1.08)

    figure_path = output_dir / 'pairplot.png'
    plt.savefig(figure_path)
    plt.close()

@config_plot()
def plot_umap(
        data: pd.DataFrame,
        continuous_columns: list,
        output_dir: Path,
    ) -> np.ndarray:
    """
    Generates a 2D UMAP projection of the specified continuous columns and saves the resulting scatter plot.

    Args:
        data (pd.DataFrame): The input DataFrame containing the data to be visualized.
        continuous_columns (list): A list of column names corresponding to continuous variables 
            to be included in the UMAP projection.
        output_dir (Path): Directory where the resulting plot will be saved.

    Returns:
        np.ndarray: A 2D NumPy array of the UMAP-transformed data.
    """
    umap_data = UMAP(n_components=2).fit_transform(data[continuous_columns])

    plt.figure(figsize=(8, 8))
    sns.scatterplot(x=umap_data[:,0], y=umap_data[:,1], alpha=.7)
    plt.title('UMAP of Continuous Variables')
    plt.savefig(output_dir / 'umap_continuous_data.png')
    plt.close()

    return umap_data

@config_plot()
def plot_kaplan_meier_by_category(
        data_x: pd.DataFrame,
        data_y: pd.DataFrame,
        categorical_columns: list,
        output_dir: Path
    ) -> None:
    """
    Plots Kaplan-Meier survival curves for each category in the specified categorical columns.

    Args:
        data_x (pd.DataFrame): Dataset containing the categorical columns to group by.
        data_y (pd.DataFrame): Dataset containing 'time' and 'event' columns for survival analysis.
        categorical_columns (list): List of categorical column names to generate survival curves for.
        output_dir (Path): Directory to save the Kaplan-Meier survival curve plots.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    for cat_col in categorical_columns:
        plt.figure(figsize=(10, 6))
        plt.title(f"Kaplan-Meier Survival Curve by {cat_col}")

        unique_categories = data_x[cat_col].unique()

        # Plot survival curves for each category
        for category in unique_categories:
            mask_category = data_x[cat_col] == category
            try: # To catch when there are not enough samples for category
                time_category, survival_prob_category, conf_int = kaplan_meier_estimator(
                    data_y["event"][mask_category].astype(bool),
                    data_y["time"][mask_category],
                    conf_type="log-log",
                )

                plt.step(
                    time_category,
                    survival_prob_category,
                    where="post",
                    label=f"{cat_col} = {category}"
                )
                plt.fill_between(
                    time_category,
                    conf_int[0],
                    conf_int[1],
                    alpha=0.25,
                    step="post"
                )
            except Exception as _:
                pass
        
        results_multivariate = multivariate_logrank_test(
            data_y['time'], 
            data_x[cat_col], 
            data_y['event']
        )
        multivariate_p_value = results_multivariate.p_value

        plt.text(0.6, 0.1, f"Multivariate log-rank p-value: {multivariate_p_value:.4e}",
                 fontsize=10, transform=plt.gca().transAxes, bbox=dict(facecolor='white', alpha=0.8))
        plt.ylim(0, 1)
        plt.ylabel(r"Estimated Probability of Survival $\hat{S}(t)$")
        plt.xlabel("Time $t$")
        plt.legend(loc="best")
        plt.grid(alpha=0.3)
        plt.savefig(output_dir / f'kaplan_meier_{cat_col}.png')
        plt.close()

# EXPLAINER

class ModelWrapper:
    def __init__(self, predictor: TabularPredictor, feature_names: list, target_variable: str=None):
        self.ag_model = predictor
        self.feature_names = feature_names
        self.target_variable = target_variable
        if target_variable is None and predictor.problem_type != 'regression':
            print("Since target_class not specified, SHAP will explain predictions for each class")

    def predict_proba(self, X):
        if isinstance(X, pd.Series):
            X = X.values.reshape(1,-1)
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X, columns=self.feature_names)

        if self.ag_model.can_predict_proba:
            preds = self.ag_model.predict_proba(X)
        else:
            preds = self.ag_model.predict(X)
        return preds

@config_plot()
def plot_feature_importance(df: pd.DataFrame, output_dir: Path, model_name: str=''):
    """
    Plots feature importance with standard deviation and p-value significance.

    Args:
        df (pd.DataFrame): DataFrame containing the feature importance data. 
            Look at example for required format.
        output_dir (Path): Directory to save the feature importance plot.
        model_name (str): Optional name of the model, included in the plot title.

    Example:
        ```python
        import pandas as pd
        from pathlib import Path

        df = pd.DataFrame({
            'importance': [0.25, 0.18, 0.12, 0.10],
            'stddev': [0.03, 0.02, 0.01, 0.015],
            'p_value': [0.03, 0.07, 0.01, 0.2]
        }, index=['Feature A', 'Feature B', 'Feature C', 'Feature D'])

        plot_feature_importance(df, Path('./output'))
        ```
    """
    fig, ax = plt.subplots(figsize=(20, 12), dpi=72)

    bars = ax.bar(df.index, df['importance'], yerr=df['stddev'], capsize=5, color='skyblue', edgecolor='black')

    if 'p_value' in df.columns:
        for bar, p_value in zip(bars, df['p_value']):
            height = bar.get_height()
            significance = '*' if p_value < 0.05 else ''
            ax.text(bar.get_x() + bar.get_width() / 2.0, height + 0.002, significance,
                    ha='center', va='bottom', fontsize=10, color='red')

    ax.set_xlabel('Feature', fontsize=14)
    ax.set_ylabel('Importance', fontsize=14)
    ax.set_title(f'Feature Importance with Standard Deviation and p-value Significance ({model_name})', fontsize=16)
    ax.axhline(0, color='grey', linewidth=0.8)

    ax.set_xticks(np.arange(len(df.index.values)))
    ax.set_xticklabels(df.index.values, rotation=60, ha='right', fontsize=10)

    ax.grid(axis='y', linestyle='--', alpha=0.7)

    significance_patch = plt.Line2D([0], [0], color='red', marker='*', linestyle='None', markersize=10, label='p < 0.05')
    ax.legend(handles=[significance_patch], loc='upper right', fontsize=12)

    plt.tight_layout()
    fig.savefig(output_dir / 'feature_importance.png')
    plt.close()

@config_plot()
def plot_shap_values(
        predictor: TabularPredictor,
        X_train: pd.DataFrame,
        X_test: pd.DataFrame,
        output_dir: Path,
        max_display: int = 10,
    ) -> None:
    """
    Generates and saves SHAP value visualizations, including a heatmap and a bar plot, for a autogluon tabular model.

    Args:
        predictor (TabularPredictor): The trained tabular predictor model for which SHAP values are calculated.
        X_train (pd.DataFrame): Training dataset used to create the SHAP background data.
        X_test (pd.DataFrame): Test dataset used to evaluate and compute SHAP values.
        output_dir (Path): Directory to save the SHAP value visualizations.
        max_display (int): Maximum number of features to display in the visualizations. Defaults to 10.
    """
    predictor = ModelWrapper(predictor, X_train.columns)
    background_data = shap.sample(X_train, 100)
    shap_exp = shap.KernelExplainer(predictor.predict_proba, background_data)

    # sample 100 samples from test set to evaluate with shap values
    test_data = shap.sample(X_test, 100)

    # Compute SHAP values for the test set
    shap_values = shap_exp(test_data)

    sns.set_theme(style="darkgrid")
    fig, ax = plt.subplots(figsize=(20, 12), dpi=72)
    shap.plots.heatmap(shap_values[...,1], max_display=max_display, show=False, ax=ax)
    fig.savefig(output_dir / 'shap_heatmap.png')
    plt.close()

    fig, ax = plt.subplots(figsize=(20, 12), dpi=72)
    shap.plots.bar(shap_values[...,1], max_display=max_display, show=False, ax=ax)
    fig.savefig(output_dir / 'shap_barplot.png')
    plt.close()

def plot_violin_of_bootstrapped_metrics(
        trainer,
        X_test: pd.Series,
        y_test: pd.Series,
        X_val: pd.Series,
        y_val: pd.Series,
        X_train: pd.Series,
        y_train: pd.Series,
        output_dir: Path
    ) -> None:
    """
    Generates violin plots for bootstrapped model performance metrics across train, validation, and test datasets.

    Args:
        trainer (TrainerSupervised): The trained model predictor for evaluating performance metrics.
        X_test (pd.Series): Test features dataset.
        y_test (pd.Series): Test target values.
        X_val (pd.Series): Validation features dataset.
        y_val (pd.Series): Validation target values.
        X_train (pd.Series): Training features dataset.
        y_train (pd.Series): Training target values.
        output_dir (Path): Directory to save the generated violin plots.
    """
    # Define metrics based on the problem type
    if trainer.settings.task == 'regression':
        metrics = [('R Squared', r2_score), ('Root Mean Squared Error', root_mean_squared_error)]
    elif trainer.settings.task == 'binary':
        metrics = [('AUROC', roc_auc_score), ('AUPRC', auprc)]
    elif trainer.settings.task == 'survival':
        metrics = [('Concordance Index', ci_wrapper)]

    # Prepare lists for DataFrame
    results = []

    # Loop through models and metrics to compute bootstrapped values
    for model_name in trainer.model_names():
        y_pred_test = trainer.infer(X_test, model=model_name)
        y_pred_val = trainer.infer(X_val, model=model_name)
        y_pred_train = trainer.infer(X_train, model=model_name)

        for metric_name, metric_func in metrics:
            test_values = bootstrap_metric(y_test.to_numpy(), y_pred_test, metric_func)
            results.extend([(model_name, metric_name, 'Test', value) for value in test_values])

            val_values = bootstrap_metric(y_val.to_numpy(), y_pred_val, metric_func)
            results.extend([(model_name, metric_name, 'Validation', value) for value in val_values])

            train_values = bootstrap_metric(y_train.to_numpy(), y_pred_train, metric_func)
            results.extend([(model_name, metric_name, 'Train', value) for value in train_values])

    # Create a results DataFrame
    result_df = pd.DataFrame(results, columns=['model', 'metric', 'data_split', 'value'])

     # Sort models by median metric value within each combination of metric and data_split
    model_order_per_split = {}
    for split in ['Test', 'Validation', 'Train']:
        split_order = (
            result_df[result_df['data_split'] == split]
            .groupby(['metric', 'model'])['value']
            .median()
            .reset_index()
            .sort_values(by=['metric', 'value'], ascending=[True, False])
            .groupby('metric')['model']
            .apply(list)
            .to_dict()
        )
        model_order_per_split[split] = split_order

    # Function to create violin plots for a specific data split
    def create_violin_plot(data_split, save_path):
        sns.set_theme(style="darkgrid")
        subset = result_df[result_df['data_split'] == data_split]
        g = sns.FacetGrid(
            subset,
            col="metric",
            margin_titles=True,
            height=4,
            aspect=1.5,
            sharex=False,
        )

        # Create violin plots with sorted models
        def violin_plot(data, **kwargs):
            metric = data.iloc[0]['metric']
            order = model_order_per_split[data_split].get(metric, None)
            sns.violinplot(data=data, x="value", y="model", linewidth=1, order=order, **kwargs)

        g.map_dataframe(violin_plot)

        # Adjust the titles and axis labels
        g.set_titles(col_template="{col_name}")
        g.set_axis_labels("", "Model")

        # Add overall title and adjust layout
        g.figure.suptitle(f"Model Performance of {data_split} Data (Bootstrapped)", fontsize=16)
        g.tight_layout(w_pad=0.5, h_pad=1)

        # Save the plot
        g.savefig(save_path, dpi=500)
        plt.close()

    # Generate and save plots for each data split
    create_violin_plot('Test', output_dir / 'test_metrics_bootstrap.png')
    create_violin_plot('Validation', output_dir / 'validation_metrics_bootstrap.png')
    create_violin_plot('Train', output_dir / 'train_metrics_bootstrap.png')

@config_plot()
def plot_regression_diagnostics(
        y_true: np.ndarray, 
        y_pred: np.ndarray, 
        output_dir: Path
    ) -> None:
    """
    Generates diagnostic plots for evaluating a regression model.

    Plots:
        - True vs. Predicted values plot.
        - Residuals plot.
        - Histogram of residuals.

    Args:
        y_true (np.ndarray): Array of true target values.
        y_pred (np.ndarray): Array of predicted values from the regression model.
        output_dir (Path): Directory to save the diagnostic plots.
    """
    residuals = y_true - y_pred
    
    # Regression Line
    plt.figure(figsize=(10, 6))
    sns.set_theme(style="darkgrid")
    sns.scatterplot(x=y_true, y=y_pred, alpha=0.5)
    sns.lineplot(x=y_true, y=y_true, color='red')  # Perfect prediction line
    plt.xlabel('True Values')
    plt.ylabel('Predictions')
    plt.title('True vs Predicted Values')
    plt.savefig(output_dir / 'true_vs_predicted.png')
    plt.close()

    # Residuals
    plt.figure(figsize=(10, 6))
    sns.set_theme(style="darkgrid")
    sns.scatterplot(x=y_pred, y=residuals, alpha=0.5)
    plt.axhline(0, color='red', linestyle='--')
    plt.xlabel('Fitted Values')
    plt.ylabel('Residuals')
    plt.title('Residual Plot')
    plt.savefig(output_dir / 'residual_plot.png')
    plt.close()

    # Residual Histogram
    plt.figure(figsize=(10, 6))
    sns.set_theme(style="darkgrid")
    sns.histplot(residuals, kde=True, bins=30)
    plt.xlabel('Residuals')
    plt.title('Histogram of Residuals')
    plt.savefig(output_dir / 'residual_hist.png')
    plt.close()

@config_plot()
def plot_classification_diagnostics(
        y_test: pd.DataFrame,
        y_test_pred: pd.DataFrame,
        y_val: pd.DataFrame,
        y_val_pred: pd.DataFrame,
        y_train: pd.DataFrame,
        y_train_pred: pd.DataFrame,
        output_dir: Path
    ) -> None:
    """
    Generates diagnostic plots for evaluating a classification model.

    Plots:
        - Epic model evaluation plots (ROC Curve, Precision-Recall Curve, Calibration Curve, Sensitivity/Flag Curve).
        - Confusion Matrix.

    Args:
        y_test (pd.DataFrame): True labels for the test dataset.
        y_test_pred (pd.DataFrame): Predicted probabilities for the test dataset.
        y_val (pd.DataFrame): True labels for the validation dataset.
        y_val_pred (pd.DataFrame): Predicted probabilities for the validation dataset.
        y_train (pd.DataFrame): True labels for the training dataset.
        y_train_pred (pd.DataFrame): Predicted probabilities for the training dataset.
        output_dir (Path): Directory to save the diagnostic plots.
    """
    plot_epic_copy(
        y_test.to_numpy(),
        y_test_pred.to_numpy(),
        y_val.to_numpy(),
        y_val_pred.to_numpy(),
        y_train.to_numpy(),
        y_train_pred.to_numpy() ,
        output_dir
    )

    conf_matrix = confusion_matrix(y_test, y_test_pred.apply(lambda x: 1 if x >= 0.5 else 0))

    plt.figure(figsize=(8, 6))
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    plt.savefig(output_dir / 'confusion_matrix.png')
    plt.close()


@config_plot()
def plot_dashboard(
        significant_results: list[dict[str, Any]],
        data: pd.DataFrame,
        output_dir: Path,
    ) -> Path:
    """
    Create a grid of violinplots for significant results, showing the distribution
    of continuous variables across categorical variables.

    Args:
        significant_results (list[dict[str, Any]]): List of significant results from statistical analysis.
            Each dict should contain 'categorical_var', 'continuous_var', and 'p_value'.
        data (pd.DataFrame): The original dataframe containing all variables.
        output_dir (Path): Directory to save the output plot.

    Returns:
        Path: Path to the saved dashboard violinplot image.
    """
    # Extract unique categorical-continuous variable pairs from significant results
    plot_pairs = []
    seen_pairs = set()
    
    for result in significant_results:
        cat_var = result.get('categorical_var')
        cont_var = result.get('continuous_var')
        p_value = result.get('p_value', None)
        
        if cat_var and cont_var and (cat_var, cont_var) not in seen_pairs:
            seen_pairs.add((cat_var, cont_var))
            plot_pairs.append({
                'cat_var': cat_var,
                'cont_var': cont_var,
                'p_value': p_value
            })
    
    if len(plot_pairs) == 0:
        raise ValueError("No valid categorical-continuous variable pairs found in significant results.")
    
    # Determine grid layout
    n_plots = len(plot_pairs)
    if n_plots <= 4:
        cols = 2
    elif n_plots <= 9:
        cols = 3
    elif n_plots <= 16:
        cols = 4
    else:
        cols = 5
    
    rows = math.ceil(n_plots / cols)
    
    # Create figure with subplots
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 4), dpi=150)
    
    # Handle single subplot case
    if n_plots == 1:
        axes = np.array([axes])
    elif rows == 1 or cols == 1:
        axes = axes.reshape(-1)
    else:
        axes = axes.flatten()
    
    # Create violinplots
    for idx, pair_info in enumerate(plot_pairs):
        ax = axes[idx]
        cat_var = pair_info['cat_var']
        cont_var = pair_info['cont_var']
        p_value = pair_info['p_value']
        
        # Create violinplot
        try:
            sns.violinplot(
                x=cat_var,
                y=cont_var,
                data=data,
                ax=ax,
                inner="point",
                palette="Set2"
            )
            
            # Add statistical annotations
            n_categories = data[cat_var].nunique()
            # Use bonferroni correction for multiple comparisons if >2 groups
            correction = 'bonferroni' if n_categories > 2 else None
            add_stat_annotation(ax, data, cat_var, cont_var, 
                              test='auto', 
                              comparisons_correction=correction,
                              text_format='star', 
                              loc='inside')
            
            # Rotate x-axis labels if needed
            if n_categories > 5:
                ax.tick_params(axis='x', labelrotation=45)
            
            # Set title with overall p-value if available
            if p_value is not None:
                ax.set_title(f"{cat_var} vs {cont_var}\n(overall p={p_value:.4f})")
            else:
                ax.set_title(f"{cat_var} vs {cont_var}")
            
            # Adjust labels
            ax.set_xlabel(cat_var)
            ax.set_ylabel(cont_var)
            
        except Exception as e:
            logger.warning(f"Could not create violinplot for {cat_var} vs {cont_var}: {e}")
            ax.text(0.5, 0.5, f"Error plotting\n{cat_var} vs {cont_var}",
                    ha='center', va='center', transform=ax.transAxes)
            ax.set_xticks([])
            ax.set_yticks([])
    
    # Hide unused subplots
    for idx in range(n_plots, len(axes)):
        axes[idx].axis('off')
    
    # Add overall title
    fig.suptitle("Dashboard: Significant Variable Relationships", fontsize=16, y=0.98)
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    # Save figure
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'dashboard_violinplots.png'
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    
    return output_path


def add_stat_annotation(ax, data, x, y, test='auto', comparisons_correction=None, 
                       text_format='star', loc='inside', verbose=0):
    """
    Add statistical annotations (brackets and significance markers) to a plot.
    
    Args:
        ax: Matplotlib axis object
        data: DataFrame containing the data
        x: Name of the categorical variable (x-axis)
        y: Name of the continuous variable (y-axis)
        test: Statistical test to use ('t-test_ind', 'Mann-Whitney', 'auto')
        comparisons_correction: Method for multiple comparisons correction ('bonferroni', 'holm', etc.)
        text_format: Format for p-value display ('star', 'simple', 'full')
        loc: Location of annotations ('inside' or 'outside')
        verbose: Verbosity level
    """
    from scipy.stats import mannwhitneyu, kruskal
    import warnings
    warnings.filterwarnings('ignore')
    
    # Get unique groups
    groups = sorted(data[x].unique())
    n_groups = len(groups)
    
    if n_groups < 2:
        return
    
    # Get positions of groups on x-axis
    positions = list(range(n_groups))
    
    # Calculate y-axis range for bracket positioning
    y_max = data[y].max()
    y_min = data[y].min()
    y_range = y_max - y_min
    
    # Starting height for brackets
    if loc == 'inside':
        h = y_max + 0.02 * y_range
    else:
        h = y_max + 0.08 * y_range
    
    # Format p-value based on text_format
    def format_pvalue(p):
        if text_format == 'star':
            if p < 0.001:
                return '***'
            elif p < 0.01:
                return '**'
            elif p < 0.05:
                return '*'
            else:
                return 'ns'
        elif text_format == 'simple':
            if p < 0.001:
                return 'p<0.001'
            else:
                return f'p={p:.3f}'
        else:  # full
            return f'p={p:.4f}'
    
    if n_groups == 2:
        # Two groups: single comparison
        group1_data = data[data[x] == groups[0]][y].dropna()
        group2_data = data[data[x] == groups[1]][y].dropna()
        
        # Perform statistical test
        if test == 'auto':
            # Check normality and choose test
            if len(group1_data) >= 20 and len(group2_data) >= 20:
                _, p_value = ttest_ind(group1_data, group2_data)
            else:
                _, p_value = mannwhitneyu(group1_data, group2_data)
        elif test == 't-test_ind':
            _, p_value = ttest_ind(group1_data, group2_data)
        elif test == 'Mann-Whitney':
            _, p_value = mannwhitneyu(group1_data, group2_data)
        
        # Draw bracket
        x1, x2 = positions[0], positions[1]
        
        # Horizontal lines
        ax.plot([x1, x1, x2, x2], [h, h + 0.01 * y_range, h + 0.01 * y_range, h], 
                lw=1.5, c='black')
        
        # Add text
        ax.text((x1 + x2) * 0.5, h + 0.02 * y_range, format_pvalue(p_value), 
                ha='center', va='bottom')
    
    else:
        # Multiple groups: pairwise comparisons
        # First perform overall test
        group_data = [data[data[x] == g][y].dropna() for g in groups]
        
        # Check if all values are identical across groups to avoid Kruskal error
        all_values = pd.concat(group_data)
        if len(all_values.unique()) == 1:
            # All values are identical, no statistical difference possible
            return
        
        try:
            if test == 'auto' or test == 'Kruskal':
                _, overall_p = kruskal(*group_data)
            else:
                _, overall_p = f_oneway(*group_data)
        except ValueError as e:
            # Handle edge cases where statistical test fails
            logger.warning(f"Statistical test failed for {x} vs {y}: {e}")
            return
        
        if overall_p < 0.05:
            # Perform post-hoc pairwise comparisons
            comparisons = []
            p_values = []
            
            # Get all pairs
            from itertools import combinations as iter_combinations
            for (i, group1), (j, group2) in iter_combinations(enumerate(groups), 2):
                group1_data = data[data[x] == group1][y].dropna()
                group2_data = data[data[x] == group2][y].dropna()
                
                if test == 'auto':
                    if len(group1_data) >= 20 and len(group2_data) >= 20:
                        _, p = ttest_ind(group1_data, group2_data)
                    else:
                        _, p = mannwhitneyu(group1_data, group2_data)
                elif test == 't-test_ind':
                    _, p = ttest_ind(group1_data, group2_data)
                elif test == 'Mann-Whitney':
                    _, p = mannwhitneyu(group1_data, group2_data)
                
                comparisons.append((i, j))
                p_values.append(p)
            
            # Apply multiple comparisons correction
            if comparisons_correction == 'bonferroni':
                p_values = [min(p * len(p_values), 1.0) for p in p_values]
            elif comparisons_correction == 'holm':
                # Holm-Bonferroni correction
                sorted_p = sorted(enumerate(p_values), key=lambda x: x[1])
                for idx, (original_idx, p) in enumerate(sorted_p):
                    sorted_p[idx] = (original_idx, min(p * (len(p_values) - idx), 1.0))
                p_values = [p for _, p in sorted(sorted_p, key=lambda x: x[0])]
            
            # Find the most significant comparison (lowest p-value that's < 0.05)
            significant_comparisons = [(i, comp, p) for i, (comp, p) in enumerate(zip(comparisons, p_values)) if p < 0.05]
            
            if significant_comparisons:
                # Get the comparison with the lowest p-value
                most_sig_idx, most_sig_comp, most_sig_p = min(significant_comparisons, key=lambda x: x[2])
                i, j = most_sig_comp
                
                # Draw bracket for only the most significant comparison
                x1, x2 = positions[i], positions[j]
                
                # Draw bracket
                ax.plot([x1, x1, x2, x2], 
                       [h, h + 0.01 * y_range, 
                        h + 0.01 * y_range, h], 
                       lw=1.5, c='black')
                
                # Add text
                ax.text((x1 + x2) * 0.5, h + 0.02 * y_range, 
                       format_pvalue(most_sig_p), ha='center', va='bottom')
    
    # Adjust y-axis limits if needed
    current_ylim = ax.get_ylim()
    if loc == 'outside':
        ax.set_ylim(current_ylim[0], max(current_ylim[1], h + 0.1 * y_range))


@config_plot()
def plot_violinplot_with_stats(
        data: pd.DataFrame,
        x: str,
        y: str,
        output_dir: Path,
        test: str = 'auto',
        comparisons_correction: str = None,
        text_format: str = 'star',
        loc: str = 'inside',
        figsize: tuple = (8, 6),
        palette: str = 'Set2',
        title: str = None
    ) -> Path:
    """
    Create a violin plot with statistical significance annotations.
    
    Args:
        data: DataFrame containing the data
        x: Name of the categorical variable (x-axis)
        y: Name of the continuous variable (y-axis)
        output_dir: Directory to save the output plot
        test: Statistical test to use ('auto', 't-test_ind', 'Mann-Whitney', 'Kruskal')
        comparisons_correction: Method for multiple comparisons ('bonferroni', 'holm', None)
        text_format: Format for p-value display ('star', 'simple', 'full')
        loc: Location of annotations ('inside' or 'outside')
        figsize: Figure size as (width, height)
        palette: Color palette for violin plot
        title: Plot title (if None, auto-generated)
    
    Returns:
        Path: Path to the saved plot
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Create violin plot
    sns.violinplot(x=x, y=y, data=data, ax=ax, inner="point", palette=palette)
    
    # Add statistical annotations
    add_stat_annotation(ax, data, x, y, test=test, 
                       comparisons_correction=comparisons_correction,
                       text_format=text_format, loc=loc)
    
    # Rotate x-axis labels if many categories
    if data[x].nunique() > 5:
        ax.tick_params(axis='x', labelrotation=45)
    
    # Set title
    if title is None:
        title = f"{x} vs {y}"
    ax.set_title(title)
    
    # Save plot
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f'{x}_vs_{y}_with_stats.png'
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path
