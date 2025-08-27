import pandas as pd
import numpy as np
import pickle
import warnings
from typing import Dict, Any, List, Optional, Union
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge, Lasso
from sklearn.svm import SVC, SVR
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.naive_bayes import GaussianNB
import os

warnings.filterwarnings('ignore')

class MLAutoTrainer:
    """
    Complete Machine Learning Library for Automatic Model Selection and Training
    """
    
    def __init__(self):
        # Default hyperparameters for each algorithm
        self.default_hyperparams = {
            'classification': {
                'test_size': 0.25,
                'cv': 5,
                'random_state': 42,
            },
            'regression': {
                'test_size': 0.25,
                'cv': 5,
                'random_state': 42,
            }
        }
        
        # Available algorithms
        self.classification_algorithms = {
            'random_forest': RandomForestClassifier,
            'logistic_regression': LogisticRegression,
            'svm': SVC,
            'decision_tree': DecisionTreeClassifier,
            'gradient_boosting': GradientBoostingClassifier,
            'knn': KNeighborsClassifier,
            'naive_bayes': GaussianNB
        }
        
        self.regression_algorithms = {
            'random_forest': RandomForestRegressor,
            'linear_regression': LinearRegression,
            'ridge': Ridge,
            'lasso': Lasso,
            'svm': SVR,
            'decision_tree': DecisionTreeRegressor,
            'gradient_boosting': GradientBoostingRegressor,
            'knn': KNeighborsRegressor
        }
        
        # Default model parameters
        self.default_model_params = {
            'classification': {
                'random_forest': {'n_estimators': 100, 'random_state': 42},
                'logistic_regression': {'random_state': 42, 'max_iter': 1000},
                'svm': {'random_state': 42, 'probability': True},
                'decision_tree': {'random_state': 42},
                'gradient_boosting': {'random_state': 42},
                'knn': {'n_neighbors': 5},
                'naive_bayes': {}
            },
            'regression': {
                'random_forest': {'n_estimators': 100, 'random_state': 42},
                'linear_regression': {},
                'ridge': {'random_state': 42},
                'lasso': {'random_state': 42},
                'svm': {},
                'decision_tree': {'random_state': 42},
                'gradient_boosting': {'random_state': 42},
                'knn': {'n_neighbors': 5}
            }
        }

    def _load_and_analyze_data(self, data_path: str, target: str) -> Dict[str, Any]:
        """Load and analyze the dataset"""
        try:
            # Load data
            if data_path.endswith('.csv'):
                df = pd.read_csv(data_path)
            else:
                raise ValueError("Currently only CSV files are supported")
            
            print(f"Dataset loaded successfully!")
            print(f"Shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            
            # Check if target column exists
            if target not in df.columns:
                raise ValueError(f"Target column '{target}' not found in dataset")
            
            # Basic analysis
            analysis = {
                'shape': df.shape,
                'columns': list(df.columns),
                'target_column': target,
                'missing_values': df.isnull().sum().sum(),
                'duplicate_rows': df.duplicated().sum(),
                'target_unique_values': df[target].nunique(),
                'target_type': df[target].dtype,
                'is_classification': self._is_classification_task(df[target])
            }
            
            print(f"Missing values: {analysis['missing_values']}")
            print(f"Duplicate rows: {analysis['duplicate_rows']}")
            print(f"Target unique values: {analysis['target_unique_values']}")
            print(f"Detected task: {'Classification' if analysis['is_classification'] else 'Regression'}")
            
            return df, analysis
            
        except Exception as e:
            raise Exception(f"Error loading data: {str(e)}")

    def _is_classification_task(self, target_series: pd.Series) -> bool:
        """Determine if it's a classification or regression task"""
        unique_values = target_series.nunique()
        total_values = len(target_series)
        
        # If target is categorical or has very few unique values relative to total
        if target_series.dtype == 'object' or target_series.dtype == 'category':
            return True
        elif unique_values <= 20 or (unique_values / total_values) < 0.05:
            return True
        else:
            return False

    def _preprocess_data(self, df: pd.DataFrame, target: str) -> tuple:
        """Preprocess the data"""
        # Separate features and target
        X = df.drop(columns=[target])
        y = df[target]
        
        # Handle missing values for numeric and categorical columns separately
        numeric_columns = X.select_dtypes(include=[np.number]).columns
        categorical_columns = X.select_dtypes(include=['object', 'category']).columns
        
        # Fill missing values for numeric columns with mean
        if len(numeric_columns) > 0:
            X[numeric_columns] = X[numeric_columns].fillna(X[numeric_columns].mean())
        
        # Fill missing values for categorical columns with mode or 'Unknown'
        if len(categorical_columns) > 0:
            for col in categorical_columns:
                if X[col].isnull().all():
                    X[col] = X[col].fillna('Unknown')
                else:
                    mode_value = X[col].mode().iloc[0] if not X[col].mode().empty else 'Unknown'
                    X[col] = X[col].fillna(mode_value)
        
        # Handle categorical variables - encode them
        for col in categorical_columns:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
        
        # Handle categorical target for classification
        label_encoder_target = None
        if y.dtype == 'object' or y.dtype == 'category':
            label_encoder_target = LabelEncoder()
            y = label_encoder_target.fit_transform(y)
        
        print(f"Preprocessed features shape: {X.shape}")
        print(f"Features after preprocessing: {list(X.columns)}")
        
        return X, y, label_encoder_target

    def _get_best_algorithm(self, X: pd.DataFrame, y: pd.Series, task: str, cv: int) -> str:
        """Automatically select the best algorithm for the dataset"""
        print(f"\n🔍 Running AutoML - Testing algorithms for {task}...")
        
        algorithms = self.classification_algorithms if task == 'classification' else self.regression_algorithms
        results = {}
        
        for alg_name, alg_class in algorithms.items():
            try:
                # Get default parameters
                params = self.default_model_params[task][alg_name].copy()
                model = alg_class(**params)
                
                # Ensure we have enough samples for CV
                n_samples = len(X)
                actual_cv = min(cv, n_samples // 2) if n_samples < 100 else cv
                
                # Cross-validation
                if task == 'classification':
                    scores = cross_val_score(model, X, y, cv=actual_cv, scoring='accuracy')
                else:
                    scores = cross_val_score(model, X, y, cv=actual_cv, scoring='r2')
                
                results[alg_name] = {
                    'mean_score': scores.mean(),
                    'std_score': scores.std(),
                    'scores': scores
                }
                
                print(f"  {alg_name}: {scores.mean():.4f} (±{scores.std():.4f})")
                
            except Exception as e:
                print(f"  {alg_name}: Failed - {str(e)}")
                continue
        
        if not results:
            raise Exception("No algorithms could be trained successfully")
        
        # Select best algorithm
        best_algorithm = max(results.keys(), key=lambda x: results[x]['mean_score'])
        best_score = results[best_algorithm]['mean_score']
        
        print(f"\n🏆 Best Algorithm: {best_algorithm} (Score: {best_score:.4f})")
        return best_algorithm

    def _train_model(self, X_train, y_train, algorithm: str, task: str, 
                    user_hyperparams: Dict = None) -> Any:
        """Train the specified model"""
        algorithms = self.classification_algorithms if task == 'classification' else self.regression_algorithms
        
        if algorithm not in algorithms:
            available = list(algorithms.keys())
            raise ValueError(f"Algorithm '{algorithm}' not supported for {task}. Available: {available}")
        
        # Get model class and default parameters
        model_class = algorithms[algorithm]
        default_params = self.default_model_params[task][algorithm].copy()
        
        # Update with user-provided hyperparameters
        if user_hyperparams:
            # Remove non-model parameters
            model_params = {k: v for k, v in user_hyperparams.items() 
                          if k not in ['test_size', 'cv', 'random_state']}
            default_params.update(model_params)
        
        print(f"Training {algorithm} with parameters: {default_params}")
        
        # Create and train model
        model = model_class(**default_params)
        model.fit(X_train, y_train)
        
        return model

    def _evaluate_model(self, model, X_test, y_test, task: str) -> Dict:
        """Evaluate the trained model"""
        predictions = model.predict(X_test)
        
        if task == 'classification':
            accuracy = accuracy_score(y_test, predictions)
            results = {
                'accuracy': accuracy,
                'classification_report': classification_report(y_test, predictions)
            }
            print(f"\n📊 Model Evaluation:")
            print(f"Accuracy: {accuracy:.4f}")
        else:
            mse = mean_squared_error(y_test, predictions)
            r2 = r2_score(y_test, predictions)
            rmse = np.sqrt(mse)
            results = {
                'mse': mse,
                'rmse': rmse,
                'r2_score': r2
            }
            print(f"\n📊 Model Evaluation:")
            print(f"R² Score: {r2:.4f}")
            print(f"RMSE: {rmse:.4f}")
        
        return results

    def _save_model(self, model, save_path: str, scaler=None, label_encoder=None, 
                   feature_columns=None, model_info=None):
        """Save the trained model with metadata"""
        model_data = {
            'model': model,
            'scaler': scaler,
            'label_encoder': label_encoder,
            'feature_columns': feature_columns,
            'model_info': model_info
        }
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
        
        with open(save_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"\n💾 Model saved successfully to: {save_path}")

# Main training function
def ml_trainer(data: str, target: str, task: Optional[str] = None, 
               algorithm: Optional[str] = None, hyperparams: Optional[Dict] = None, 
               save_path: str = "best_model.pkl") -> Dict[str, Any]:
    """
    Train a machine learning model on the given dataset
    
    Args:
        data: Path to CSV file
        target: Target column name
        task: 'classification' or 'regression' (auto-detected if None)
        algorithm: Algorithm name (AutoML mode if None)
        hyperparams: Dictionary of hyperparameters
        save_path: Path to save the trained model
    
    Returns:
        Dictionary with training results and model info
    """
    
    trainer = MLAutoTrainer()
    
    try:
        # Load and analyze data
        df, analysis = trainer._load_and_analyze_data(data, target)
        
        # Determine task type
        if task is None:
            detected_task = 'classification' if analysis['is_classification'] else 'regression'
            print(f"\n🎯 Auto-detected task: {detected_task}")
            task = detected_task
        else:
            if task not in ['classification', 'regression']:
                raise ValueError("Task must be 'classification' or 'regression'")
            print(f"\n🎯 User-specified task: {task}")
        
        # Merge hyperparameters
        final_hyperparams = trainer.default_hyperparams[task].copy()
        if hyperparams:
            final_hyperparams.update(hyperparams)
        
        print(f"Using hyperparameters: {final_hyperparams}")
        
        # Preprocess data
        X, y, label_encoder = trainer._preprocess_data(df, target)
        
        # Split data
        test_size = final_hyperparams.get('test_size', 0.25)
        random_state = final_hyperparams.get('random_state', 42)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, 
            stratify=y if task == 'classification' else None
        )
        
        print(f"\n📊 Data split - Train: {X_train.shape[0]}, Test: {X_test.shape[0]}")
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Algorithm selection
        if algorithm is None:
            # AutoML mode
            selected_algorithm = trainer._get_best_algorithm(
                pd.DataFrame(X_train_scaled, columns=X.columns), 
                y_train, task, final_hyperparams.get('cv', 5)
            )
        else:
            # User-specified algorithm
            selected_algorithm = algorithm.lower().replace(' ', '_')
            print(f"\n🎯 User-specified algorithm: {selected_algorithm}")
        
        # Train model
        print(f"\n🚀 Training {selected_algorithm}...")
        model = trainer._train_model(X_train_scaled, y_train, selected_algorithm, task, final_hyperparams)
        
        # Evaluate model
        evaluation = trainer._evaluate_model(model, X_test_scaled, y_test, task)
        
        # Prepare model info
        model_info = {
            'algorithm': selected_algorithm,
            'task': task,
            'dataset_shape': df.shape,
            'target_column': target,
            'feature_columns': list(X.columns),
            'hyperparams': final_hyperparams,
            'evaluation': evaluation,
            'training_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Save model
        trainer._save_model(
            model=model,
            save_path=save_path,
            scaler=scaler,
            label_encoder=label_encoder,
            feature_columns=list(X.columns),
            model_info=model_info
        )
        
        result = {
            'algorithm': selected_algorithm,
            'task': task,
            'evaluation': evaluation,
            'model_path': save_path,
            'feature_columns': list(X.columns),
            'success': True
        }
        
        print(f"\n✅ Training completed successfully!")
        return result
        
    except Exception as e:
        print(f"\n❌ Error during training: {str(e)}")
        return {'success': False, 'error': str(e)}

def ml_predictor(model_path: str, values: List[List[float]]) -> Dict[str, Any]:
    """
    Make predictions using a saved model
    
    Args:
        model_path: Path to the saved model file
        values: List of feature vectors for prediction
    
    Returns:
        Dictionary with predictions and model info
    """
    
    try:
        # Check if model file exists
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        # Load model
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        model = model_data['model']
        scaler = model_data['scaler']
        label_encoder = model_data['label_encoder']
        feature_columns = model_data['feature_columns']
        model_info = model_data['model_info']
        
        print(f"📁 Loaded model: {model_info['algorithm']} ({model_info['task']})")
        print(f"Expected features ({len(feature_columns)}): {feature_columns}")
        
        # Validate input
        if not isinstance(values, list):
            raise ValueError("Values must be a list")
        
        if not values:
            raise ValueError("Values list cannot be empty")
            
        if not isinstance(values[0], list):
            raise ValueError("Values must be a list of lists (2D array)")
        
        if len(values[0]) != len(feature_columns):
            raise ValueError(f"Expected {len(feature_columns)} features, got {len(values[0])}. "
                           f"Features should be in order: {feature_columns}")
        
        # Convert to DataFrame
        X_pred = pd.DataFrame(values, columns=feature_columns)
        print(f"Input data shape: {X_pred.shape}")
        print(f"Input data:\n{X_pred}")
        
        # Scale features
        X_pred_scaled = scaler.transform(X_pred)
        
        # Make predictions
        predictions = model.predict(X_pred_scaled)
        
        # Get prediction probabilities for classification
        probabilities = None
        if model_info['task'] == 'classification' and hasattr(model, 'predict_proba'):
            try:
                probabilities = model.predict_proba(X_pred_scaled)
            except:
                probabilities = None
        
        # Convert predictions back to original labels if needed
        original_predictions = predictions.copy()
        if label_encoder is not None:
            try:
                predictions = label_encoder.inverse_transform(predictions.astype(int))
            except:
                predictions = original_predictions
        
        result = {
            'predictions': predictions.tolist() if hasattr(predictions, 'tolist') else predictions,
            'probabilities': probabilities.tolist() if probabilities is not None else None,
            'input_data': X_pred.to_dict('records'),
            'model_info': {
                'algorithm': model_info['algorithm'],
                'task': model_info['task'],
                'training_date': model_info['training_date'],
                'feature_columns': feature_columns
            },
            'success': True
        }
        
        print(f"🎯 Predictions: {predictions}")
        if probabilities is not None:
            print(f"📊 Prediction probabilities: {probabilities}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error during prediction: {str(e)}")
        return {'success': False, 'error': str(e), 'input_values': values}

# Example usage and testing
