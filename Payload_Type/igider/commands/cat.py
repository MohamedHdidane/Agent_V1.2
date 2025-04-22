from mythic_container.MythicCommandBase import *

class CatArguments(TaskArguments):
    def __init__(self, command_line: str = None):
        super().__init__()
        self.args = []
        self.add_arg(
            "args",
            CommandParameter(
                name="args",
                type=ParameterType.String,
                description="File to read",
                default_value="",
                parameter_group_info=[ParameterGroupInfo(ui_position=1)]
            )
        )
        if command_line:
            self.load_args_from_string(command_line)

    async def parse_arguments(self):
        pass

class CatCommand(CommandBase):
    cmd = "cat"
    needs_admin = False
    help_cmd = "cat [file_path]"
    description = "Read a file"
    version = 1
    author = "@med"
    argument_class = CatArguments
    attributes = CommandAttributes(supported_os=[SupportedOS.Linux, SupportedOS.MacOS, SupportedOS.Windows])

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        return task

    async def process_response(self, response: AgentResponse):
        pass