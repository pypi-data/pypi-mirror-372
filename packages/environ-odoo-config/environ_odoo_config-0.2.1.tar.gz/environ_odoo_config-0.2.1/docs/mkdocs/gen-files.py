"""Generate the code reference pages and navigation."""

import sys
from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

config = mkdocs_gen_files.FilesEditor.current()

watched_paths = config.config["plugins"]["mkdocstrings"].config.data["handlers"]["python"]["paths"]
processed_path = []

if sys.version_info >= (3, 9):

    def is_relative_to(path1: Path, path2: Path):
        return path1.is_relative_to(path2)

else:

    def is_relative_to(path1: Path, path2: Path):
        try:
            path1.relative_to(path2)
            return True
        except ValueError:
            return False


for used_path in watched_paths:
    # TODO exclude the other path because handle after
    print(">", used_path)
    for path in sorted(Path(used_path).rglob("*.py")):
        print(">>", path)
        if any(
            is_relative_to(path, watch_path)
            for watch_path in watched_paths
            if watch_path != used_path and watch_path not in processed_path
        ):
            print(">>> Is relative !!!!!")
            continue

        if path.name == "_version.py":
            print("Exclude")
            continue

        module_path = path.relative_to(used_path).with_suffix("")
        doc_path = path.relative_to(used_path).with_suffix(".md")

        full_doc_path = Path("reference", doc_path)

        parts = tuple(module_path.parts)

        if parts[-1] == "__init__":
            parts = parts[:-1]
            doc_path = doc_path.with_name("index.md")
            full_doc_path = full_doc_path.with_name("index.md")
        elif parts[-1] == "__main__":
            continue

        nav[parts] = doc_path.as_posix()

        with mkdocs_gen_files.open(full_doc_path, "w") as fd:
            ident = ".".join(parts)
            fd.write(f"::: {ident}")

        mkdocs_gen_files.set_edit_path(full_doc_path, path)
    processed_path.append(used_path)

with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
