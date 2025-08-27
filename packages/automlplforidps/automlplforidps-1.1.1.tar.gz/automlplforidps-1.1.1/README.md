# AutoML Pipeline for Tabular Classification

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/automlplforidps.svg)](https://badge.fury.io/py/automlplforidps)

A comprehensive, automated pipeline for multiclass classification on tabular data. This project is engineered to dramatically simplify the machine learning workflow, from raw data to a deployable, high-performance model. It intelligently handles preprocessing, feature engineering, and hyperparameter tuning, making it an ideal tool for complex classification tasks like those in Intrusion Detection and Prevention Systems (IDPS).

The core philosophy is to provide a robust, automated, and transparent process that not only produces a model but also saves all the necessary components (artifacts) for making predictions on new data.

## Core Features

- **End-to-End Automation:** Manages the entire ML pipeline: data cleaning, balancing, feature scaling, intelligent feature selection, and advanced hyperparameter optimization.
- **Robust Preprocessing:** Imputes missing data, handles infinite values, and automatically encodes both categorical features and target labels.
- **Advanced Data Balancing:** Employs a sophisticated hybrid strategy using **BorderlineSMOTE** to generate synthetic data points along the decision boundary between classes, rather than deep within a class. This creates more useful and robust decision surfaces.
- **Intelligent Feature Selection:** Leverages **Particle Swarm Optimization (PSO)**, a powerful bio-inspired algorithm, to discover the optimal subset of features, reducing model complexity and improving generalization.
- **Sophisticated Hyperparameter Tuning:** Utilizes **Bayesian Search Cross-Validation** to efficiently navigate complex search spaces and find the best hyperparameters for multiple models, converging on optimal solutions faster than random search.
- **Multi-Model Evaluation:** Trains, tunes, and evaluates three powerful and popular models: **RandomForest**, **XGBoost**, and **CatBoost**.
- **Automatic Artifact Persistence:** Automatically saves the best-performing model along with the corresponding data scaler, label encoder, and the list of selected features into a single, portable `classification_artifacts.joblib` file for easy deployment.

## Installation

To get started, install the package using pip
```bash
pip install automlplforidps
```

 Or clone this repository and install the required dependencies. It is highly recommended to use a virtual environment.

```bash
# Clone the repository
git clone https://github.com/your-username/autoMLplforIDPS.git
cd autoMLplforIDPS

# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install the project in editable mode
pip install -e .
```

This project requires **Python 3.12+**. All dependencies are listed in `pyproject.toml`.

## The AutoML Workflow: From Training to Prediction

Using the pipeline is a two-stage process. First, you train the pipeline on your historical data. During this phase, the pipeline performs all the automated ML steps and saves the resulting artifacts. Second, you load these artifacts to make predictions on new, unseen data.

### Part 1: Training the Pipeline & Saving Artifacts

This is the main training step. You provide your dataset, and the pipeline handles the rest.

```python
from automlplforidps import run_classification_pipeline

def run_training_pipeline():
    """
    Runs the full training pipeline and saves the best model and artifacts.
    """
    print("--- PART 1: TRAINING AND SAVING THE BEST MODEL ---")
    
    # Provide the path to your dataset and the name of the target column
    my_file_path = 'path/to/your/dataset.csv'
    my_target_column = 'your_target_label'

    try:
        # This single function call executes the entire automated workflow
        trained_models = run_classification_pipeline(
            file_path=my_file_path,
            target_column=my_target_column
        )
        
        if trained_models:
            print("\n✅ Pipeline training complete. Artifacts have been saved to 'classification_artifacts.joblib'")
        else:
            print("\n❌ Pipeline training failed.")
            
    except Exception as e:
        print(f"\nAn error occurred during training: {e}")
        print("Please ensure 'path/to/your/dataset.csv' is a valid file path.")

# Execute the training process
run_training_pipeline()
```

### Part 2: Loading Artifacts & Making Predictions

After the training is complete and `classification_artifacts.joblib` has been created, you can use it to build a prediction service.

```python
import pandas as pd
import numpy as np
import joblib

def run_prediction_on_new_data():
    """
    Loads the saved artifacts to make a prediction on new data.
    """
    print("\n\n--- PART 2: LOADING ARTIFACTS FOR A NEW PREDICTION ---")
    
    try:
        # Load the dictionary of artifacts saved during training
        artifacts = joblib.load('classification_artifacts.joblib')
        model = artifacts['model']
        scaler = artifacts['scaler']
        label_encoder = artifacts['label_encoder']
        selected_features = artifacts['selected_features']
        
        print("✅ Successfully loaded model and artifacts.")
        print(f"The model was trained on these {len(selected_features)} features: {selected_features}")
        
        # --- Create a new data sample for prediction ---
        # IMPORTANT: The new data MUST have the same feature columns (and names) 
        # that the model was originally trained on.
        
        # This sample is randomly generated for demonstration.
        # Replace this with your actual new data.
        new_sample_values = np.random.rand(1, len(selected_features))
        new_data = pd.DataFrame(new_sample_values, columns=selected_features)
        
        print("\nGenerated a new sample for prediction:")
        print(new_data)
        
        # The prediction process must follow these steps:
        # 1. Scale the new data using the *loaded* scaler
        new_data_scaled = scaler.transform(new_data)
        
        # 2. Make the prediction
        prediction_encoded = model.predict(new_data_scaled)
        
        # 3. Decode the prediction from its numeric form back to the original label
        prediction_label = label_encoder.inverse_transform(prediction_encoded)
        
        print(f"\n---> 🚀 Model Prediction: '{prediction_label[0]}'")

    except FileNotFoundError:
        print("\n❌ Error: 'classification_artifacts.joblib' not found.")
        print("Please run the training pipeline first to generate the artifacts.")
    except Exception as e:
        print(f"\nAn error occurred during prediction: {e}")

# Execute the prediction process
run_prediction_on_new_data()
```

## Pipeline Stages in Detail

The `run_classification_pipeline` function executes the following sequence of steps:

1.  **Load & Preprocess Data**:
    - Reads the dataset from the provided CSV file path.
    - Replaces any infinite values (`inf`, `-inf`) with `NaN`.
    - Imputes missing numerical values using the `median` and categorical values using the `most_frequent` strategy.
    - Encodes all categorical features and boolean values into numerical representations.
    - Encodes the target variable into integer labels and stores the mapping in a `LabelEncoder` object.

2.  **Balance Data**:
    - To address class imbalance, a hybrid sampling strategy is applied.
    - **BorderlineSMOTE**: An advanced oversampling technique that focuses on generating synthetic data points along the decision boundary between classes, rather than deep within a class. This creates more useful and robust decision surfaces.
    - **TomekLinks**: An undersampling technique used for cleaning. It identifies pairs of very close instances that belong to different classes and removes the instance from the majority class, clarifying the class boundary.

3.  **Normalize Features**:
    - All numerical features are scaled using `StandardScaler`. This standardizes features by removing the mean and scaling to unit variance.
    - The fitted `scaler` object is saved to be used later for scaling new data during prediction, ensuring consistency.

4.  **Feature Engineering (PSO)**:
    - **Particle Swarm Optimization (PSO)** is used to select the most informative subset of features.
    - PSO is a metaheuristic inspired by the social behavior of bird flocking. It initializes a "swarm" of "particles" (potential feature subsets) and iteratively moves them through the feature space to find the combination that yields the best model performance (minimizing `log_loss` in this case).
    - This step is crucial for reducing noise, preventing overfitting, and potentially speeding up prediction times.

5.  **Tune & Evaluate Models**:
    - The pipeline trains and tunes three different models: RandomForest, XGBoost, and CatBoost.
    - For each model, **Bayesian Hyperparameter Optimization** is used to find the best set of hyperparameters (e.g., `n_estimators`, `max_depth`). Bayesian optimization builds a probability model of the objective function and uses it to select the most promising hyperparameters to evaluate, making it more efficient than random or grid search.
    - Each model is evaluated on a hold-out test set, and its overall accuracy and per-class recall are printed.

6.  **Save Artifacts**:
    - The pipeline identifies the model with the highest overall accuracy on the test set as the "best" model.
    - It then saves the following essential components into a single file named `classification_artifacts.joblib`:
        - `model`: The best-performing, fully trained model object.
        - `scaler`: The `StandardScaler` object fitted on the training data.
        - `label_encoder`: The `LabelEncoder` object for the target variable.
        - `selected_features`: The list of feature names selected by the PSO algorithm.

## Customization and Configuration

You can customize the pipeline's behavior by passing a configuration dictionary to the `run_classification_pipeline` function. If no config is provided, the default settings are used.

**Example of overriding default settings:**
```python
from automlplforidps import run_classification_pipeline

# Define custom parameters
custom_config = {
    "random_state": 101,
    "train_size": 0.75,
    "pso_iterations": 15,
    "pso_population_size": 25,
    "bayes_iterations": 30,
    "cv_folds": 5,
}

# Run the pipeline with the custom configuration
run_classification_pipeline(
    file_path='path/to/your/dataset.csv',
    target_column='your_target_label',
    config=custom_config
)
```

### All Configuration Options

The following table details all the available parameters in the configuration dictionary.

| Parameter             | Description                                                                                                   | Default Value |
| --------------------- | ------------------------------------------------------------------------------------------------------------- | ------------- |
| `random_state`        | The seed for all random operations, ensuring reproducibility.                                                 | `42`          |
| `train_size`          | The proportion of the dataset to allocate to the training set (the rest becomes the test set).                | `0.8`         |
| `pso_iterations`      | The number of iterations the Particle Swarm Optimization algorithm will run for feature selection.            | `10`          |
| `pso_population_size` | The number of "particles" (feature subsets) in the swarm for each PSO iteration.                              | `20`          |
| `bayes_iterations`    | The number of iterations the Bayesian Search will run for hyperparameter tuning for each model.               | `25`          |
| `cv_folds`            | The number of folds to use for cross-validation within the Bayesian Search hyperparameter tuning process.     | `3`           |

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## License

This project is distributed under the MIT License. See the `LICENSE` file for more information.
