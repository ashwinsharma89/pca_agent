"""
Data loading utilities
"""
import pandas as pd
import joblib
from pathlib import Path
from ..config import DATA_DIR, MODELS_DIR


def load_historical_data(file_path=None, use_sample=False):
    """
    Load historical campaign data
    
    Args:
        file_path: Path to CSV file
        use_sample: If True, load sample data
    
    Returns:
        pandas.DataFrame or None
    """
    try:
        if use_sample:
            sample_path = DATA_DIR / "historical_campaigns_sample.csv"
            if sample_path.exists():
                return pd.read_csv(sample_path)
            else:
                return None
        
        if file_path:
            if isinstance(file_path, str):
                return pd.read_csv(file_path)
            else:
                # Streamlit UploadedFile
                return pd.read_csv(file_path)
        
        return None
    
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return None


def load_model(model_path):
    """
    Load a saved model
    
    Args:
        model_path: Path to model file
    
    Returns:
        Loaded model or None
    """
    try:
        if isinstance(model_path, str):
            model_path = Path(model_path)
        
        if model_path.exists():
            return joblib.load(model_path)
        else:
            return None
    
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        return None


def save_model(model, model_path):
    """
    Save a model
    
    Args:
        model: Model object to save
        model_path: Path to save model
    
    Returns:
        bool: True if successful
    """
    try:
        if isinstance(model_path, str):
            model_path = Path(model_path)
        
        # Create directory if it doesn't exist
        model_path.parent.mkdir(parents=True, exist_ok=True)
        
        joblib.dump(model, model_path)
        return True
    
    except Exception as e:
        print(f"Error saving model: {str(e)}")
        return False


def load_csv_data(file_path):
    """
    Load CSV data with error handling
    
    Args:
        file_path: Path to CSV file or UploadedFile
    
    Returns:
        pandas.DataFrame or None
    """
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Error loading CSV: {str(e)}")
        return None


def save_csv_data(df, file_path):
    """
    Save DataFrame to CSV
    
    Args:
        df: pandas.DataFrame
        file_path: Path to save CSV
    
    Returns:
        bool: True if successful
    """
    try:
        if isinstance(file_path, str):
            file_path = Path(file_path)
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(file_path, index=False)
        return True
    
    except Exception as e:
        print(f"Error saving CSV: {str(e)}")
        return False


def validate_campaign_data(df):
    """
    Validate campaign data has required columns
    
    Args:
        df: pandas.DataFrame
    
    Returns:
        tuple: (is_valid, missing_columns)
    """
    required_columns = [
        'budget', 'duration', 'audience_size',
        'channels', 'creative_type', 'objective',
        'start_date', 'roas', 'cpa', 'conversions'
    ]
    
    missing = [col for col in required_columns if col not in df.columns]
    
    return len(missing) == 0, missing


def get_sample_data_path():
    """Get path to sample data"""
    return DATA_DIR / "historical_campaigns_sample.csv"


def sample_data_exists():
    """Check if sample data exists"""
    return get_sample_data_path().exists()
