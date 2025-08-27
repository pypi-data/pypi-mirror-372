import argparse

from pylatexenc.latexwalker import (
    LatexEnvironmentNode,
    LatexGroupNode,
    LatexMacroNode,
    LatexWalker,
)
from pylatexenc.macrospec import LatexContextDb, MacroSpec, ParsedMacroArgs

# Set up argument parser
argparser = argparse.ArgumentParser()
argparser.add_argument("input", help="Input LaTeX file")
group = argparser.add_mutually_exclusive_group()
group.add_argument("--output", "-o", help="Output file")
group.add_argument("--replace", "-x", help="Replace input file", action="store_true")

# Set up LaTeX context
db = LatexContextDb()
db.add_context_category(
    "changes",
    macros=[
        MacroSpec("added", "[{"),
        MacroSpec("highlight", "[{"),
        MacroSpec("deleted", "[{"),
        MacroSpec("comment", "[{"),
        MacroSpec("replaced", "[{{"),
    ],
)


def process_changes_args(args: ParsedMacroArgs) -> str:
    # remove surrounding braces and newlines
    text_to_keep = args.latex_verbatim()[1:-1].strip("\n")
    # trim each line for extra whitespace
    return "\n".join(map(str.strip, text_to_keep.splitlines()))


def handle_macro_node(node: LatexMacroNode) -> str:
    match node.macroname:
        case "added" | "highlight":
            return process_changes_args(node.nodeargd.argnlist[-1])
        case "deleted" | "comment":
            return ""
        case "replaced":
            return process_changes_args(node.nodeargd.argnlist[-2])
        case _:
            return node.latex_verbatim()


def handle_environment(node: LatexEnvironmentNode) -> str:
    output = f"\\begin{{{node.environmentname}}}"
    output += process_nodes(node.nodelist)
    output += f"\\end{{{node.environmentname}}}"
    return output


def handle_group(node: LatexGroupNode) -> str:
    output = "{"
    output += process_nodes(node.nodelist)
    output += "}"
    return output


def process_nodes(nodelist: list) -> str:
    output = ""
    prev_piece = None
    for n in nodelist:
        match n:
            case LatexEnvironmentNode():
                piece = handle_environment(n)
            case LatexGroupNode():
                piece = handle_group(n)
            case LatexMacroNode():
                piece = handle_macro_node(n)
            case _:
                piece = n.latex_verbatim()
                if (
                    prev_piece is not None  # skip first node
                    and not prev_piece  # previous piece was a deleted or comment macro
                    and not piece.startswith("\n\n")  # ignore empty lines
                ):
                    # Remove leading newline
                    piece = piece.removeprefix("\n")
        output += piece
        prev_piece = piece
    return output


def main():
    # Process arguments
    args = argparser.parse_args()
    input_file = args.input
    output_file = args.output if not args.replace else input_file

    # Read input file
    with open(input_file, mode="r") as fp:
        w = LatexWalker(
            fp.read(),
            latex_context=db,
        )
        nodelist, pos, len = w.get_latex_nodes()

    # Process the data
    output = process_nodes(nodelist)

    # Write results
    try:
        with open(output_file, "w") as fp:
            fp.write(output + "\n")
    except TypeError:
        print(output)  # write to stdout if no file given


if __name__ == "__main__":
    main()
