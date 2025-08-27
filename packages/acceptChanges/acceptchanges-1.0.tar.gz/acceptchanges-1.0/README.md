acceptChanges
=============

A simple Python tool for accepting all changes made to a LaTeX source file
using the package [`changes`](https://ctan.org/pkg/changes).

## Usage

    $ acceptChanges INPUT_FILE

See help with
    
    $ acceptChanges -h
    usage: acceptChanges.exe [-h] [--output OUTPUT | --replace] input

    positional arguments:
    input                Input LaTeX file

    options:
    -h, --help           show this help message and exit
    --output, -o OUTPUT  Output file
    --replace, -x        Replace input file

## Capabilities

Should work for changes inside macros, environments and groups.