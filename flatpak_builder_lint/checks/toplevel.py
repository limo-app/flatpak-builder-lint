from typing import Any

from .. import config
from . import Check


class TopLevelCheck(Check):
    def check_manifest(self, manifest: dict[str, Any]) -> None:
        build_extension = manifest.get("build-extension")
        appid = manifest.get("id")
        is_baseapp = bool(
            isinstance(appid, str) and appid.endswith(config.FLATHUB_BASEAPP_IDENTIFIER)
        )

        if not build_extension and not is_baseapp:
            command = manifest.get("command")
            if not command:
                self.errors.add("toplevel-no-command")
            elif command.startswith("/"):
                self.errors.add("toplevel-command-is-path")
                self.info.add(
                    "toplevel-command-is-path: Command in manifest is a path"
                    + f" {command}. Please install the executable to"
                    + " $FLATPAK_DEST/bin and change command to just the name"
                )

            branch = manifest.get("branch")
            def_branch = manifest.get("default-branch")
            allowed = ("stable", "beta", None)

            if branch not in allowed or def_branch not in allowed:
                self.errors.add("toplevel-unnecessary-branch")
                self.info.add(
                    "toplevel-unnecessary-branch: Please remove the toplevel"
                    + " branch or default-branch property in the manifest"
                )

        cleanup = manifest.get("cleanup")
        if cleanup and "/lib/debug" in cleanup:
            self.errors.add("toplevel-cleanup-debug")

        if not manifest.get("modules"):
            self.errors.add("toplevel-no-modules")

        gitmodules = manifest.get("x-gitmodules")
        if gitmodules:
            ext_gitmodules = [
                m for m in gitmodules if not m.startswith(config.FLATHUB_ALLOWED_GITMODULE_URLS)
            ]
            if ext_gitmodules:
                self.errors.add("external-gitmodule-url-found")
                self.info.add(
                    "external-gitmodule-url-found: Only flatpak, flathub"
                    + " and flathub-infra gitmodules are allowed in Flathub manifest"
                    + " repo {ext_gitmodules}"
                )

        large_files = manifest.get("x-large-git-files")
        if large_files:
            for file in large_files:
                self.errors.add(f"large-git-file-found-{file}")
                self.info.add(
                    f"large-git-file-found-{file}: Files larger than 20 MB are"
                    " not allowed in Flathub manifest git repo"
                )
