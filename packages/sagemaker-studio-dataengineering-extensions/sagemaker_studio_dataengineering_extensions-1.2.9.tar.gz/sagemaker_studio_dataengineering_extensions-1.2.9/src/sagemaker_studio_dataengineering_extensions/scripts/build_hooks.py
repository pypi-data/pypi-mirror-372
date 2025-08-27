import os
import subprocess
import time

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        super().initialize(version, build_data)

        if os.environ.get("AMZN_BUILD"):
            print("using peru hatch to build")

        # Get the project directory
        project_dir = os.path.dirname(os.path.abspath(__file__))
        print(f'custom build script triggered, dir is {project_dir}')

        # test the run_commands function
        # uncomment this and run bb when make changes in run_commands function
        # self.test_run_commands()

        self.prepare_env()

        self.build_spark_monitoring_widget()
        self.build_data_explorer()
        self.build_connection_magic_jlextension()
        self.build_ui_doc_manager()
        self.build_studio_ui_theme()
        self.build_post_startup_notification_plugin()
        self.build_sagemaker_studio_jupyter_scheduler()

    def run_commands(self, *commands, fail_fast=True):
        """
        Run one or more terminal commands and return their output.

        Args:
        *commands: Variable number of command strings to execute.

        Returns:
        A list of tuples, each containing the command, return code, stdout, and stderr.
        """
        results = []

        for cmd in commands:
            try:
                # Run the command and capture output
                process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout, stderr = process.communicate()

                # Get the return code
                return_code = process.returncode


                if fail_fast and return_code != 0:
                # If fail_fast is True and an exception occurred, stop execution
                    raise BuildException(f'command {cmd} failed with return_code {return_code}\n stdout is {stdout}\n stderr is {stderr}')
                # Append results
                results.append((cmd, return_code, stdout.strip(), stderr.strip()))

            except BuildException as e:
                raise e
            except Exception as e:
                # If there's an error running the command, capture it
                results.append((cmd, -1, "", str(e)))

        return results

    def test_run_commands(self):
        commands = [
            "echo Hello, World!",
            "ls -l",
            "invalid_command",  # This will cause an error
            "pwd"
        ]
        output = self.run_commands(*commands)
        for cmd, return_code, out, error in output:
            print(f'cmd {cmd} with return_code {return_code}, out is {out}, error is {error}')

    def prepare_env(self):
        commands = [
            #configure npm
            "peru-npm configure-npm",
        ]

        if os.environ.get("AMZN_BUILD"):
            print("running prepare_env commands")
            output = self.run_commands(*commands)
        else:
            print("skipping prepare_env commands")


    def build_spark_monitoring_widget(self):
        print("running build_spark_monitoring_widget commands")
        dir = "src/sagemaker_studio_dataengineering_extensions/sagemaker_spark_monitor_widget"

        build_commands = [
            f"cd {dir} && jlpm install --no-immutable && jlpm build:lib && jlpm build:lib:prod && jlpm run build:labextension && rm -r .yarn lib node_modules"
        ]

        conda_commands = [
            f"cd {dir} && rm -rf .npmrc .yarnrc.yml && npm install"
        ]

        conda_commands.extend(build_commands)

        # command for brazil-build
        commands = [
            # copy npm config generated from peru-npm to current dir
            f"cp .npmrc {dir}/ ",
            # configure npm server jlpm(yarn) is using to point to internal amazon registry
            f"cd {dir} && jlpm config set npmRegistryServer $(run-npm config get registry)",
            # configure http whitelist of jlpm(yarn) as it's http registry and was refused in jlpm(yarn) by default
            f"cd {dir} && jlpm config set unsafeHttpWhitelist $(echo $(run-npm config get registry) | sed -E 's#^(https?://)?([^/:]+)(:[0-9]+)?.*#\\2#')",
        ]
        commands.extend(build_commands)

        if not os.environ.get("AMZN_BUILD"):
            print("running normal build")
            output = self.run_commands(*conda_commands)
        else:
            print("running amazon build")
            output = self.run_commands(*commands)

        # debugging info
        # for cmd, return_code, out, error in output:
        #     print(f'building spark_monitoring_widget --- cmd "{cmd}" with return_code {return_code}, out is {out}, error is {error}')

    def build_data_explorer(self):
        print("running build_data_explorer commands")
        dir = "src/sagemaker_studio_dataengineering_extensions/sagemaker_data_explorer"
        commands = [
            #configure npm
            "peru-npm configure-npm",
            # configure npm server jlpm(yarn) is using to point to internal amazon registry
            f"cd {dir} && jlpm config set npmRegistryServer $(run-npm config get registry)",
            # configure http whitelist of jlpm(yarn) as it's http registry and was refused in jlpm(yarn) by default
            f"cd {dir} && jlpm config set unsafeHttpWhitelist $(echo $(run-npm config get registry) | sed -E 's#^(https?://)?([^/:]+)(:[0-9]+)?.*#\\2#')",
            # command to build spark monitor
            f"cd {dir} && jlpm install --no-immutable && jlpm build:prod && rm -r .yarn lib node_modules"
        ]

        conda_commands = [
            f"cd {dir} && rm -rf .npmrc .yarnrc.yml && npm install && jlpm install --no-immutable && jlpm build:prod && rm -r .yarn lib node_modules"
        ]

        if not os.environ.get("AMZN_BUILD"):
            print("running normal build")
            output = self.run_commands(*conda_commands)
        else:
            print("running amazon build")
            output = self.run_commands(*commands)

    def build_connection_magic_jlextension(self):
        print("running build_connection_magic_jlextension commands")
        dir = "src/sagemaker_studio_dataengineering_extensions/sagemaker_connection_magics_jlextension"

        build_commands = [
            # command to build
            f"cd {dir} && npm install && npm run clean && npm run build:lib:prod && npm run build:labextension",
            # command to clean up
            f"cd {dir} && rm -rf build lib node_modules dist",
        ]

        conda_commands = [
            f"cd {dir} && rm -rf .npmrc"
        ]

        conda_commands.extend(build_commands)

        # command for brazil-build
        commands = [
            # copy npm config generated from peru-npm to current dir
            f"cp .npmrc {dir}/ ",
        ]

        commands.extend(build_commands)

        if not os.environ.get("AMZN_BUILD"):
            print("running normal build")
            output = self.run_commands(*conda_commands)
        else:
            print("running amazon build")
            output = self.run_commands(*commands)

    def build_ui_doc_manager(self):
        print("running sagemaker_ui_doc_manager_jl_plugin commands")
        dir = "src/sagemaker_studio_dataengineering_extensions/sagemaker_ui_doc_manager_jl_plugin"

        build_commands = [
            # command to build
            f"cd {dir} && npm install && npm run build:prod",

            # command to clean up
            f"cd {dir} && rm -rf build lib node_modules",
        ]

        conda_commands = [
            f"cd {dir} && rm -rf .npmrc"
        ]

        conda_commands.extend(build_commands)

        # command for brazil-build
        commands = [
            # copy npm config generated from peru-npm to current dir
            f"cp .npmrc {dir}/ ",
        ]

        commands.extend(build_commands)

        if not os.environ.get("AMZN_BUILD"):
            print("running normal build")
            output = self.run_commands(*conda_commands)
        else:
            print("running amazon build")
            output = self.run_commands(*commands)

    def build_studio_ui_theme(self):
        print("running sagemaker_studio_theme build")
        dir = "src/sagemaker_studio_dataengineering_extensions/sagemaker_studio_theme"

        build_commands = [
            # command to build
            f"cd {dir} && npm install && npm run build:prod",

            # command to clean up
            f"cd {dir} && rm -rf build lib node_modules",
        ]

        conda_commands = [
            f"cd {dir} && rm -rf .npmrc"
        ]

        conda_commands.extend(build_commands)

        # command for brazil-build
        commands = [
            # copy npm config generated from peru-npm to current dir
            f"cp .npmrc {dir}/ ",
        ]

        commands.extend(build_commands)

        if not os.environ.get("AMZN_BUILD"):
            print("running normal build")
            output = self.run_commands(*conda_commands)
        else:
            print("running amazon build")
            output = self.run_commands(*commands)

    def build_post_startup_notification_plugin(self):
        print("running sagemaker_post_startup_notification_plugin build")
        dir = "src/sagemaker_studio_dataengineering_extensions/sagemaker_post_startup_notification_plugin"

        build_commands = [
            # command to build
            f"cd {dir} && npm install && npm run clean && npm run build:prod && npm run build:labextension",

            # command to clean up
            f"cd {dir} && rm -rf build lib node_modules",
        ]

        conda_commands = [
            f"cd {dir} && rm -rf .npmrc"
        ]

        conda_commands.extend(build_commands)

        # command for brazil-build
        commands = [
            # copy npm config generated from peru-npm to current dir
            f"cp .npmrc {dir}/ ",
            # set local NPM registry to amzn registry
            f"cd {dir} && jlpm config set npmRegistryServer $(run-npm config get registry)",
            # configure http whitelist of jlpm(yarn) as it's http registry and was refused in jlpm(yarn) by default
            f"cd {dir} && jlpm config set unsafeHttpWhitelist $(echo $(run-npm config get registry) | sed -E 's#^(https?://)?([^/:]+)(:[0-9]+)?.*#\\2#')",
        ]

        commands.extend(build_commands)

        if not os.environ.get("AMZN_BUILD"):
            print("running normal build")
            output = self.run_commands(*conda_commands)
        else:
            output = self.run_commands(*commands)
    
    def build_sagemaker_studio_jupyter_scheduler(self):
        print("running sagemaker_studio_jupyter_scheduler build")
        dir = "src/sagemaker_studio_dataengineering_extensions/sagemaker_studio_jupyter_scheduler"
  
        build_commands = [
            # command to build
            f"cd {dir} && npm run clean && npm install && npm run release",

            # command to clean up
            f"cd {dir} && rm -rf build lib node_modules",
        ]

        conda_commands = [
            f"cd {dir} && rm -rf .npmrc"
        ]

        conda_commands.extend(build_commands)

        # command for brazil-build
        commands = [
            # copy npm config generated from peru-npm to current dir
            f"cp .npmrc {dir}/ ",
        ]

        commands.extend(build_commands)

        if not os.environ.get("AMZN_BUILD"):
            print("running normal build")
            output = self.run_commands(*conda_commands)
        else:
            print("running amazon build")
            output = self.run_commands(*commands)

    def finalize(self, version, build_data, artifact_directory):
        if not os.environ.get("AMZN_BUILD"):
            print("Not amazon build, skipping custom build finalize")
            return  # exit immediately if we are not building amazon artifacts

        print("building in amazon build system, executing a second time build to package external artifacts")
        skip_finally = False

        try:
            subprocess.run([
                "mv", "pyproject.toml", "pyproject.toml.backup"
            ], check=True)
            
            subprocess.run([
                "mv", "amzn.pyproject.toml", "pyproject.toml"
            ], check=True)

            subprocess.run([
                ".venv/bin/python3", "-m", "pip", "install", "hatch"
            ], check=True)

            time.sleep(7)

            subprocess.run([
                ".venv/bin/python3", "-m", "hatch", "build"
            ], check=True)

            # Restore the original pyproject.toml configuration

            subprocess.run([
                "mv", "pyproject.toml", "amzn.pyproject.toml"
            ], check=True)
            
            subprocess.run([
                "mv", "pyproject.toml.backup", "pyproject.toml"
            ], check=True) 

            skip_finally = True

        finally:
            # Restore the original pyproject.toml configuration

            if not skip_finally:
                subprocess.run([
                    "mv", "pyproject.toml", "amzn.pyproject.toml"
                ], check=True)

                time.sleep(3)

                subprocess.run([
                    "mv", "pyproject.toml.backup", "pyproject.toml"
                ], check=True)

class BuildException(Exception):
    pass
