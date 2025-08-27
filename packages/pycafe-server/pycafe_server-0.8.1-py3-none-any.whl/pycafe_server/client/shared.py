import io
from pathlib import Path
from typing import Any, Tuple, List, Union
import zipfile
from packaging.requirements import Requirement
from urllib.parse import urlparse
import json
from typing import List, Set, Any


def add_requirements_default(
    requirements: List[Requirement | str], defaults: List[Requirement | str]
) -> List[str | Requirement]:
    def getname(req: Union[str, Requirement]):
        if isinstance(req, Requirement):
            return req.name
        assert isinstance(req, str)
        if req.endswith(".whl"):
            name = req.split("-")[0]
            name = name.strip("/")
            return name

    requirements_names = list(map(getname, requirements))
    requirements_map = dict(zip(requirements_names, requirements))
    unused_defaults: List[Requirement | str] = []
    for default in defaults:
        default_name = getname(default)
        # default is not in requirements, so we add it
        if default_name not in requirements_names:
            unused_defaults.append(default)
        elif default_name == "tornado":
            # we have tornado, but we need our version
            unused_defaults.append(default)
    # filter out tornado
    requirements = [req for req in requirements if getname(req) != "tornado"]
    return requirements + unused_defaults


def parse_requirements(requirements_txt: str) -> Tuple[List[Requirement | str], str | None]:
    lines = requirements_txt.splitlines()
    requirements = []
    hash = None
    for line in lines:
        line = line.strip()
        if line.strip() in [".1"]:
            continue
        if line.startswith("#"):
            if line.startswith("# hash:"):
                hash = line.split(":", 1)[1].strip()
            continue
        # we support foo @ https://example.com/foo-1.2.3-py3-none-any.whl
        # via requirements, but we used to follow this pattern for relative
        # urls, e.g. /foo-1.2.3-py3-none-any.whl
        if urlparse(line).path.endswith(".whl") and "@" not in line:
            requirements.append(line)
        else:
            if "#" in line:
                line, comment = line.split("#", 1)
                line = line.strip()
                comment = comment.strip()
            else:
                comment = None
            if line.startswith("openssl"):
                continue
            if line:
                req = Requirement(line)
                # we add the comment to the requirement object
                # so we can test if it container the 'mock' string
                req.comment = comment
                requirements.append(req)
                is_mock = hasattr(req, "comment") and "mock" in (req.comment or "")
                req.mock = is_mock
    return requirements, hash


def get_alternative_wheels(repodata_packages: Any, origin: str):
    return {
        "tornado": {
            "6.4.2": f"{origin}/tornado-6.4.2-py3-none-any.whl",
        },
        "dash-daq": {
            "0.5.0": f"{origin}/dash_daq-0.5.0-py3-none-any.whl",
        },
        # Below fails in micropip, since it's built with a different version of emscripten than the python of pyodide 0.23.0
        "google-crc32c": {
            "1.5.0": f"{origin}/google_crc32c-1.5.0-py3-none-any.whl",
        },
        "pyperclip": {
            "1.8.2": f"{origin}/pyperclip-1.8.2-py3-none-any.whl"  # There is only a source distribution .tar.gz available, but micropip only supports .whl
        },
        "stringcase": {
            "1.2.0": f"{origin}/stringcase-1.2.0-py3-none-any.whl"  # There is only a source distribution .tar.gz available, but micropip only supports .whl
        },
        **(
            {
                "duckdb": {
                    "0.10.2": "https://duckdb.github.io/duckdb-pyodide/wheels/duckdb-0.10.2-cp311-cp311-emscripten_3_1_46_wasm32.whl",
                }
            }
            if "duckdb" not in repodata_packages
            else {}
        ),
    }


unvendored = ["ssl", "sqlite3", "distutils", "lzma"]


