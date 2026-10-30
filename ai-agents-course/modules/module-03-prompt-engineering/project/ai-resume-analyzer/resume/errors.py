class AnalyzerError(Exception):
    """Base class for every error the analyzer reports to the user."""


class BudgetExceeded(AnalyzerError):
    """Spending would go past the configured budget."""
