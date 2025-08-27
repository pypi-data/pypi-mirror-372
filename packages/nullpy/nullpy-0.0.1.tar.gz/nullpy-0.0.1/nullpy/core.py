# nullpy.py
# A Python library for intelligent, data-aware cleaning of pandas DataFrames.

# --- Core Dependencies ---
import pandas as pd
import numpy as np
import warnings
from typing import List, Dict, Any, Optional, Tuple

# --- Machine Learning Dependencies (Scikit-learn) ---
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, r2_score
from scipy.stats import chi2_contingency

# --- Rich for Enhanced Console Output ---
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.theme import Theme

# --- Suppress specific warnings for a cleaner output ---
import warnings
warnings.filterwarnings("ignore")

# --- Custom Theme for Rich Console ---
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "danger": "bold red",
    "report_title": "bold green",
    "report_header": "white",
})

class SmartDFCleaner:
    """
    An intelligent DataFrame cleaner that automatically analyzes data characteristics
    to apply the most suitable cleaning and imputation strategies.
    """

    def __init__(self,
                 target_column: Optional[str] = None,
                 impute_strategy: str = 'auto',
                 outlier_strategy: str = 'auto',
                 verbose: bool = True,
                 show_difference: bool = False):
        """
        Initializes the SmartDFCleaner.

        Args:
            target_column (Optional[str]): The name of the target variable.
                Required for target-aware predictive imputation.
            impute_strategy (str): The strategy for imputing missing values.
                Options: 'auto', 'mean', 'median', 'mode', 'predictive'.
            outlier_strategy (str): The strategy for handling outliers.
                Options: 'auto', 'clip', 'drop', 'predictive'.
            verbose (bool): If True, prints detailed logs and reports of the cleaning process.
            show_difference (bool): If True, shows a comparison of the DataFrame
                before and after cleaning.
        """
        self.target_column = target_column
        self.impute_strategy = impute_strategy
        self.outlier_strategy = outlier_strategy
        self.verbose = verbose
        self.show_difference = show_difference

        # Internal state
        self.models_: Dict[str, Any] = {}
        self.report_: List[Dict[str, Any]] = []
        self.original_df_shape_: Optional[Tuple[int, int]] = None
        self.cleaned_df_shape_: Optional[Tuple[int, int]] = None

        # Initialize rich console
        self.console = Console(theme=custom_theme)

    def _log(self, message: str, style: str = "info"):
        """Prints a message to the console if verbose is True."""
        if self.verbose:
            self.console.print(f"[{style}]> {message}[/]", highlight=False)

    def _identify_column_types(self, df: pd.DataFrame) -> Tuple[List[str], List[str], List[str]]:
        """
        Identifies numerical, categorical, and datetime columns in the DataFrame.
        """
        numerical_cols = df.select_dtypes(include=np.number).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_cols = df.select_dtypes(include=['datetime', 'timedelta']).columns.tolist()

        # Ensure target column is not treated as a feature
        if self.target_column:
            if self.target_column in numerical_cols:
                numerical_cols.remove(self.target_column)
            if self.target_column in categorical_cols:
                categorical_cols.remove(self.target_column)
            if self.target_column in datetime_cols:
                datetime_cols.remove(self.target_column)

        return numerical_cols, categorical_cols, datetime_cols

    def _check_correlation(self, df: pd.DataFrame, feature_col: str) -> bool:
        """
        Checks if a feature has a significant correlation with the target column.
        """
        if not self.target_column or self.target_column not in df.columns:
            return False

        temp_df = df[[feature_col, self.target_column]].dropna()
        if temp_df.shape[0] < 20: # Not enough data to determine correlation
             return False

        target_is_numeric = pd.api.types.is_numeric_dtype(df[self.target_column])
        feature_is_numeric = pd.api.types.is_numeric_dtype(df[feature_col])

        # Case 1: Numeric Feature vs. Numeric Target
        if feature_is_numeric and target_is_numeric:
            correlation = temp_df[feature_col].corr(temp_df[self.target_column])
            is_significant = abs(correlation) > 0.3
            self._log(f"Correlation between '{feature_col}' and '{self.target_column}': {correlation:.2f}. Significant: {is_significant}")
            return is_significant

        # Case 2: Categorical Feature vs. Categorical Target
        elif not feature_is_numeric and not target_is_numeric:
            contingency_table = pd.crosstab(temp_df[feature_col], temp_df[self.target_column])
            chi2, p, _, _ = chi2_contingency(contingency_table)
            is_significant = p < 0.05 # Using p-value to determine significance
            self._log(f"Chi-squared test for '{feature_col}' and '{self.target_column}': p-value={p:.3f}. Significant: {is_significant}")
            return is_significant

        # Other cases (e.g., Numeric vs. Cat) are more complex (ANOVA).
        # For this library, we'll consider them not strongly correlated to keep it robust.
        return False

    def _impute_predictive(self, df: pd.DataFrame, col_to_impute: str) -> pd.DataFrame:
        """
        Imputes missing values in a column using a predictive machine learning model.
        """
        self._log(f"Applying [bold yellow]Predictive Imputation[/] for column: '{col_to_impute}'")

        # 1. Prepare data: Separate rows with and without the missing value
        df_with_null = df[df[col_to_impute].isnull()]
        df_without_null = df[df[col_to_impute].notnull()]

        if df_with_null.empty or df_without_null.empty:
            self._log(f"Not enough data to train a predictive model for '{col_to_impute}'. Skipping.", style="warning")
            return df

        # 2. Identify feature and target types
        is_classification = pd.api.types.is_categorical_dtype(df[col_to_impute]) or \
                            pd.api.types.is_object_dtype(df[col_to_impute])

        features = [col for col in df.columns if col != col_to_impute]
        X = df_without_null[features]
        y = df_without_null[col_to_impute]
        X_to_predict = df_with_null[features]

        # 3. Define preprocessing pipelines for features
        numeric_features, categorical_features, _ = self._identify_column_types(X)

        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())])

        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore'))])

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)])

        # 4. Select the model based on target type
        if is_classification:
            # Use RandomForest for its robustness
            model = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)
            model_name = "RandomForestClassifier"
        else:
            # Use RandomForestRegressor
            model = RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1)
            model_name = "RandomForestRegressor"

        # 5. Create and train the full pipeline
        pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                                   ('model', model)])

        try:
            pipeline.fit(X, y)
        except Exception as e:
            self._log(f"Failed to train predictive model for '{col_to_impute}'. This is likely due to incompatible feature types or insufficient data after dropping NaNs: {e}", style="danger")
            return df # Return original df on failure

        # 6. Predict and fill missing values
        predicted_values = pipeline.predict(X_to_predict)
        df.loc[df[col_to_impute].isnull(), col_to_impute] = predicted_values

        # 7. Store the trained model and report the action
        self.models_[f'impute_{col_to_impute}'] = pipeline
        self.report_.append({
            "Column": col_to_impute,
            "Action": "Impute Missing Values",
            "Method": "Predictive",
            "Model": model_name,
            "Details": f"{len(predicted_values)} values imputed."
        })
        return df

    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Orchestrates the process of handling missing values based on the chosen strategy.
        """
        cols_with_missing = df.isnull().sum()
        cols_with_missing = cols_with_missing[cols_with_missing > 0].index.tolist()

        for col in cols_with_missing:
            missing_percentage = df[col].isnull().sum() / len(df)
            is_numeric = pd.api.types.is_numeric_dtype(df[col])

            strategy = self.impute_strategy
            method_used = ""
            details = f"{df[col].isnull().sum()} missing values ({missing_percentage:.1%})"

            # --- Automatic Strategy Decision Logic ---
            if strategy == 'auto':
                if missing_percentage > 0.4:
                    strategy = 'median' if is_numeric else 'mode'
                    self._log(f"'{col}' has high missing data ({missing_percentage:.1%}). Using simple imputation.", style="warning")
                elif missing_percentage > 0.05 and self._check_correlation(df, col):
                    df = self._impute_predictive(df, col)
                    continue # Predictive imputation has its own reporting
                else:
                    strategy = 'median' if is_numeric else 'mode'

            # --- Predictive Strategy ---
            if strategy == 'predictive':
                 df = self._impute_predictive(df, col)
                 continue

            # --- Simple Imputation Strategies ---
            if is_numeric:
                if strategy == 'mean':
                    fill_value = df[col].mean()
                    method_used = "Mean"
                else: # Default to median for robustness to outliers
                    fill_value = df[col].median()
                    method_used = "Median"
            else: # Categorical
                mode_values = df[col].mode()
                if not mode_values.empty:
                    fill_value = mode_values[0]
                    method_used = "Mode"
                else:
                    self._log(f"Could not determine mode for column '{col}'. Skipping imputation.", style="warning")
                    continue


            df[col].fillna(fill_value, inplace=True)
            self.report_.append({
                "Column": col,
                "Action": "Impute Missing Values",
                "Method": method_used,
                "Details": details
            })
            self._log(f"Applied [bold green]{method_used} Imputation[/] to column '{col}'.")

        return df

    def _handle_outliers(self, df: pd.DataFrame, num_cols: List[str]) -> pd.DataFrame:
        """
        Orchestrates the process of handling outliers in numerical columns.
        """
        for col in num_cols:
            if df[col].nunique() <= 2: # Skip binary columns
                continue

            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]

            if not outliers.empty:
                strategy = self.outlier_strategy
                num_outliers = len(outliers)

                # --- Auto Strategy for Outliers ---
                if strategy == 'auto':
                    # If outliers are a small portion, clipping is a safe default.
                    strategy = 'clip'

                if strategy == 'clip':
                    df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
                    self.report_.append({
                        "Column": col,
                        "Action": "Handle Outliers",
                        "Method": "Clip (IQR)",
                        "Details": f"{num_outliers} outliers capped."
                    })
                    self._log(f"Clipped [bold cyan]{num_outliers} outliers[/] in column '{col}'.")

                elif strategy == 'drop':
                    df.drop(outliers.index, inplace=True)
                    self.report_.append({
                        "Column": col,
                        "Action": "Handle Outliers",
                        "Method": "Drop (IQR)",
                        "Details": f"{num_outliers} rows dropped."
                    })
                    self._log(f"Dropped [bold red]{num_outliers} rows[/] due to outliers in '{col}'.")

                elif strategy == 'predictive':
                    self._log(f"Marking outliers in '{col}' as missing for predictive imputation.", style="warning")
                    df.loc[outliers.index, col] = np.nan
                    # The missing value handler will now pick this up
                    # This requires running the missing value handler again
                    # For simplicity in this version, we will log and move on.
                    # A more advanced version could re-trigger the imputation.

        return df

    def _generate_report(self):
        """Generates and prints a summary report of all cleaning actions."""
        if not self.verbose or not self.report_:
            return

        table = Table(title="[report_title]Data Cleaning Summary Report[/]", header_style="report_header", show_lines=True)
        table.add_column("Column", justify="left", style="cyan", no_wrap=True)
        table.add_column("Action", justify="left", style="magenta")
        table.add_column("Method", justify="left", style="green")
        table.add_column("Details", justify="left")

        for action in self.report_:
            table.add_row(action["Column"], action["Action"], action["Method"], action["Details"])

        shape_info = f"Original Shape: {self.original_df_shape_} -> Cleaned Shape: {self.cleaned_df_shape_}"
        panel = Panel.fit(table, title="Cleaning Actions", border_style="white", subtitle=shape_info)
        self.console.print(panel)

    def _show_difference_report(self, original_df: pd.DataFrame, cleaned_df: pd.DataFrame):
        """
        Generates and prints a report showing the differences between the
        original and cleaned DataFrames.
        """
        if not self.show_difference:
            return

        self._log("Generating difference report...")

        # Using pandas.compare() for a direct cell-by-cell comparison
        try:
            # Align indices for accurate comparison
            original_aligned, cleaned_aligned = original_df.align(cleaned_df)
            diff = original_aligned.compare(cleaned_aligned, keep_shape=True, keep_equal=False)

            # Find indices where there are changes
            changed_indices = diff.dropna(how='all').index

            if changed_indices.empty:
                self._log("No changes detected between original and cleaned DataFrames.")
                return

            # Display a sample of the changed rows
            sample_indices = changed_indices[:10] # Show up to 10 changed rows

            original_sample = original_df.loc[sample_indices]
            cleaned_sample = cleaned_df.loc[sample_indices]

            # Create tables for comparison
            table_orig = Table(title="[bold yellow]Original Data (Sample of Changes)[/]", header_style="yellow")
            table_clean = Table(title="[bold green]Cleaned Data (Sample of Changes)[/]", header_style="green")

            for col in original_sample.columns:
                table_orig.add_column(str(col))
                table_clean.add_column(str(col))

            for index, row in original_sample.iterrows():
                table_orig.add_row(*[str(v) for v in row.values])

            for index, row in cleaned_sample.iterrows():
                table_clean.add_row(*[str(v) for v in row.values])

            self.console.print(table_orig)
            self.console.print(table_clean)

        except Exception as e:
            self._log(f"Could not generate difference report: {e}", style="danger")


    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies the complete cleaning pipeline to the DataFrame.

        Args:
            df (pd.DataFrame): The input DataFrame to clean.

        Returns:
            pd.DataFrame: The cleaned DataFrame.
        """
        self._log("Starting Smart Cleaning Process...", style="bold green")

        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame.")

        cleaned_df = df.copy()
        original_df = df.copy() if self.show_difference else None
        self.original_df_shape_ = df.shape
        self.report_ = [] # Reset report for new run

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console,
            disable=not self.verbose
        ) as progress:

            task1 = progress.add_task("[cyan]Analyzing Data[/]", total=4)

            # --- Step 1: Identify Column Types ---
            num_cols, cat_cols, _ = self._identify_column_types(cleaned_df)
            self._log(f"Identified {len(num_cols)} numerical and {len(cat_cols)} categorical features.")
            progress.update(task1, advance=1, description="[cyan]Identifying Column Types[/]")

            # --- Step 2: Handle Missing Values ---
            cleaned_df = self._handle_missing_values(cleaned_df)
            progress.update(task1, advance=1, description="[magenta]Imputing Missing Values[/]")

            # --- Step 3: Handle Outliers ---
            cleaned_df = self._handle_outliers(cleaned_df, num_cols)
            progress.update(task1, advance=1, description="[yellow]Handling Outliers[/]")

            # --- Step 4: Finalize and Report ---
            self.cleaned_df_shape_ = cleaned_df.shape
            self._generate_report()
            if self.show_difference and original_df is not None:
                self._show_difference_report(original_df, cleaned_df)
            progress.update(task1, advance=1, description="[green]Generating Reports[/]")

        self._log("Cleaning process completed successfully!", style="bold green")
        return cleaned_df
    def demo_report(self,
                    df: pd.DataFrame,
                    target_column: str,
                    auto_impute: str = "auto",
                    auto_outlier: str = "auto",
                    predictive_outlier: str = "clip",
                    verbose: bool = True,
                    show_difference: bool = True):
        """
        Runs a full demo cleaning report on the given DataFrame.
        Shows original data, auto-cleaned data, predictive-cleaned data,
        null counts, and summary reports in console.

        Args:
            df (pd.DataFrame): Input DataFrame
            target_column (str): Target variable name
            auto_impute (str): Imputation strategy for automatic cleaning
            auto_outlier (str): Outlier strategy for automatic cleaning
            predictive_outlier (str): Outlier strategy for predictive cleaning
            verbose (bool): Print detailed logs
            show_difference (bool): Show before/after difference report
        """
        console = Console(theme=custom_theme)

        # Show Original DF
        console.print(Panel.fit("[bold yellow]Original DataFrame[/]", border_style="yellow"))
        console.print(df)

        # --- Scenario 1: Fully Automatic Cleaning ---
        console.print(Panel.fit("[bold green]Scenario 1: Fully Automatic Cleaning[/]\nTarget-aware, auto strategies, verbose output, and difference report.", border_style="green"))

        cleaner_auto = SmartDFCleaner( # Corrected from self()
            target_column=target_column,
            impute_strategy=auto_impute,
            outlier_strategy=auto_outlier,
            verbose=verbose,
            show_difference=show_difference
        )
        cleaned_df_auto = cleaner_auto.fit_transform(df)

        console.print(Panel.fit("[white]Cleaned DataFrame (Auto)[/]", border_style="white"))
        console.print(cleaned_df_auto)
        console.print(f"Original Nulls:\n{df.isnull().sum().to_string()}")
        console.print(f"Cleaned Nulls:\n{cleaned_df_auto.isnull().sum().to_string()}")

        # --- Scenario 2: Forced Predictive Imputation ---
        console.print(Panel.fit("[bold magenta]Scenario 2: Forced Predictive Imputation[/]\nUsing 'predictive' strategy for all missing values.", border_style="magenta"))

        cleaner_predictive = SmartDFCleaner( # Corrected from self()
            target_column=target_column,
            impute_strategy="predictive",
            outlier_strategy=predictive_outlier,
            verbose=verbose,
            show_difference=False
        )
        cleaned_df_predictive = cleaner_predictive.fit_transform(df)

        console.print(Panel.fit("[white]Cleaned DataFrame (Predictive)[/]", border_style="white"))
        console.print(cleaned_df_predictive)

        return cleaned_df_auto, cleaned_df_predictive
    def clean_it(
                 self,
                    df: pd.DataFrame,
                    target_column: str,
                    auto_impute: str = "auto",
                    auto_outlier: str = "auto",
                    predictive_outlier: str = "clip",
                    verbose: bool = True,
                    show_difference: bool = True):
      if (verbose) : self.demo_report(df, target_column, auto_impute, auto_outlier, predictive_outlier, verbose, show_difference)
      newdf = self.fit_transform(df)
      return newdf