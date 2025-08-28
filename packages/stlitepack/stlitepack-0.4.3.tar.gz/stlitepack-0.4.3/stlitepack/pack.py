import json
from pathlib import Path
from packaging import version
import requests
import warnings
import re
import os
import base64
import fnmatch
import subprocess
import webbrowser
import sys
import time
import random
import socket

# MARK: HTML templates
TEMPLATE = """<!doctype html>
<html>
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta
      name="viewport"
      content="width=device-width, initial-scale=1, shrink-to-fit=no"
    />
    <title>{title}</title>
    <link
      rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/@stlite/browser@{stylesheet_version}/build/stlite.css"
    />
    <script
      type="module"
      src="https://cdn.jsdelivr.net/npm/@stlite/browser@{js_bundle_version}/build/stlite.js"
    ></script>
    {material_icons_style}
  </head>
  <body>
    <streamlit-app>
{app_files}
{requirements}
    </streamlit-app>
  </body>
</html>
"""


TEMPLATE_MOUNT = """<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
    <title>{title}</title>
    <link
      rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/@stlite/browser@{stylesheet_version}/build/style.css"
    />
  {material_icons_style}
  </head>
  <body>
    <div id="root"></div>
    <script type="module">
      import {{ mount }} from "https://cdn.jsdelivr.net/npm/@stlite/browser@{js_bundle_version}/build/stlite.js";
      mount(
        {{
          {pyodide_version}
          requirements: {requirements},
          entrypoint: "{entrypoint}",
          files: {{
{files}
          }},
        }},
        document.getElementById("root")
      );
    </script>
  </body>
</html>"""


# MARK: Private helper functions
def _read_file_flexibly(path: Path):
    try:
        # Try reading as UTF-8 text
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # Fallback: read as bytes and encode as base64
        binary_content = path.read_bytes()
        return base64.b64encode(binary_content).decode("utf-8")


def _material_icons_style(
    version: str = "Rounded", force_download: bool = False
) -> str:
    """
    Get Material Icons CSS with embedded base64 font.
    Caches the font locally to avoid repeated downloads.

    Parameters
    ----------
    version: str, optional
        Valid versions are 'Rounded', 'Outlined', 'Sharp'.
    force_download : bool, optional
        If True, always re-download the font from GitHub.

    Returns
    -------
    str
        A <style> block containing the Material Icons font embedded as base64.
    """
    if version not in ["Rounded", "Outlined", "Sharp"]:
        raise ValueError(
            f"Valid values for version are 'Rounded', 'Outlined' or 'Sharp'. You entered {version}."
        )

    try:
        # Cache directory (cross-platform)
        cache_dir = Path.home() / ".cache" / "material_icons"
        cache_dir.mkdir(parents=True, exist_ok=True)
        font_path = cache_dir / "MaterialIcons-Regular.woff2"

        # Download font if not cached or if forced
        if not font_path.exists() or force_download:
            url = f"https://raw.githubusercontent.com/google/material-design-icons/refs/heads/master/variablefont/MaterialSymbols{version}%5BFILL%2CGRAD%2Copsz%2Cwght%5D.woff2"
            resp = requests.get(url)
            resp.raise_for_status()
            font_path.write_bytes(resp.content)

        # Load from cache
        font_bytes = font_path.read_bytes()
        font_b64 = base64.b64encode(font_bytes).decode("utf-8")

        # Build CSS
        css = f"""
      <style>
      @font-face {{
        font-family: 'Material Icons';
        font-style: normal;
        font-weight: 400;
        src: url(data:font/woff2;base64,{font_b64}) format('woff2');
      }}

      .material-icons {{
        font-family: 'Material Icons';
        font-weight: normal;
        font-style: normal;
        font-size: 24px;
        display: inline-block;
        line-height: 1;
        text-transform: none;
        letter-spacing: normal;
        white-space: nowrap;
        direction: ltr;
        -webkit-font-smoothing: antialiased;
        text-rendering: optimizeLegibility;
        -moz-osx-font-smoothing: grayscale;
        font-feature-settings: 'liga';
      }}

      [data-testid="stIconMaterial"] {{
        font-family: 'Material Icons' !important;
        font-weight: normal;
        font-style: normal;
        font-size: 24px;  /* adjust as needed */
        display: inline-block;
        line-height: 1;
        text-transform: none;
        letter-spacing: normal;
        white-space: nowrap;
        direction: ltr;
        -webkit-font-smoothing: antialiased;
        text-rendering: optimizeLegibility;
        -moz-osx-font-smoothing: grayscale;
        font-feature-settings: 'liga';
      }}

      </style>
      """

        return css
    except:
        print("Error retrieving material icons font file")
        return ""