def supports_repodata(requirement: Requirement, repodata_packages: Any, verbose=False) -> bool:
    package_name = requirement.name
    if package_name in repodata_packages:
        if requirement.url:
            # we have a url, so we do not need to check the version
            return False
        if requirement.specifier.contains(repodata_packages[package_name]["version"]):
            # if the version requested is not in the repodata, we the version does not match,
            # we try to install from the wheel from pypi instead
            return True
        else:
            if verbose:
                print(
                    f"Version {requirement.specifier} requested for {package_name} does not match repodata version, {repodata_packages[package_name]['version']}, installing from pypi"
                )
            return False
    else:
        return False


def create_constraints(ignore_packages: Set[str], repodata_packages: Any, origin: str):
    # the constraints we send to uv compile
    constraints = ""

    for name, repodata_package in repodata_packages.items():
        if name in ["openssl"]:
            # not sure why this is vendored? we remove it from the constraints because uv cannot handle it
            # because it is not on pypi
            continue
        if name in ignore_packages:
            continue
        version = repodata_package["version"]
        constraints += f"{name}=={version}\n"

    # add the alternative wheels to the constraints
    for name, versions in get_alternative_wheels(repodata_packages, origin).items():
        constraints += f"{name}"
        first = True
        for version, url in versions.items():
            if first:
                constraints += f"=={version}"
                first = False
            else:
                constraints += f", =={version}"
        constraints += "\n"
    return constraints


def create_query(
    requirements: List[Requirement | str],
    repodata_packages: Any,
    python_version: str,
    origin: str,
    universal: bool = False,
):
    mock_names = [req.name for req in requirements if isinstance(req, Requirement) and getattr(req, "mock", False)]

    requirements_content = ""
    unvendored_but_requested: List[Requirement | str] = []
    overrides = ""
    # the local files we will send to the resolve endpoint
    local_files: list[str] = []

    for req in requirements:
        if isinstance(req, Requirement):
            # override in comment?
            if req.comment and "override" in req.comment:  # type: ignore
                overrides += str(req) + "\n"
            # uv should not see the unvendored packages
            if req.name not in unvendored:
                requirements_content += f"{req}\n"
            else:
                unvendored_but_requested.append(req)
            # e.g. foobar @ file://./foobar-0.1.0.whl
            if req.url and req.url.startswith("file://"):
                local_files.append(req.url)
        else:
            # e.g. file://./foobar-0.1.0.whl (without foobar @)
            if req.startswith("file://"):
                local_files.append(req)
            requirements_content += f"{req}\n"

    # ignore packages with are no in the repodata
    constraints = create_constraints(
        [
            req.name
            for req in requirements
            if isinstance(req, Requirement) and not supports_repodata(req, repodata_packages)
        ],
        repodata_packages,
        origin,
    )
    return (
        json.dumps(
            {
                "requirements": requirements_content,
                "constraints": constraints,
                "overrides": overrides,
                "python_version": python_version,
                "universal": "true" if universal else "false",
            }
        ),
        unvendored_but_requested,
        local_files,
    )


def create_minimal_wheel(wheel_path: str | Path) -> bytes:
    """
    Creates a minimal wheel archive containing only metadata files from the original wheel.

    Args:
        wheel_path (str): Path to the original wheel file.

    Returns:
        bytes: A bytes object representing a zip archive containing only the metadata files.
    """
    # Create an in-memory bytes buffer to hold the minimal wheel.
    out_buffer = io.BytesIO()

    # Open the original wheel as a zip file.
    with zipfile.ZipFile(wheel_path, "r") as zin:
        # Create a new zip file in the bytes buffer.
        with zipfile.ZipFile(out_buffer, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            # Iterate over each file in the original wheel.
            for info in zin.infolist():
                # Check if the file is in a .dist-info directory.
                if ".dist-info/" in info.filename:
                    # Read file data from the original zip.
                    file_data = zin.read(info.filename)
                    # Write the file (with its original metadata) to the new zip.
                    zout.writestr(info, file_data)

    # Reset buffer's current position to the beginning and return its bytes.
    out_buffer.seek(0)
    return out_buffer.getvalue()
