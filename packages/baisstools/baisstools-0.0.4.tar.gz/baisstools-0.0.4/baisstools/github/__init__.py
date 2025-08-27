import os
import subprocess

def is_git_url(giturl: str) -> bool:
    """
        Check if a string is a valid git URL.
        :return: True if the string is a valid git URL, False otherwise.
        :rtype: bool
        :raises ValueError: If the string is not a valid git URL.
    """
    if not isinstance(giturl, str) or not giturl:
        return False
    for c in giturl:
        if c.isalnum() or c in "-_.@:/":
            continue
        return False
    return True

def clone_repository(url: str = "", owner: str = "", name: str = "", gh_token: str = "", dest_path: str = "", asname: str = "", provider: str = "github.com", branch: str = "main"):
    """
    Clone a git repository from a given URL or owner/name.
    :param url: The URL of the git repository to clone.
    :param owner: The owner of the git repository.
    :param name: The name of the git repository.
    :param gh_token: The GitHub token for authentication.
    :param dest_path: The destination path where the repository will be cloned.
    :param asname: The name to use for the cloned repository.
    :param provider: The git provider (default is "github.com").
    :param branch: The branch to clone (default is "main").
    :raises ValueError: If the URL is not a valid git URL.
    """
    if not url or not isinstance(url, str):
        url = ""
    if not provider or not isinstance(provider, str):
        provider = ""
    if not gh_token or not isinstance(gh_token, str):
        gh_token = ""
    url      = url.strip()
    gh_token = gh_token.strip()

    if not url:
        if gh_token:
            url = f"https://{gh_token}@{provider}/{owner}/{name}.git"
        else:
            url = f"git@{provider}:{owner}/{name}.git"

    if not url.startswith("https://") and not url.startswith("git@"):
        prefix = url.split(":")[0].split("/")[0]
        if url[len(prefix)] == ":":
            url = "git@" + url
        else:
            url = "https://" + url

    if gh_token:
        prefix   = url.strip(":").split(":")[0]
        if ("://" in url[:10]):
            prefix = url[url.index("://") + 3:].strip("/").split("/")[0]
        suffix   = url[url.index(prefix) + len(prefix):].strip("/:")
        if not provider:
            provider = prefix.split("@")[-1]
        url = f"https://{gh_token}@{provider}/{suffix}"

    if not is_git_url(url):
        raise ValueError(f"Invalid git URL: {url}")

    if not asname:
        asname = url.split("/")[-1]
        if asname.endswith(".git"):
            asname = asname[:-len(".git")]
    if not dest_path:
        dest_path = os.getcwd()
    cmd = ["git", "clone", "--branch", branch, url, asname]
    subprocess.run(cmd, shell=True, check=True, cwd = dest_path, capture_output = True, text = True)
