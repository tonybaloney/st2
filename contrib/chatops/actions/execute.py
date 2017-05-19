import os

from st2common.runners.base_action import Action
from st2client.models.action_alias import ActionAliasMatch, ActionAliasExecution

from st2client.client import Client


class ExecuteActionAliasAction(Action):
    def __init__(self, config=None):
        super(ExecuteActionAliasAction, self).__init__(config=config)
        api_url = os.environ.get('ST2_ACTION_API_URL', None)
        token = os.environ.get('ST2_ACTION_AUTH_TOKEN', None)
        self.client = Client(api_url=api_url, token=token)

    def run(self, text, source_channel=None, user=None):
        alias_match = ActionAliasMatch()
        alias_match.command = text
        alias, representation = self.client.managers['ActionAlias'].match(
            alias_match)

        execution = ActionAliasExecution()
        execution.name = alias.name
        execution.format = representation
        execution.command = text
        execution.source_channel = source_channel  # ?
        execution.notification_channel = None
        execution.notification_route = None
        execution.user = user

        action_exec_mgr = self.app.client.managers['ActionAliasExecution']

        execution = action_exec_mgr.create(execution)
        return execution.execution['id']