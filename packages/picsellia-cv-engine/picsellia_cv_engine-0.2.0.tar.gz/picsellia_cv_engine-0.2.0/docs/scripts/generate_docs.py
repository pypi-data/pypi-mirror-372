import os
from typing import Any

import yaml

# Directories to include in documentation
SOURCE_DIRS = ["src/picsellia_cv_engine"]

# Directories to exclude from documentation
EXCLUDE_DIRS = [
    "src/picsellia_cv_engine/core/logging",
]

# Specific files to exclude
EXCLUDE_FILES = [
    "enums.py",
    "logger.py",
    "src/picsellia_cv_engine/core/data/coco_file_manager.py",
]

DOCS_DIR = "docs/api"
MKDOCS_CONFIG_FILE = "mkdocs.yml"

# Template for Markdown doc pages
MKDOCS_TEMPLATE = """# {title}

::: {module}
    handler: python
    options:
        show_submodules: false
        show_if_no_docstring: true
        show_root_heading: true
"""


def should_exclude(path, filename=None):
    """Check if a path or specific file should be excluded."""
    if any(path.startswith(exclude) for exclude in EXCLUDE_DIRS):
        return True

    if filename:
        full_file_path = os.path.join(path, filename).replace("\\", "/")
        return any(
            full_file_path.endswith(exclude_file) or full_file_path == exclude_file
            for exclude_file in EXCLUDE_FILES
        )

    return False


def generate_markdown():
    os.makedirs(DOCS_DIR, exist_ok=True)
    generated_files = []

    for source_dir in SOURCE_DIRS:
        for root, _, files in os.walk(source_dir):
            if should_exclude(root):
                continue

            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    if should_exclude(root, file):
                        continue

                    module_path = (
                        os.path.join(root, file)
                        .replace("/", ".")
                        .replace("\\", ".")
                        .replace(".py", "")
                    )
                    module_path = module_path.replace("src.", "")
                    module_name = module_path.replace("picsellia_cv_engine.", "")

                    title = module_name  # Keep full dotted path as lowercase title

                    relative_path = (
                        root.replace(source_dir, "").strip(os.sep).replace(os.sep, "/")
                    )
                    output_dir = os.path.join(DOCS_DIR, relative_path)
                    os.makedirs(output_dir, exist_ok=True)

                    md_filename = os.path.join(
                        output_dir, f"{file.replace('.py', '.md')}"
                    )
                    md_content = MKDOCS_TEMPLATE.format(title=title, module=module_path)

                    with open(md_filename, "w") as md_file:
                        md_file.write(md_content)

                    generated_files.append((relative_path, file.replace(".py", ".md")))
                    print(f"✅ Generated: {md_filename}")

    return generated_files


def update_mkdocs_nav(generated_files):
    if not os.path.exists(MKDOCS_CONFIG_FILE):
        print(f"❌ Error: {MKDOCS_CONFIG_FILE} not found!")
        return

    with open(MKDOCS_CONFIG_FILE) as f:
        config = yaml.safe_load(f)

    # Remove previous API entries
    config["nav"] = [
        item
        for item in config["nav"]
        if not isinstance(item, dict) or "API Reference" not in item
    ]

    api_section: dict[str, list] = {"API Reference": [{"Overview": "api/index.md"}]}
    structure: dict[str, Any] = {}

    for path, file in generated_files:
        sections = path.split("/") if path else []
        target = structure

        for section in sections:
            target = target.setdefault(section, {})  # Keep lowercase

        display_name = file.replace(".md", "").replace("_", " ")
        target[display_name] = f"api/{path}/{file}" if path else f"api/{file}"

    def build_nav(struct: dict) -> list:
        nav = []
        for key, value in sorted(struct.items()):
            if isinstance(value, dict):
                nav.append({key: build_nav(value)})
            else:
                nav.append({key: value})
        return nav

    api_section["API Reference"].extend(build_nav(structure))
    config["nav"].append(api_section)

    with open(MKDOCS_CONFIG_FILE, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    print(f"✅ Updated {MKDOCS_CONFIG_FILE} with new API navigation.")


if __name__ == "__main__":
    generated_files = generate_markdown()
    update_mkdocs_nav(generated_files)
