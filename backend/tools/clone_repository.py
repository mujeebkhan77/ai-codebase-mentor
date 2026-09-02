import os
from git import Repo

def clone_repository(repo_url: str):
    """
    Clone a GitHub repository locally using a shallow clone.

    Use this tool when you need to:
    - download a repository before analyzing its code
    - create a local copy that other tools can inspect
    - access files, folders, and source code from a GitHub URL

    This tool performs a shallow clone to avoid downloading the complete
    repository history, making it faster for large repositories.

    Do not use this tool if the repository has already been cloned.

    Input:
    repo_url: The GitHub repository URL.

    Output:
    Returns the local path of the cloned repository.
    """

    repo_name = repo_url.rstrip("/").split("/")[-1]

    clone_path = os.path.join("repositories", repo_name)

    if os.path.exists(clone_path):
        return clone_path

    os.makedirs("repositories", exist_ok=True)

    Repo.clone_from(
        repo_url,
        clone_path,
        multi_options=["--depth", "1"]
    )

    return clone_path
