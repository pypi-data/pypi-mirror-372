"""
Simple JavaScript Documentation Generator
Only extract actual function/class definitions (not usage)
"""

import re
from pathlib import Path
from collections import Counter, defaultdict


def generate_js_documentation(js_dir: Path):
    """Generate simple JS documentation"""

    all_constructs = Counter()
    file_constructs = defaultdict(list)

    for js_file in Path(js_dir).rglob("*.js"):
        content = js_file.read_text(encoding='utf-8')
        constructs = extract_js_constructs(content)

        file_constructs[js_file] = constructs
        construct_names = [c['name'] for c in constructs]
        all_constructs.update(construct_names)

    # Generate documentation
    doc = [
        "# JavaScript Documentation",
        f"*Auto-generated from `{js_dir}/`*\n",
        "## Constructs by Usage Frequency",
        ""
    ]

    for construct_name, count in all_constructs.most_common():
        doc.append(f"- `{construct_name}` ({count} files)")

    doc.extend(["\n## Constructs by File", ""])

    for js_file in sorted(file_constructs.keys()):
        relative_path = js_file.relative_to(js_dir)
        doc.append(f"### {relative_path}")

        constructs = file_constructs[js_file]
        if constructs:
            for construct in constructs:
                if construct['params']:
                    doc.append(f"- `{construct['name']}({construct['params']})` *(line {construct['line']})*")
                else:
                    doc.append(f"- `{construct['name']}` *(line {construct['line']})*")
        else:
            doc.append("- *No constructs found*")
        doc.append("")

    # Write documentation
    file = js_dir.parent / "js_documentation.md"
    file.write_text('\n'.join(doc), encoding='utf-8')
    return f"Documentation written to {file}"


def extract_js_constructs(content: str) -> list:
    """Extract only top-level JS definitions"""
    constructs = []
    lines = content.split('\n')

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip comments and empty lines
        if not stripped or stripped.startswith('//') or stripped.startswith('/*'):
            continue

        # Only process top-level (minimal indentation)
        leading_spaces = len(line) - len(line.lstrip())
        if leading_spaces > 4:
            continue

        # Function declarations: function name(
        func_match = re.match(r'^function\s+([a-zA-Z_$][\w$]*)\s*\(([^)]*)', stripped)
        if func_match:
            name, params = func_match.groups()
            constructs.append({
                'type': 'function',
                'name': name,
                'params': params.strip(),
                'line': i + 1
            })
            continue

        # Const functions: const name = function( or const name = (
        const_func_match = re.match(r'^const\s+([a-zA-Z_$][\w$]*)\s*=\s*(?:function\s*\(([^)]*)|(?:\(([^)]*)\)|([a-zA-Z_$][\w$]*?))\s*=>)', stripped)
        if const_func_match:
            name = const_func_match.group(1)
            params = const_func_match.group(2) or const_func_match.group(3) or const_func_match.group(4) or ''
            constructs.append({
                'type': 'const-function',
                'name': name,
                'params': params.strip(),
                'line': i + 1
            })
            continue

        # Regular const: const NAME =
        const_match = re.match(r'^const\s+([a-zA-Z_$][\w$]*)\s*=', stripped)
        if const_match and 'function' not in stripped and '=>' not in stripped:
            name = const_match.group(1)
            constructs.append({
                'type': 'const',
                'name': name,
                'params': '',
                'line': i + 1
            })
            continue

        # Class declarations: class Name
        class_match = re.match(r'^class\s+([a-zA-Z_$][\w$]*)', stripped)
        if class_match:
            name = class_match.group(1)
            constructs.append({
                'type': 'class',
                'name': name,
                'params': '',
                'line': i + 1
            })

    return constructs