def _get_free_port(start=8000, end=8999, max_tries=20):
    """Find a free TCP port between start and end, or fall back to OS-assigned."""
    for _ in range(max_tries):
        port = random.randint(start, end)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("localhost", port))
                return port
            except OSError:
                continue  # port in use, try another
    # Fallback: let OS assign any free port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("localhost", 0))
        return s.getsockname()[1]


def _run_preview_server(
    port, dir_to_change_to: str = "", start_page: str = "docs/index.html"
):
    """Start a simple HTTP server and open the browser to the given page."""

    url = f"http://localhost:{port}/{start_page}"

    # Start the server in a subprocess
    process = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=dir_to_change_to,
    )

    # Give the server a moment to start
    time.sleep(1)

    # Open the browser
    webbrowser.open(url)

    print(f"Serving at {url}")
    print("Press Ctrl+C to stop the server.")
    print(
        "Note that any subsequent functions in your script will not run until you stop the server!"
    )

    try:
        process.wait()  # Keep running until interrupted
    except KeyboardInterrupt:
        print("\nStopping server...\n")
        process.terminate()


# MARK: Main Function
def pack(
    app_file: str,
    extra_files_to_embed: list[str] | None = None,
    extra_files_to_link: list[str] | dict | None = None,
    prepend_github_path: str | None = None,
    github_branch: str = "main",
    requirements: list[str] | None = None,
    title: str = "App",
    output_dir: str = "docs",
    output_file: str = "index.html",
    stylesheet_version: str = "0.80.5",
    js_bundle_version: str = "0.80.5",
    use_raw_api: bool = True,
    pyodide_version: str = "default",
    replace_df_with_table: bool = False,
    force_redownload_material_icons: bool = False,
    print_preview_message: bool = True,
    run_preview_server: bool = False,
    randomise_preview_port: bool = True,
    port: int = 8000,
    automated_stlite_fixes: bool = True,
):
    """
    Pack a Streamlit app into a stlite-compatible index.html file.

    This function reads a Streamlit Python script, injects it into an HTML
    template compatible with stlite, and writes the output as ``index.html``.
    The resulting HTML can be served as static content (e.g., via GitHub Pages).

    If additional pages are found in a 'pages' folder at the same level as the main app file,
    these will be added in as additional files.

    Note that the package will access the internet to download the latest version
    of Google's material UI font. This is necessary to ensure all standard streamlit icons
    display correctly, as well as allowing the use of material icons elsewhere in the app where
    streamlit supports this.

    Parameters
    ----------
    app_file : str
        Path to the main Streamlit application file (entrypoint) (e.g., ``"app.py"``).
        If additional pages are found in a 'pages' folder at the same level as this main app file,
        these will be added in as additional files.
    extra_files_to_embed : list[str], optional
        Additional files to mount directly into the app (e.g. .streamlit/config.toml).
        This will work best with files that are primarily text-based (e.g. .py, .toml, .csv).
        If binary files (e.g. .png, .jpg, .mp4) are provided, the script will attempt to convert
        them to base64 encoded representations that can live entirely within your file.
        However, this can massively increase the size of your resulting index.html file,
        and is currently experimental.
        For binary files it is recommended that you pass them using the 'extra_files_to_link'
        option instead.
    extra_files_to_link : list[str] or dict, optional
        Additional files to hyperlink to.
        - If passed as a list, must be used with the argument 'prepend_github_path'.
          The list must be a list of relative filepaths.
        - If passed as a dict, expects key:value pairs of relative_filepath: url
        e.g. {'img/my_img.png': 'https://raw.githubusercontent.com/your-github-username/your-github-repository/refs/heads/main/img/my_img.png}
        Can only be used with the raw API (use_raw_api=True).
        Defaults to None
    prepend_github_path : str, optional
        If files to be linked are stored on github, you can pass them as relative paths in the
        'extra_files_to_link' argument, and then use this argument to automatically generate the url
        links to the files in your repository.
        Needs to passed in the format "username/reponame"
        e.g. a username of Bergam0t with a reponame of my-streamlit-app would be
        "Bergam0t/my-streamlit-app"
        Then, for example, if you passed a list of ['img/my_img.png'] to the 'extra_files_to_link'
        argument, it would automatically generate the url of
        https://raw.githubusercontent.com/Bergam0t/my-streamlit-app/refs/heads/main/img/my_img.png
        Ignored if 'extra_files_to_link' is None.
        Can only be used with the raw API (use_raw_api=True).
        Defaults to None
    github_branch: str, optional
        If files to be linked to on Github need to come from a branch other than main, provide
        the name of the desired branch here.
        e.g. a username of Bergam0t with a reponame of my-streamlit-app would be
        "Bergam0t/my-streamlit-app"
        If you passed 'dev' as your branch to this argument, and then passed a list
        of ['img/my_img.png'] to the 'extra_files_to_link' argument, it would automatically
        generate the url of
        https://raw.githubusercontent.com/Bergam0t/my-streamlit-app/refs/heads/dev/img/my_img.png
        Ignored if 'extra_files_to_link' is None or prepend_github_path is None.
        Can only be used with the raw API (use_raw_api=True).
        Defaults to 'main'
    requirements : str or list of str
        Either:
          - Path to a ``requirements.txt`` file (str), or
          - A list of required Python packages (list of str).
    title : str, optional
        Title to insert into the HTML ``<title>`` tag. Default is ``"stlite app"``.
    output_dir : str, optional
        Directory where the generated ``index.html`` will be written.
        Default is ``"dist"``.
    use_raw_api : bool, optional
        If True, will use the version of the template that calls the `mount()` API explicitly.
        Default is `True`.
    pyodide_version: str, optional
        If not 'default', tries to serve the requested pyodide version from the pyodide CDN.
        Only works with raw API.
        Versions can be found here: https://pyodide.org/en/stable/project/changelog.html
        Default is 'default' (use default pyodide version, which is linked to stlite version)
    replace_df_with_table: bool, optional
        Some versions of streamlit and stlite seem to have issues with displaying tables that should
        be shown with st.dataframe.
        This option will replace all instances of st.dataframe with st.table, removing interactivity
        from the tables but ensuring they do at least display.
        Default is `False`.
    print_preview_message: bool, optional
        If True, prints a message explaining how to start a preview server.
        Ignored if run_preview_server is True.
        Default is `True`.
    run_preview_server: bool, optional
        If True, starts a small server previewing the output file.
        Supersedes print_preview_message. If both are True, only the preview server will be started.
        Default is `True`.
    randomise_preview_port: bool, optional
        If True, this will choose a different port from 8000-8999 each time.
        This can prevent clashes - for example, if you pack two apps and accidentally leave one
        running...
        Ignored if run_preview_server is False
        Default is True
    port: int, optional
        If randomise_preview_port is False, will use the port provided here.
        Ignored if run_preview_server is False
        Default is 8000
    automated_stlite_fixes: bool, optional
        If True, applies some automated fixes for common stlite issues
        - Inserts an await statement at the start of any st.spinner blocks to ensure the code in
        the spinner is non-blocking and also that the spinner itself is displayed
        - [PLANNED] Replace time.sleep with async equivalent

    Raises
    ------
    FileNotFoundError
        If the specified app_file does not exist.
    ValueError
        If ``requirements`` is not a list or a valid requirements file path.

    Notes
    -----
    - Currently supports only single-page Streamlit apps.
    - Future versions will support multi-page apps, additional resources,
      and GitHub Pages deployment automation.

    Examples
    --------
    Pack an app using a requirements file:

    >>> from stlitepack import pack
    >>> pack("app.py", requirements="requirements.txt", title="My App")

    Pack an app with inline requirements:

    >>> pack("app.py", requirements=["pandas", "numpy"], title="Data Explorer")

    The resulting HTML file will be written to ``dist/index.html`` by default.
    """
    # --- Version check ---
    min_version = version.parse("0.76.0")
    for v_name, v_str in [
        ("stylesheet_version", stylesheet_version),
        ("js_bundle_version", js_bundle_version),
    ]:
        if version.parse(v_str) < min_version:
            raise ValueError(f"{v_name} must be >= 0.76.0, got {v_str}")

    app_path = Path(app_file)
    if not app_path.exists():
        raise FileNotFoundError(f"App file not found: {app_file}")

    base_dir = app_path.parent

    # Gather files: entrypoint first, then optional pages/*
    files_to_pack = [app_path]
    pages_dir = base_dir / "pages"
    if pages_dir.is_dir():
        files_to_pack.extend(sorted(pages_dir.glob("*.py")))

    # Add extra files explicitly
    if extra_files_to_embed:
        files_to_pack.extend(Path(f) for f in extra_files_to_embed)

    # Normalize requirements
    if requirements is None:
        req_list = []
    elif isinstance(requirements, str):
        with open(requirements) as f:
            req_list = [
                line.split("#", 1)[0].strip()
                for line in f
                if line.strip() and not line.strip().startswith("#")
            ]
    else:
        req_list = requirements

    def code_replacements(code_str, replace_df_with_table=False):
        def replace_spinner(code_str):
            lines = code_str.splitlines()
            new_lines = []
            i = 0
            while i < len(lines):
                line = lines[i]
                stripped = line.lstrip()
                if stripped.startswith("with st.spinner"):
                    new_lines.append(line)  # keep spinner line
                    base_indent = line[: len(line) - len(stripped)]

                    # Find the indentation of the first line inside the spinner block
                    block_indent = None
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j]
                        if next_line.strip() == "":
                            j += 1
                            continue
                        next_line_indent = len(next_line) - len(next_line.lstrip())
                        if next_line_indent > len(base_indent):
                            block_indent = next_line[:next_line_indent]
                        break

                    # If the block is empty, use 4 spaces deeper than spinner
                    if block_indent is None:
                        block_indent = base_indent + "    "

                    # Insert extra lines with correct indentation
                    new_lines.append(f"{block_indent}import asyncio")
                    new_lines.append(f"{block_indent}await asyncio.sleep(1)")

                    i += 1
                else:
                    new_lines.append(line)
                    i += 1
            return "\n".join(new_lines)

        code_str = replace_spinner(code_str=code_str)

        if replace_df_with_table:
            code_str = re.sub(r"st\.dataframe", "st.table", code_str)

        return code_str

    # Build for raw API
    if use_raw_api:
        file_entries = []
        # Pack main files
        for f in files_to_pack:
            rel_name = f.relative_to(base_dir).as_posix()
            content = _read_file_flexibly(f)
            file_entries.append(
                f'"{rel_name}": `\n{code_replacements(content, replace_df_with_table=replace_df_with_table) if automated_stlite_fixes else content}\n            `'
            )

        # NOTE - Here will add in the step of including any additional linked files
        # where instead of embedding the code
        if isinstance(extra_files_to_link, dict):
            for k, v in extra_files_to_link.items():
                file_entries.append(f'"{k}": {{\nurl: "{v}"\n}}')
        elif isinstance(extra_files_to_link, list) and prepend_github_path is not None:
            for f in extra_files_to_link:
                file_entries.append(
                    f'"{f}": {{\nurl: "https://raw.githubusercontent.com/{prepend_github_path}/refs/heads/{github_branch}/{f}"\n}}'
                )
        elif isinstance(extra_files_to_link, list) and prepend_github_path is None:
            warnings.warn(
                "pyodide_version is ignored when use_raw_api=False. "
                "The simple API uses Pyodide version linked to the chosen stlite release.",
                UserWarning,
            )

        # Finalise the string of additional files
        files_js = ",\n".join(file_entries)

        if pyodide_version != "default":
            if not use_raw_api:
                warnings.warn(
                    "pyodide_version is ignored when use_raw_api=False. "
                    "The simple API uses Pyodide version linked to the chosen stlite release.",
                    UserWarning,
                )
                pyodide_version_string = ""
            else:
                pyodide_version_string = f'pyodideUrl: "https://cdn.jsdelivr.net/pyodide/v{pyodide_version}/full/pyodide.js",'
        else:
            pyodide_version_string = ""

        html = TEMPLATE_MOUNT.format(
            title=title,
            stylesheet_version=stylesheet_version,
            js_bundle_version=js_bundle_version,
            requirements=json.dumps(req_list),
            entrypoint=app_path.relative_to(base_dir).as_posix(),
            files=files_js,
            pyodide_version=pyodide_version_string,
            material_icons_style=_material_icons_style(
                force_download=force_redownload_material_icons
            ),
        )

    # Build for <streamlit-app> template
    else:
        # Build <app-file> blocks
        app_file_blocks = []
        for f in files_to_pack:
            code = f.read_text(encoding="utf-8")
            code = (
                code_replacements(code, replace_df_with_table=replace_df_with_table)
                if automated_stlite_fixes
                else code
            )
            rel_name = f.relative_to(base_dir).as_posix()
            entry_attr = " entrypoint" if f == app_path else ""
            app_file_blocks.append(
                f'  <app-file name="{rel_name}"{entry_attr}>\n'
                + "\n".join("    " + line for line in code.splitlines())
                + "\n  </app-file>"
            )
        app_files_section = "\n".join(app_file_blocks)

        # Requirements block
        if req_list:
            reqs = (
                "<app-requirements>\n" + "\n".join(req_list) + "\n</app-requirements>"
            )
        else:
            reqs = ""

        html = TEMPLATE.format(
            title=title,
            app_files=app_files_section,
            requirements=reqs,
            stylesheet_version=stylesheet_version,
            js_bundle_version=js_bundle_version,
            material_icons_style=_material_icons_style(
                force_download=force_redownload_material_icons
            ),
        )

    # Write to output dir
    outdir = Path(output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    outfile = outdir / output_file
    outfile.write_text(html, encoding="utf-8")

    print(f"Packed app written to {outfile}")

    if run_preview_server:
        if randomise_preview_port:
            _run_preview_server(
                port=_get_free_port(),
                start_page=f"{output_file}",
                dir_to_change_to=None if output_dir == "current_dir" else output_dir,
            )
        else:
            _run_preview_server(
                port=8000,
                start_page=f"{output_file}",
                dir_to_change_to=None if output_dir == "current_dir" else output_dir,
            )
    elif print_preview_message:
        print("Preview your app by running")
        print("python -m http.server 8000")
        print("and navigating to the index.html file.")
        print("e.g. http://localhost:8000/index.html")
        print("or http://localhost:8000/docs/index.html")


def get_stlite_versions():
    """
    Fetch the list of released Stlite versions from GitHub and print a nicely formatted message.

    Returns
    -------
    list[str]
        A list of version strings (e.g., ["0.84.1", "0.84.0", ...]).

    Raises
    ------
    RuntimeError
        If the GitHub API request fails.
    """
    url = "https://api.github.com/repos/whitphx/stlite/releases"
    resp = requests.get(url)
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to fetch Stlite releases: HTTP {resp.status_code}")

    releases = resp.json()
    versions = [r["tag_name"].lstrip("v") for r in releases]

    if not versions:
        print("No versions found on GitHub.")
        return []

    newest = versions[0]
    other_versions = versions[1:]

    # Terminal-friendly formatting
    print("\n=== Stlite Versions ===")
    print(f"Newest release: {newest}\n")

    if other_versions:
        print("Other valid releases:")
        # print in columns of 5
        for i in range(0, len(other_versions), 5):
            print("  " + ", ".join(other_versions[i : i + 5]))
    print("=======================\n")

    return versions


def list_files_in_folders(folders, recursive=False, pattern=None, invert=False):
    """
    Given a list of folder paths, return a list of all files inside them
    with their relative paths (including the folder name).

    Parameters
    ----------
    folders : list of str
        List of folder paths to search in.
    recursive : bool, default=False
        If True, include files in subfolders recursively.
    pattern : str, optional
        A glob pattern (e.g., "*.csv") or regex to filter file paths.
        If None, all files are included.
    invert : bool, default=False
        If True, include all files *except* those that match the pattern.
    """
    all_files = []

    # Convert glob to regex if needed
    if pattern:
        # Simple heuristic: treat pattern as glob if it contains *, ?, or []
        if any(char in pattern for char in "*?[]"):
            regex = re.compile(fnmatch.translate(pattern))
        else:
            regex = re.compile(pattern)
    else:
        regex = None

    for folder in folders:
        folder = os.path.abspath(folder)  # normalize path
        if recursive:
            for root, _, files in os.walk(folder):
                for file in files:
                    rel_path = os.path.relpath(
                        os.path.join(root, file), start=os.path.dirname(folder)
                    )
                    rel_path = rel_path.replace(os.sep, "/")
                    if regex:
                        match = bool(regex.search(rel_path))
                        if match != invert:
                            all_files.append(rel_path)
                    else:
                        all_files.append(rel_path)
        else:
            for file in os.listdir(folder):
                full_path = os.path.join(folder, file)
                if os.path.isfile(full_path):
                    rel_path = os.path.relpath(full_path, start=os.path.dirname(folder))
                    rel_path = rel_path.replace(os.sep, "/")
                    if regex:
                        match = bool(regex.search(rel_path))
                        if match != invert:
                            all_files.append(rel_path)
                    else:
                        all_files.append(rel_path)

    return all_files
