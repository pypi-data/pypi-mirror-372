import re

def render_nanohtml(text):
    tag_pattern = re.compile(r"(\w+)(?:\s+([^:]+):\s*([^;]+);)?\s*:\s*(.*?)::", re.S)
    html = text
    for match in tag_pattern.finditer(text):
        tag, attr, val, content = match.groups()
        attr_str = ""
        if attr and val:
            if attr.strip() == "style":
                attr_str = f' style="{val.strip()}"'
            elif attr.strip() == "class":
                attr_str = f' class="{val.strip()}"'
        html_tag = f"<{tag}{attr_str}>{content.strip()}</{tag}>"
        html = html.replace(match.group(0), html_tag)
    return html
