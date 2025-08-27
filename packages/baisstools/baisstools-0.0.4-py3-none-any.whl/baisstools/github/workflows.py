"""
    - To learn more about GitHub Actions workflows, see:
        https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions
    - Example: Multiple jobs with their own timeouts

        on:
        workflow_dispatch:
            inputs:
            timeout:
                description: "Job timeout in minutes"
                required: false
                default: "15"

        jobs:
            myjob:
                runs-on: ubuntu-latest
                timeout-minutes: ${{ fromJSON(inputs.timeout) }}
                steps:
                - run: echo "Running with timeout: ${{ inputs.timeout }} minutes"

"""
import requests

def workflow_dispatch(workflow_name: str, owner: str, repo: str, gh_token: str, branch = "main", inputs = None, workflow_timeout: int = -1) -> dict:
    """
    Dispatch a GitHub Actions workflow with optional inputs and timeout.
    :param workflow_name: Name of the workflow to dispatch.
    :param owner: Owner of the repository.
    :param repo: Name of the repository.
    :param gh_token: GitHub token for authentication.
    :param branch: Branch to run the workflow on (default is "main").
    :param inputs: Optional dictionary of inputs to pass to the workflow.
    :param workflow_timeout: Timeout for the workflow in minutes (default is -1, meaning no timeout).
    :return: A dictionary with the status of the request.
    """
    if not inputs:
        inputs = {}
    if workflow_timeout > 0:
        inputs["timeout"] = str(workflow_timeout)
    try:
        url = f'https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_name}/dispatches'
        headers = {
            'Authorization': f'token {gh_token}',
            'Accept'       : 'application/vnd.github+json',
            'Content-Type' : 'application/json'
        }
        data = {
            'ref': branch
        }
        if inputs:
            data["inputs"] = inputs
        response = requests.post(url, headers = headers, json = data)
        return {"status": response.status_code}
    except:
        pass
    return {"status": 500}
