import sys

from ..base_rule import BaseRule
from ..config import RuleConfig


class Rule(BaseRule):
    """
    Implementation of a simple rule that can edit the first line of a file.
    """

    COMMAND = [sys.executable, "-m", __name__]

    def __init__(self, rule_config: RuleConfig) -> None:
        self.rule_config = rule_config

    def prepare(self):  # type: ignore[no-untyped-def] # FIX ME
        pass

    # def work_on_project(self, project_path):
    #     return SubprocessManager(
    #         command=self.COMMAND,
    #         env={
    #             "RULE_DIR": self.rule_config.dir,
    #             "RULE_NAME": self.rule_config.name,
    #             "RULE_CONFIG": encode(self.rule_config),
    #         },
    #         cwd=project_path,
    #     )


if __name__ == "__main__":
    pass
