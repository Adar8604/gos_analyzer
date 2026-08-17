import re

def markdown_to_text(md: str):

    # Remove bold
    md = re.sub(r"\*\*(.*?)\*\*", r"\1", md)

    # Remove headings
    md = re.sub(r"^##\s*", "", md, flags=re.MULTILINE)

    # Convert markdown tables
    lines = md.splitlines()

    output = []

    table = []

    inside_table = False

    for line in lines:

        if "|" in line:

            if "---" in line:
                continue

            inside_table = True

            cols = [c.strip() for c in line.split("|") if c.strip()]

            table.append(cols)

        else:

            if inside_table:

                output.append("")

                for row in table:

                    output.append("    ".join(row))

                output.append("")

                table = []

                inside_table = False

            output.append(line)

    if table:

        output.append("")

        for row in table:

            output.append("    ".join(row))

    return "\n".join(output)