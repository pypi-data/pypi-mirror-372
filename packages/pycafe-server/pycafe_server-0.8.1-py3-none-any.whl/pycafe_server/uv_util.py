import os
from pathlib import Path
import subprocess
import sys
from typing import Dict

try:
    import uv

    print("uv found")
except ImportError:
    print("uv not found")


def find_uv():
    # this path seems to work on vercel
    cmd = os.path.abspath(os.path.join(__file__, "../../bin/uv"))
    if os.path.exists(cmd):
        return cmd
    else:
        # this should be the uv way
        return uv.find_uv_bin()


uvcmd = os.fsdecode(find_uv())


# see:
#  https://github.com/astral-sh/uv/pull/6663
#  https://github.com/astral-sh/uv/issues/6641
# uv 0.3.5 added support for custom environments
# marker values for uv pip compile
# Note that this file/configuration is only respected
# when the --universal flag is passed to uv pip compile
uv_toml = """
environments = [
    "platform_system == 'Emscripten'"
]
"""

with open("/tmp/pycafe-server-uv.toml", "w") as f:
    f.write(uv_toml)

os.environ["UV_CONFIG_FILE"] = "/tmp/pycafe-server-uv.toml"


# from solara: https://github.com/widgetti/solara/blob/a7773eaaad230e8ffb20eaef4ac5b594a8f3453f/solara/server/utils.py#L21
def path_is_child_of(path: Path, parent: Path) -> bool:
    # We use os.path.normpath() because we do not want to follow symlinks
    # in editable installs, since some packages are symlinked
    path_string = os.path.normpath(path)
    parent_string = os.path.normpath(parent)
    if sys.platform == "win32":
        # on windows, we sometimes get different casing (only seen on CI)
        path_string = path_string.lower()
        parent_string = parent_string.lower()
    return path_string.startswith(parent_string)


def _run_resolve(
    requirements,
    constraints,
    overrides,
    python_version: str,
    universal: bool,
    files: Dict[str, bytes],
):
    import tempfile

    # create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # write the requirements file
        input = os.path.join(temp_dir, "requirements.txt")
        output = os.path.join(temp_dir, "requirements-resolved.txt")
        constraints_path = os.path.join(temp_dir, "constraints.txt")
        overrides_path = os.path.join(temp_dir, "overrides.txt")
        with open(input, "w") as f:
            f.write(requirements)
        with open(constraints_path, "w") as f:
            f.write(constraints)
        with open(overrides_path, "w") as f:
            f.write(overrides)

        # uv cannot install all minor versions of Python, just use the major.minor version
        python_version = ".".join(python_version.split(".")[:2])
        # run uv python install manually, see
        #  https://github.com/py-cafe/app/pull/252
        #  https://github.com/astral-sh/uv/issues/8039

        # don't expose potentially sensitive environment variables to build scripts run by uv
        sanitized_env = {
            k: v
            for k, v in os.environ.items()
            if k.startswith("UV_") or k in ["PATH", "LANG", "PWD"]
        }

        for filename, file_content in files.items():
            target_path = Path(os.path.join(temp_dir, filename))
            if not path_is_child_of(target_path, Path(temp_dir)):
                raise RuntimeError(f"Invalid file path: {target_path}")
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with open(target_path, "wb") as f:
                f.write(file_content)

        try:
            subprocess.run(
                [
                    uvcmd,
                    "python",
                    "install",
                    python_version,
                ],
                check=True,
                capture_output=True,
                env=sanitized_env,
            )
        except subprocess.CalledProcessError as e:
            print("Failed to install Python", e.stderr)
        # run uv pip compile
        subprocess.run(
            [
                uvcmd,
                "--directory",
                temp_dir,
                "pip",
                "compile",
                input,
                "-o",
                output,
                "-q",
                "--no-header",
                "-c",
                constraints_path,
                "--override",
                overrides_path,
                "--python-version",
                python_version,
            ]
            + (["--universal"] if universal else []),
            check=True,
            capture_output=True,
            env=sanitized_env,
        )
        # read the output file
        with open(output, "r") as f:
            output = f.read()
            print("resolved", output)
        return output
