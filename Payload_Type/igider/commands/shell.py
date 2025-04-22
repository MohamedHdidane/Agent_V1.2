from mythic_container.MythicCommandBase import *


class ShellArguments(TaskArguments):
    def __init__(self, command_line: str = None):
        super().__init__()
        self.args = []
        self.add_arg(
            "args",
            CommandParameter(
                name="args",
                type=ParameterType.String,
                description="Shell command to run",
                default_value="",
                parameter_group_info=[ParameterGroupInfo(ui_position=1)]
            )
        )
        if command_line:
            self.load_args_from_string(command_line)

    async def parse_arguments(self):
        pass


class ShellCommand(CommandBase):
    cmd = "shell"
    needs_admin = False
    help_cmd = "shell [args]"
    description = "Run a shell command"
    version = 1
    author = "@med"
    argument_class = ShellArguments
    attributes = CommandAttributes(supported_os=[SupportedOS.Linux, SupportedOS.MacOS, SupportedOS.Windows])

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        return task

    async def process_response(self, response: AgentResponse):
        pass