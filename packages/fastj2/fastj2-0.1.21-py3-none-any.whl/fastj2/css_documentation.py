"""
Simple CSS Documentation Generator
Only extract actual CSS class definitions (not usage)
"""

import re
from pathlib import Path
from collections import Counter, defaultdict


def generate_css_documentation(css_dir: Path):
    """Generate simple CSS documentation"""

    all_constructs = Counter()
    file_constructs = defaultdict(list)

    for css_file in Path(css_dir).rglob("*.css"):
        content = css_file.read_text(encoding='utf-8')
        constructs = extract_css_constructs(content)

        file_constructs[css_file] = constructs
        construct_names = [c['name'] for c in constructs]
        all_constructs.update(construct_names)

    # Generate documentation
    doc = [
        "# CSS Documentation",
        f"*Auto-generated from `{css_dir}/`*\n",
        "## Constructs by Usage Frequency",
        ""
    ]

    for construct_name, count in all_constructs.most_common():
        doc.append(f"- `{construct_name}` ({count} files)")

    doc.extend(["\n## Constructs by File", ""])

    for css_file in sorted(file_constructs.keys()):
        relative_path = css_file.relative_to(css_dir)
        doc.append(f"### {relative_path}")

        constructs = file_constructs[css_file]
        if constructs:
            for construct in constructs:
                doc.append(f"- `{construct['name']}` *(line {construct['line']})*")
        else:
            doc.append("- *No constructs found*")
        doc.append("")

    # Write documentation
    file = css_dir.parent / "css_documentation.md"
    file.write_text('\n'.join(doc), encoding='utf-8')
    return f"Documentation written to {file}"


def extract_css_constructs(content: str) -> list:
    """Extract only CSS class definitions and key constructs"""
    constructs = []
    lines = content.split('\n')

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip comments and empty lines
        if not stripped or stripped.startswith('/*') or stripped.startswith('//'):
            continue

        # Only match selectors that start a rule (followed by { on same line or next)
        # This avoids matching classes used in property values

        # Class definitions: .classname { or .classname,
        if re.match(r'^\s*\.[\w-]+\s*[{,]', line):
            class_match = re.findall(r'\.([a-zA-Z][\w-]*)', line)
            for class_name in class_match:
                constructs.append({
                    'type': 'class',
                    'name': class_name,
                    'line': i + 1
                })

        # CSS Variables: --variable-name:
        var_matches = re.findall(r'(--[\w-]+)\s*:', stripped)
        for var_name in var_matches:
            constructs.append({
                'type': 'variable',
                'name': var_name,
                'line': i + 1
            })

        # Animations: @keyframes name
        keyframe_match = re.match(r'^\s*@keyframes\s+([a-zA-Z][\w-]*)', stripped)
        if keyframe_match:
            constructs.append({
                'type': 'animation',
                'name': keyframe_match.group(1),
                'line': i + 1
            })

        # Media queries
        if stripped.startswith('@media'):
            constructs.append({
                'type': 'media-query',
                'name': stripped[6:].strip().rstrip('{').strip(),
                'line': i + 1
            })

    return constructs