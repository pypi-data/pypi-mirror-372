class NotAGitRepositoryError(Exception):
    """Raised when trying to update a repository that is not of type 'git'."""
