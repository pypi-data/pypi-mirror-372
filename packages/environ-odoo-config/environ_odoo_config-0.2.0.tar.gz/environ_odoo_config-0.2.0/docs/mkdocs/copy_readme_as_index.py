"""Generate the code reference pages and navigation."""

from pathlib import Path

from mkdocs_gen_files import FilesEditor

config: FilesEditor = FilesEditor.current()

index_md_path = Path("index.md")
print(index_md_path)
readme_md_path = Path(config.config.config_file_path).parent.joinpath("README.md")
print(readme_md_path)
with open(str(readme_md_path), "r") as f_src, config.open(str(index_md_path), "w") as f_dest:
    f_dest.writelines(f_src.readlines())
