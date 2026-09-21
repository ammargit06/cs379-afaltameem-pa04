# PA 4: The USILang Symbol Table

Public template: https://github.com/cwillpinto/cs379-pa04-usilang-symbol-table

Due **Monday, September 21, 2026 at 11:59 PM**.

## Bring forward PA 2 and PA 3

Replace this starter folder's `lexer.py` and `parser.py` with your completed PA 2
and PA 3 versions. Keep all four Python files in this same directory so
`symtable.py` and `test_symtable.py` can import `lexer` and `parser` directly.
Before editing `symtable.py`, run your lexer and parser tests again from this
directory and resolve any remaining TODOs in those dependencies.

Full assignment: `PA_04_The_USILang_Symbol_Table.md`.

## Setup
Paste your own completed PA 2 `lexer.py` and PA 3 `parser.py` in first
(see the notes at the top of each file).

## Run
```bash
python test_symtable.py
```
Complete `Environment` and `check_program` in `symtable.py`. The
harness tests `Environment` directly, then checks valid programs
resolve cleanly, replays the Part A duplicate-declaration trace, and
confirms use-before-declare / undeclared-assignment cases raise
`SemanticError`. Success Token prints once every check passes.

## Submit
1. `PA4_Theory.pdf` (or `.md`)
2. `symtable.py` (and your working `lexer.py`/`parser.py`)
3. The Success Token
