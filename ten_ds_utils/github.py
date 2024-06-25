import logging
from typing import List, Optional, Union
from github import GithubIntegration, Github, GithubObject, Repository, Issue
from github.GithubException import BadCredentialsException
from enum import Enum
from ten_ds_utils.utils.types import ensure_value_is_list
from ten_ds_utils.aws.secret_manager import SecretManager
from ten_ds_utils.aws.system_manager import SystemManager


OWNER = "PMO-Data-Science"
APP_ID_PARAMETER_NAME = "bug-reporter-bot-id"
APP_KEY_SECRET_NAME = "bug-reporter-bot-secret"


class Label(Enum):
    BUG = "Technical Issue"
    ENHANCEMENT = "Enhancement"
    FEEDBACK = "Feedback"
    QUESTION = "Question"


def validate_authentication(func):
    def wrapper(api, *args, **kwargs):
        if not api.is_authenticated():
            api.github = api.authenticate_app_with_github()
        return func(api, *args, **kwargs)

    return wrapper


class GithubAppAPI:
    """
    A class for using the github api via a github app
    """

    def __init__(self, owner: str, repo: str, key: str, id: int) -> None:
        """
        :param owner: string - The owner of the repo - often the organisation
        :param repo: string - The repo with which to authenticate.
        The github app must be installed here
        :param key: string - The private key of the github app
        :param id: int - The id of the github app
        """
        self.id = id
        self.owner = owner
        self.key = key
        self.repo = repo
        self.github = self.authenticate_app_with_github()

    def _get_github_integration(self, id: str, key: str) -> GithubIntegration:
        return GithubIntegration(id, key.encode())

    def authenticate_app_with_github(self) -> Github:
        integration = self._get_github_integration(self.id, self.key)
        installation = integration.get_installation(self.owner, self.repo)
        token = integration.get_access_token(installation.id)

        return Github(token.token)

    def is_authenticated(self) -> bool:
        try:
            res = self.github.get_repo(f"{self.owner}/{self.repo}")
            if isinstance(res, Repository.Repository):
                return True
            else:
                return False
        except BadCredentialsException:
            return False

    @validate_authentication
    def _get_repo(self, repo: str) -> Repository.Repository:
        return self.github.get_repo(f"{self.owner}/{repo}")

    def create_issue(
        self,
        repo: str,
        title: str,
        text: str,
        labels: Optional[Union[List[Label], Label]] = GithubObject.NotSet,
    ) -> Issue:
        repository = self._get_repo(repo)
        logging.info("Creating issue")
        logging.info(f"Issue: Title = {title}")
        logging.info(f"Issue: Body = {text}")
        logging.info(f"Issue: Labels = {labels}")
        return repository.create_issue(
            title, body=text, labels=ensure_value_is_list(labels)
        )
