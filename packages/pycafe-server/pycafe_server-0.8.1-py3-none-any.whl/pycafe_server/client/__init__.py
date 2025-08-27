import argparse
import os
import json
import sys
import requests
import hashlib
import base64

from pycafe_server.client import requirements_system, shared

app_types = ["vizro", "dash", "streamlit", "solara", "panel", "shiny"]
pyodide_versions = ["0.27.2", "0.27.1", "0.26.2", "0.26.1", "0.25.1", "0.23.0"]


def main():
    url = os.environ["PYCAFE_CLIENT_URL"].rstrip("/")
    token = os.environ["PYCAFE_API_KEY"]
    parser = argparse.ArgumentParser(
        description="Send a GET request to the /api/sign endpoint with a hash and an Authorization header."
    )
    parser.add_argument(
        "--input-dir",
        default="",
        help="The source directory to make html (default: '')",
        required=True,
    )
    parser.add_argument(
        "--name", default="project", help="The of the html (default: 'project')"
    )
    parser.add_argument("--title", default="", help="The title (default: '')")
    parser.add_argument(
        "--pyodide",
        default="0.26.1",
        choices=pyodide_versions,
        help=f"The pyodide version (default: '0.26.1') {pyodide_versions}",
    )
    parser.add_argument(
        "--type",
        default="",
        choices=app_types,
        help=f"The app type. (default: '') {app_types}",
        required=True,
    )
    args = parser.parse_args()

    module_dir = os.path.dirname(__file__)
    file_path = os.path.join(module_dir, "file-template.html")

    with open(file_path, "r") as f:
        template = f.read()

    project = {
        "name": args.name,
        "type": args.type,
        "python": f"pyodide-v{args.pyodide}",
        "code": None,
        "requirements": None,
        "files": [],
        "title": args.title,
    }

    for root, dirs, files in os.walk(args.input_dir):
        dirs[:] = [
            d
            for d in dirs
            if d not in ["venv", ".venv", "env", ".env", ".git", "__pycache__"]
        ]
        for filename in files:
            file_path = os.path.join(root, filename)
            sub_path = file_path[len(args.input_dir) + 1 :]
            try:
                if filename in [".DS_Store"]:
                    continue
                if sub_path in ["app.py", "requirements.txt"]:
                    with open(file_path, "r", encoding="utf-8") as f:
                        project["code" if sub_path == "app.py" else "requirements"] = (
                            f.read()
                        )
                else:
                    encoding = {}
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                    except UnicodeDecodeError:
                        with open(file_path, "rb") as f:
                            content = f.read()
                            content = base64.b64encode(content).decode("utf-8")
                            encoding = {"encoding": "base64"}
                    project["files"].append(
                        {"name": sub_path, "content": content, **encoding}
                    )
            except Exception as e:
                print(f"Could not read {file_path}: {e}")

    if project["code"] is None or project["requirements"] is None:
        raise ValueError("app.py and requirements.txt are required")

    requirements, _ = shared.parse_requirements(project["requirements"])
    defaults = shared.parse_requirements(getattr(requirements_system, args.type))[0]
    requirements = shared.add_requirements_default(requirements, defaults)

    # lock_file = "https://cdn.jsdelivr.net/npm/pyodide@0.27.1/pyodide-lock.json"
    # read lock_file
    lock_file = requests.get(
        f"https://cdn.jsdelivr.net/npm/pyodide@{args.pyodide}/pyodide-lock.json"
    ).json()
    python_version = lock_file["info"]["python"]
    repodata_packages = lock_file["packages"]
    # print(lock_file)

    query, unvendored_but_requested, local_files = shared.create_query(
        requirements, repodata_packages, python_version, url
    )

    files = [
        (
            "wheels",
            (
                file_name[7:],
                shared.create_minimal_wheel(args.input_dir + "/" + file_name[7:]),
            ),
        )
        for file_name in local_files
    ]

    resolve_request = requests.post(
        f"{url}/api/resolve",
        files=files,
        data={"query": query},
    )
    if not resolve_request.ok:
        print(
            f"Error resolving requirements: {resolve_request.status_code} {resolve_request.text}"
        )
        sys.exit(1)
    env_lock = resolve_request.text
    project["lockfileContent"] = env_lock

    sorted_project = dict(sorted(project.items()))
    sorted_project["files"] = [
        dict(sorted(file.items())) for file in sorted_project["files"]
    ]
    project_string = json.dumps(
        sorted_project, separators=(",", ":"), ensure_ascii=False
    )
    hash = hashlib.sha256(project_string.encode()).hexdigest()

    try:
        response = requests.get(
            f"{url}/api/sign?hash={hash}",
            headers={
                "Authorization": f"Bearer {token}",
                "X-Authorization": f"Bearer {token}",
            },
        )
        if not response.ok:
            print(f"Error: {response.status_code} {response.text}")
            sys.exit(1)
        signature = response.json()["signatureJwt"]

        with open(f"{args.name}.html", "w") as f:
            f.write(
                template.replace("#title#", args.name)
                .replace("#viewerUrl#", f"{url}/view?iframe")
                .replace('"#signatureJwt#"', f'"{signature}"')
                .replace("true; //#preAuth#", "false")
                .replace("#origin#", url)
                .replace('{ "projectState": "" }', project_string.replace("/", "\\/"))
            )
        print(f"Created {args.name}.html")
    except requests.RequestException as e:
        print("Error occurred while making the request:", e)


if __name__ == "__main__":
    main()
