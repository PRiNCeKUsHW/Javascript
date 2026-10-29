class StudyError(Exception):
    """Base class for every error the assistant reports to the user."""


class BudgetExceeded(StudyError):
    """Spending would go past the configured budget."""
