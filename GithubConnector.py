from github import Github

# Authentication is defined via github.Auth
from github import Auth


class GithubConnector:
    def __init__(self, github_access_token):
        self.github_access_token = github_access_token
        self.repo = 'zhiduozhang/fastapi_demo_sxsw'

    def create_sweep_ticket(self, title: str, description: str, tags: list):
        # using an access token
        auth = Auth.Token(self.github_access_token)

        # Public Web Github
        g = Github(auth=auth)

        # Then play with your Github objects:
        repo = g.get_repo(self.repo)

        repo.create_issue(title="Sweep:" + title, body=description, labels=tags)

        # To close connections after use
        g.close()