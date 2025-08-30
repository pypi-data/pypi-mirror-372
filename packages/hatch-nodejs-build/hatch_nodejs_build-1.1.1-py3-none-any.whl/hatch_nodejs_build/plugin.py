import glob
import json
import platform
import shutil
import sys
from pathlib import Path
from subprocess import run

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

from hatch_nodejs_build._util import node_matches, get_node_executable_version
from hatch_nodejs_build.cache import NodeCache
from hatch_nodejs_build.config import NodeJsBuildConfiguration


class NodeJsBuildHook(BuildHookInterface):
    PLUGIN_NAME = "nodejs-build"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plugin_config: NodeJsBuildConfiguration = None
        self.node_executable: str = None
        self.node_cache = NodeCache()

    def initialize(self, version, build_data):
        self.prepare_plugin_config()
        self.app.display_mini_header("hatch-nodejs-build")
        self.app.display_info(
            f"Configuration:\n{self.plugin_config.model_dump_json(indent=2)}"
        )

        if self.plugin_config.require_node:
            self.require_node()

        self.run_install_command()
        self.run_build_command()

        artifact_dir = (
            (self.plugin_config.source_dir / self.plugin_config.artifact_dir)
            .absolute()
            .resolve()
        )
        artifact_list = glob.glob(str(artifact_dir / "**"), recursive=True)

        if not artifact_list:
            raise RuntimeError(
                f"[hatch-nodejs-build] no artifacts found in '{artifact_dir}'"
            )

        self.app.display_info(
            f"Copying {len(artifact_list)} artifacts from '{artifact_dir}'..."
        )
        self.app.display_debug(f"Artifacts:")
        for artifact in artifact_list:
            self.app.display_debug(f"- {artifact}")

        project_name = self.build_config.builder.metadata.core.name.replace("-", "_")
        bundled_dir = (
            (Path(self.root) / project_name / self.plugin_config.bundle_dir)
            .absolute()
            .resolve()
        )
        self.app.display_info(
            f"Copying artifacts from '{artifact_dir}'\n to '{bundled_dir}'..."
        )

        shutil.copytree(artifact_dir, bundled_dir, dirs_exist_ok=True)
        build_data["artifacts"].append(bundled_dir)

        if self.plugin_config.inline_bundle:
            self.app.display_waiting("Inlining bundle...")
            index_template = self.plugin_config.source_dir / "index.html"
            if not index_template.exists():
                raise RuntimeError(
                    f"[hatch-nodejs-build] Index template '{index_template}' does not exist"
                )
            index_content = index_template.read_text()
            js_bundle = bundled_dir / "bundle.js"
            if js_bundle.exists():
                index_content = index_content.replace(
                    "<script data-bundle-js></script>",
                    f"<script>{js_bundle.read_text()}</script>",
                )
                js_bundle.unlink()
            else:
                raise RuntimeError(
                    f"Inlining failed. Bundle file '{js_bundle}' not found"
                )

            css_bundle = bundled_dir / "bundle.css"
            if css_bundle.exists():
                index_content = index_content.replace(
                    "<style data-bundle-css></style>",
                    f"<style>{css_bundle.read_text()}</style>",
                )
                css_bundle.unlink()

            bundle_index = bundled_dir / "index.html"
            bundle_index.write_text(index_content)
            self.app.display_info(f"Inlined bundle index written to '{bundle_index}'")

        self.app.display_success("hatch-nodejs-build finished successfully")

    def prepare_plugin_config(self):
        self.plugin_config = NodeJsBuildConfiguration(**self.config)

    def require_node(self):
        package = self.get_package_json()
        required_engine = package.get("engines", {}).get("node")
        node_description = "Node.js" + (
            f" matching '{required_engine}'" if required_engine else ""
        )
        self.app.display_info(f"Looking for {node_description}...")

        # Find Node.js from the configured executable, or on PATH
        node_version = get_node_executable_version(
            self.plugin_config.node_executable or "node2"
        )

        # Check if it matches the possible requirement in package.json
        if node_version is not None and node_matches(node_version, required_engine):
            # If no node_executable given, `node` is on PATH, hopefully also `npm`
            if not self.plugin_config.node_executable:
                self.node_executable = shutil.which("node")
            else:
                self.node_executable = self.plugin_config.node_executable

            self.app.display_info(
                f"Found Node.js {node_version}: '{self.node_executable}'"
            )
            return

        # Node.js not found, check in cache
        if self.node_cache.has(required_engine):
            self.node_executable = self.node_cache.get(required_engine)
            node_version = get_node_executable_version(self.node_executable)
            if node_version is None:
                raise RuntimeError(f"Cached node '{self.node_executable}' not runnable")

            self.app.display_info(
                f"Found cached Node.js {node_version}: '{self.node_executable}'"
            )
            return

        self.app.display_warning(node_description + " not found.")
        # Node.js not cached either, install it in cache
        self.node_executable = self.node_cache.install(
            required_engine, self.plugin_config.lts, self.app
        )
        node_version = get_node_executable_version(self.node_executable)
        if node_version is None:
            raise RuntimeError(
                node_description
                + f" installation failed: '{self.node_executable}' not runnable"
            )
        self.app.display_warning(node_description + " not found.")
        self.app.display_info(
            f"Using installed Node.js {node_version}: '{self.node_executable}'"
        )

    def get_package_json(self):
        package_json_path = Path(self.plugin_config.source_dir) / "package.json"
        try:
            return json.loads(package_json_path.read_text())
        except FileNotFoundError:
            raise Exception(
                f"[hatch-nodejs-build] package.json not found in source directory '{package_json_path.absolute()}'"
            )

    def run_install_command(self):
        return self._run_command("install", self.plugin_config.install_command)

    def run_build_command(self):
        return self._run_command("build", self.plugin_config.build_command)

    def format_tokens(self, command: list[str]):
        tokens = {
            "node": self.node_executable,
            "npm": Path(self.node_executable).parent
            / ("npm.cmd" if sys.platform == "win32" else "npm"),
        }
        return [token.format(**tokens) for token in command]

    def _run_command(self, tag: str, tokens: list[str]):
        command = self.format_tokens(tokens)
        self.app.display_waiting(f"Running {tag} command: '{' '.join(command)}'")

        cwd = self.plugin_config.source_dir.absolute().resolve()
        self.app.display_info(f"└ working directory: '{cwd}'")
        self.app.display_mini_header(f"{tag.title()} logs")
        run(
            command,
            cwd=cwd,
            check=True,
        )
        self.app.display_mini_header(f"hatch-nodejs-build")
        self.app.display_info(f"{tag.title()} command finished.")
