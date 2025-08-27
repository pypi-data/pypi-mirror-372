"""
YAML generator for Spacelift plugins.
"""

import importlib.util
import os
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, Union

import yaml
from jinja2 import Environment, PackageLoader, select_autoescape
from mergedeep import Strategy, merge  # type: ignore

if TYPE_CHECKING:
    from .plugin import SpaceforgePlugin

from dataclasses import fields

from .cls import (
    Binary,
    Context,
    MountedFile,
    Parameter,
    PluginManifest,
    Policy,
    Variable,
    Webhook,
)
from .plugin import SpaceforgePlugin

static_binary_directory = "/mnt/workspace/plugins/plugin_binaries"


class PluginGenerator:
    """Generates plugin.yaml from a Python plugin class."""

    def __init__(
        self, plugin_path: str = "plugin.py", output_path: str = "plugin.yaml"
    ) -> None:
        """
        Initialize the generator.

        Args:
            plugin_path: Path to the plugin Python file
            output_path: Path where to write the generated YAML
        """
        self.plugin_path = plugin_path
        self.output_path = output_path
        self.plugin_class: Optional[Type[SpaceforgePlugin]] = None
        self.plugin_instance: Optional[SpaceforgePlugin] = None
        self.plugin_working_directory: Optional[str] = None
        self.config: Optional[Dict[str, Any]] = None
        self.jinja = Environment(
            loader=PackageLoader("spaceforge"), autoescape=select_autoescape()
        )

    def load_plugin(self) -> None:
        """Load the plugin class from the specified path."""
        if not os.path.exists(self.plugin_path):
            raise FileNotFoundError(f"Plugin file not found: {self.plugin_path}")

        # Load the module
        spec = importlib.util.spec_from_file_location("plugin_module", self.plugin_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load plugin from {self.plugin_path}")

        plugin_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin_module)

        # Find the plugin class (should inherit from SpaceforgePlugin)
        plugin_class = None
        for attr_name in dir(plugin_module):
            attr = getattr(plugin_module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, SpaceforgePlugin)
                and attr != SpaceforgePlugin
            ):
                plugin_class = attr
                break

        if plugin_class is None:
            raise ValueError("No SpaceforgePlugin subclass found in plugin file")

        self.plugin_class = plugin_class
        self.plugin_instance = plugin_class()
        self.plugin_working_directory = (
            "/mnt/workspace/plugins/"
            + plugin_class.__plugin_name__.lower().replace(" ", "_")
        )
        self.config = {
            "setup_virtual_env": (
                f"cd {self.plugin_working_directory} && python -m venv ./venv && "
                + "source venv/bin/activate && (command -v spaceforge &> /dev/null || pip install spaceforge)"
            ),
            "plugin_mounted_path": f"{self.plugin_working_directory}/{os.path.basename(self.plugin_path)}",
        }

    def get_plugin_metadata(self) -> Dict[str, Union[str, List[str]]]:
        """Extract metadata from the plugin class."""
        if self.plugin_class is None:
            raise ValueError("Plugin class not loaded. Call load_plugin() first.")

        doc = getattr(self.plugin_class, "__doc__", "")
        if doc:
            doc = doc.strip()

        metadata = {
            "name_prefix": getattr(
                self.plugin_class,
                "__plugin_name__",
                self.plugin_class.__name__.lower().replace("plugin", ""),
            ),
            "version": getattr(self.plugin_class, "__version__", "1.0.0"),
            "labels": getattr(self.plugin_class, "__labels__", []),
            "description": doc
            or f"A Spacelift plugin built with {self.plugin_class.__name__}",
            "author": getattr(self.plugin_class, "__author__", "Unknown"),
        }
        return metadata

    def get_plugin_parameters(self) -> Optional[List[Parameter]]:
        """Extract parameter definitions from the plugin class."""
        return getattr(self.plugin_class, "__parameters__", None)

    def get_available_hooks(self) -> List[str]:
        """Get list of hook methods implemented in the plugin."""
        hook_methods = []

        for method_name in dir(self.plugin_class):
            if method_name.startswith(
                ("after_", "before_")
            ) and not method_name.startswith("_"):
                method = getattr(self.plugin_class, method_name)
                base_method = getattr(SpaceforgePlugin, method_name, None)

                # Check if the method is overridden (different from base implementation)
                if (
                    callable(method)
                    and base_method
                    and method.__qualname__ != base_method.__qualname__
                ):
                    hook_methods.append(method_name)

        return hook_methods

    def _add_to_mounted_files(
        self,
        hooks: Dict[str, List[str]],
        mounted_files: List[MountedFile],
        phase: str,
        filepath: str,
        filecontent: str,
    ) -> None:
        file = f"{self.plugin_working_directory}/{filepath}"
        hooks[phase].append(f"chmod +x {file} && {file}")
        mounted_files.append(
            MountedFile(
                path=f"{self.plugin_working_directory}/{filepath}",
                content=filecontent,
                sensitive=False,
            )
        )

    def _update_with_requirements(self, mounted_files: List[MountedFile]) -> None:
        """Update the plugin hooks if there is a requirements.txt"""
        if os.path.exists("requirements.txt") and self.config is not None:
            # read the requirements.txt file
            with open("requirements.txt", "r") as f:
                mounted_files.append(
                    MountedFile(
                        path=f"{self.plugin_working_directory}/requirements.txt",
                        content=f.read(),
                        sensitive=False,
                    )
                )

    def _update_with_python_file(self, mounted_files: List[MountedFile]) -> None:
        """Ensure the plugin file itself is mounted."""
        if os.path.exists(self.plugin_path) and self.config is not None:
            with open(self.plugin_path, "r") as f:
                mounted_files.append(
                    MountedFile(
                        path=self.config["plugin_mounted_path"],
                        content=f.read(),
                        sensitive=False,
                    )
                )

    def _add_spaceforge_hooks(
        self,
        hooks: Dict[str, List[str]],
        mounted_files: List[MountedFile],
        has_binaries: bool,
    ) -> None:
        # Add the spaceforge hook to actually run the plugin
        if self.config is None:
            raise ValueError("Plugin config not set. Call load_plugin() first.")

        available_hooks = self.get_available_hooks()
        for hook in available_hooks:
            # Ensure the hook exists in the first context
            if hook not in hooks:
                hooks[hook] = []

            directory = os.path.dirname(self.config["plugin_mounted_path"])
            template = self.jinja.get_template("ensure_spaceforge_and_run.sh.j2")
            render = template.render(
                plugin_path=directory,
                plugin_file=self.config["plugin_mounted_path"],
                phase=hook,
                has_binaries=has_binaries,
            )
            self._add_to_mounted_files(hooks, mounted_files, hook, f"{hook}.sh", render)

    def _map_variables_to_parameters(self, contexts: List[Context]) -> None:
        for context in contexts:
            # Get the variables from the plugin and change the value_from_parameter to the ID of the parameter
            # based on its name.
            if context.env is None:
                continue

            for variable in context.env:
                if variable.value_from_parameter:
                    parameter_name = variable.value_from_parameter
                    parameters = self.get_plugin_parameters()
                    if parameters:
                        parameter = next(
                            (
                                p
                                for p in parameters
                                if p.name == parameter_name or p.id == parameter_name
                            ),
                            None,
                        )
                        if parameter:
                            variable.value_from_parameter = parameter.id
                        else:
                            raise ValueError(
                                f"Parameter {parameter_name} not found for variable {variable.key}"
                            )

    def get_plugin_contexts(self) -> List[Context]:
        """Get context definitions from the plugin class."""

        f"cd {self.plugin_working_directory}"
        hooks: Dict[str, List[str]] = {
            "before_init": [f"mkdir -p {self.plugin_working_directory}"]
        }
        mounted_files: List[MountedFile] = []

        self._update_with_requirements(mounted_files)
        self._update_with_python_file(mounted_files)
        has_binaries = self._generate_binary_install_command(hooks, mounted_files)
        self._add_spaceforge_hooks(hooks, mounted_files, has_binaries)

        # Get the contexts and append the hooks and mounted files to it.
        if self.plugin_class is None:
            raise ValueError("Plugin class not loaded. Call load_plugin() first.")

        contexts = getattr(
            self.plugin_class,
            "__contexts__",
            [
                Context(
                    name_prefix=self.plugin_class.__plugin_name__.lower(),
                    description=f"Main context for {self.plugin_class.__plugin_name__}",
                )
            ],
        )

        if contexts[0].hooks is None:
            contexts[0].hooks = {}
        if contexts[0].mounted_files is None:
            contexts[0].mounted_files = []
        if contexts[0].env is None:
            contexts[0].env = []

        # Add the hooks and mounted files to the first context
        merge(contexts[0].hooks, hooks, strategy=Strategy.TYPESAFE_ADDITIVE)
        contexts[0].mounted_files += mounted_files

        self._map_variables_to_parameters(contexts)

        return contexts

    def _generate_binary_install_command(
        self, hooks: Dict[str, List[str]], mounted_files: List[MountedFile]
    ) -> bool:
        binaries = self.get_plugin_binaries()
        if binaries is None:
            return False

        for i, binary in enumerate(binaries):
            amd64_url = binary.download_urls.get("amd64", None)
            arm64_url = binary.download_urls.get("arm64", None)
            binary_path = f"{static_binary_directory}/{binary.name}"
            if amd64_url is None and arm64_url is None:
                raise ValueError(
                    f"Binary {binary.name} must have at least one download URL defined (amd64 or arm64)"
                )

            template = self.jinja.get_template("binary_install.sh.j2")
            render = template.render(
                binary=binary,
                amd64_url=amd64_url,
                arm64_url=arm64_url,
                binary_path=binary_path,
                static_binary_directory=static_binary_directory,
            )
            self._add_to_mounted_files(
                hooks,
                mounted_files,
                "before_init",
                f"binary_install_{binary.name}.sh",
                render,
            )

        return True

    def get_plugin_binaries(self) -> Optional[List[Binary]]:
        """Get binary definitions from the plugin class."""
        return getattr(self.plugin_class, "__binaries__", None)

    def get_plugin_policies(self) -> Optional[List[Policy]]:
        """Get policy definitions from the plugin class."""
        return getattr(self.plugin_class, "__policies__", None)

    def get_plugin_webhooks(self) -> Optional[List[Webhook]]:
        """Get webhook definitions from the plugin class."""
        return getattr(self.plugin_class, "__webhooks__", None)

    def generate_manifest(self) -> PluginManifest:
        """Generate the complete plugin YAML structure."""
        if self.plugin_class is None:
            self.load_plugin()

        metadata = self.get_plugin_metadata()

        return PluginManifest(
            name=str(metadata.get("name_prefix", "unknown")),
            version=str(metadata.get("version", "1.0.0")),
            description=str(metadata.get("description", "")),
            author=str(metadata.get("author", "Unknown")),
            labels=list(metadata.get("labels", [])),
            parameters=self.get_plugin_parameters(),
            contexts=self.get_plugin_contexts(),
            webhooks=self.get_plugin_webhooks(),
            policies=self.get_plugin_policies(),
        )

    def write_yaml(self, manifest: PluginManifest) -> None:
        """Write the YAML data to file."""

        class CustomDumper(yaml.Dumper):
            def choose_scalar_style(self) -> str:
                """Override scalar style selection to prefer literal for multiline code."""
                style = super().choose_scalar_style()
                if (
                    hasattr(self, "event")
                    and self.event
                    and hasattr(self.event, "value")
                ):
                    if self.event.value.count("\n") > 0 and len(self.event.value) > 100:
                        return "|"
                return style if isinstance(style, str) else ""

            def represent_str(self, data: str) -> Any:
                """Override string representation for multiline strings."""
                if data.count("\n") > 0:
                    data = data.strip()
                    data = "\n".join([line.rstrip() for line in data.splitlines()])
                    return self.represent_scalar(
                        "tag:yaml.org,2002:str", data, style="|"
                    )
                return self.represent_scalar("tag:yaml.org,2002:str", data)

            def represent_dataclass(self, data: Any) -> Any:
                """Override dataclass representation to exclude None values."""
                filtered_dict = {
                    field.name: getattr(data, field.name)
                    for field in fields(data)
                    if getattr(data, field.name) is not None
                }
                return self.represent_dict(filtered_dict)

        # Register representers using the instance methods
        CustomDumper.add_representer(str, CustomDumper.represent_str)
        CustomDumper.add_representer(Context, CustomDumper.represent_dataclass)
        CustomDumper.add_representer(Parameter, CustomDumper.represent_dataclass)
        CustomDumper.add_representer(Variable, CustomDumper.represent_dataclass)
        CustomDumper.add_representer(Webhook, CustomDumper.represent_dataclass)
        CustomDumper.add_representer(Policy, CustomDumper.represent_dataclass)
        CustomDumper.add_representer(MountedFile, CustomDumper.represent_dataclass)
        CustomDumper.add_representer(PluginManifest, CustomDumper.represent_dataclass)

        with open(self.output_path, "w") as f:
            yaml.dump(
                manifest,
                f,
                Dumper=CustomDumper,
                default_flow_style=False,
                sort_keys=False,
                indent=2,
                width=float("inf"),
            )
        print(f"Generated plugin.yaml at: {self.output_path}")

    def generate(self) -> None:
        """Generate the plugin.yaml file."""
        self.write_yaml(self.generate_manifest())


import click


@click.command(name="generate")
@click.argument(
    "plugin_file",
    default="plugin.py",
    type=click.Path(exists=True, dir_okay=False, readable=True),
)
@click.option(
    "-o",
    "--output",
    default="plugin.yaml",
    type=click.Path(dir_okay=False, writable=True),
    help="Output YAML file path (default: plugin.yaml)",
)
def generate_command(plugin_file: str, output: str) -> None:
    """Generate plugin.yaml from Python plugin.

    PLUGIN_FILE: Path to the plugin Python file (default: plugin.py)
    """
    generator = PluginGenerator(plugin_file, output)
    generator.generate()
