"""
Input Validation Utilities

Provides validation functions for stock agent inputs to prevent crashes
and ensure data quality.
"""

from typing import List, Dict, Any, Optional
import re
from .logging_config import get_logger

logger = get_logger('agent.validators')


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class InputValidator:
    """Validates inputs for stock agent operations"""

    @staticmethod
    def validate_ticker(ticker: str) -> str:
        """
        Validate stock ticker format.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Uppercase ticker string

        Raises:
            ValidationError: If ticker format is invalid
        """
        if not ticker:
            raise ValidationError("Ticker cannot be empty")

        if not isinstance(ticker, str):
            raise ValidationError(f"Ticker must be a string, got {type(ticker)}")

        # Convert to uppercase
        ticker = ticker.upper().strip()

        # Check length (most tickers are 1-5 characters)
        if len(ticker) < 1 or len(ticker) > 5:
            raise ValidationError(f"Ticker '{ticker}' length must be between 1-5 characters")

        # Check format (alphanumeric only)
        if not re.match(r'^[A-Z0-9]+$', ticker):
            raise ValidationError(f"Ticker '{ticker}' must contain only letters and numbers")

        return ticker

    @staticmethod
    def validate_tickers(tickers: List[str]) -> List[str]:
        """
        Validate a list of stock tickers.

        Args:
            tickers: List of ticker symbols

        Returns:
            List of validated uppercase tickers

        Raises:
            ValidationError: If tickers list is invalid
        """
        if tickers is None:
            raise ValidationError("Tickers list cannot be None")

        if not isinstance(tickers, list):
            raise ValidationError(f"Tickers must be a list, got {type(tickers)}")

        if len(tickers) == 0:
            raise ValidationError("Tickers list cannot be empty")

        validated_tickers = []
        for ticker in tickers:
            try:
                validated_ticker = InputValidator.validate_ticker(ticker)
                validated_tickers.append(validated_ticker)
            except ValidationError as e:
                logger.warning(f"Skipping invalid ticker: {e}")
                continue

        if len(validated_tickers) == 0:
            raise ValidationError("No valid tickers found in input list")

        return validated_tickers

    @staticmethod
    def validate_lookback_days(days: int) -> int:
        """
        Validate lookback period for historical data.

        Args:
            days: Number of days to look back

        Returns:
            Validated days value

        Raises:
            ValidationError: If days value is invalid
        """
        if not isinstance(days, int):
            try:
                days = int(days)
            except (ValueError, TypeError):
                raise ValidationError(f"Lookback days must be an integer, got {type(days)}")

        if days < 1:
            raise ValidationError(f"Lookback days must be at least 1, got {days}")

        if days > 365:
            raise ValidationError(f"Lookback days cannot exceed 365, got {days}")

        return days

    @staticmethod
    def validate_news_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate news data structure.

        Args:
            data: List of news item dictionaries

        Returns:
            Validated news data

        Raises:
            ValidationError: If news data structure is invalid
        """
        if data is None:
            raise ValidationError("News data cannot be None")

        if not isinstance(data, list):
            raise ValidationError(f"News data must be a list, got {type(data)}")

        if len(data) == 0:
            raise ValidationError("News data list cannot be empty")

        # Validate each news item has required fields
        required_fields = ['Ticker', 'Title']
        validated_data = []

        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                logger.warning(f"Skipping non-dict item at index {idx}")
                continue

            # Check for required fields
            missing_fields = [field for field in required_fields if field not in item]
            if missing_fields:
                logger.warning(f"Item at index {idx} missing required fields: {missing_fields}")
                continue

            validated_data.append(item)

        if len(validated_data) == 0:
            raise ValidationError("No valid news items found in input data")

        return validated_data

    @staticmethod
    def validate_sentiment_analysis(sentiment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate sentiment analysis data structure.

        Args:
            sentiment_data: Dictionary of ticker -> sentiment info

        Returns:
            Validated sentiment data

        Raises:
            ValidationError: If sentiment data structure is invalid
        """
        if sentiment_data is None:
            raise ValidationError("Sentiment data cannot be None")

        if not isinstance(sentiment_data, dict):
            raise ValidationError(f"Sentiment data must be a dict, got {type(sentiment_data)}")

        if len(sentiment_data) == 0:
            raise ValidationError("Sentiment data cannot be empty")

        # Validate each ticker's sentiment data
        for ticker, data in sentiment_data.items():
            if not isinstance(data, dict):
                raise ValidationError(f"Sentiment data for {ticker} must be a dict")

            # Check for required fields
            if 'sentiment_score' not in data:
                raise ValidationError(f"Sentiment data for {ticker} missing 'sentiment_score'")

            if 'news_count' not in data:
                raise ValidationError(f"Sentiment data for {ticker} missing 'news_count'")

        return sentiment_data

    @staticmethod
    def validate_limit(limit: int, min_val: int = 1, max_val: int = 100) -> int:
        """
        Validate a limit/count parameter.

        Args:
            limit: Limit value to validate
            min_val: Minimum allowed value (default: 1)
            max_val: Maximum allowed value (default: 100)

        Returns:
            Validated limit value

        Raises:
            ValidationError: If limit is invalid
        """
        if not isinstance(limit, int):
            try:
                limit = int(limit)
            except (ValueError, TypeError):
                raise ValidationError(f"Limit must be an integer, got {type(limit)}")

        if limit < min_val:
            raise ValidationError(f"Limit must be at least {min_val}, got {limit}")

        if limit > max_val:
            raise ValidationError(f"Limit cannot exceed {max_val}, got {limit}")

        return limit


def safe_validate(validator_func, value, default_value=None, log_error=True):
    """
    Safely apply a validator function with error handling.

    Args:
        validator_func: Validation function to apply
        value: Value to validate
        default_value: Value to return if validation fails (optional)
        log_error: Whether to log validation errors (default: True)

    Returns:
        Validated value or default_value if validation fails
    """
    try:
        return validator_func(value)
    except ValidationError as e:
        if log_error:
            logger.error(f"Validation failed: {e}")
        if default_value is not None:
            return default_value
        raise
