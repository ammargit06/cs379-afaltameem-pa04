"""
PA 4: The USILang Symbol Table -- verification suite.

Run: python test_symtable.py
Prints the Success Token only if every check below passes.
"""

import base64
import hashlib
import sys

from lexer import tokenize
from parser import parse
from symtable import Environment, SemanticError, check_program

ASSIGNMENT_ID = "PA04"


def get_student_id() -> str:
    """Prompt for the student's USI username; baked into the Success Token
    so a copied/shared token decodes to someone else's name, not yours."""
    student_id = input("Enter your USI username (e.g. cwill): ").strip()
    while not student_id:
        student_id = input("Username cannot be blank. Enter your USI username: ").strip()
    return student_id


def generate_token(assignment_id: str, student_id: str) -> str:
    digest = hashlib.sha256(f"CS379-{assignment_id}-{student_id}-VERIFIED".encode()).hexdigest()[:16]
    raw = f"CS379|{assignment_id}|{student_id}|PASS|{digest}"
    return base64.b64encode(raw.encode()).decode()


def print_success_banner(assignment_id: str) -> None:
    student_id = get_student_id()
    token = generate_token(assignment_id, student_id)
    print("\n" + "=" * 60)
    print(f"  ALL CHECKS PASSED -- {assignment_id}")
    print(f"  STUDENT: {student_id}")
    print("  SUCCESS TOKEN (paste this into Blackboard):")
    print(f"  {token}")
    print("=" * 60 + "\n")


def check(label: str, condition: bool, failures: list) -> None:
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}")
    if not condition:
        failures.append(label)


def check_source(source: str):
    return check_program(parse(tokenize(source)))


def main() -> int:
    failures: list = []

    print("Testing Environment directly...\n")
    env = Environment()
    env.define("x", 1)
    check("resolve() finds a name defined in the same scope", env.resolve("x") == 1, failures)
    try:
        env.define("x", 4)
        check("define() raises SemanticError on duplicate declaration in the same scope", False, failures)
    except SemanticError as e:
        msg = str(e)
        check("duplicate-declaration error mentions both line 4 and the original line 1", "4" in msg and "1" in msg, failures)

    child = Environment(parent=env)
    check("resolve() climbs to the parent scope when not found locally", child.resolve("x") == 1, failures)
    child.define("x", 9)  # shadowing a parent name must NOT raise
    check("shadowing a parent-scope name in a child scope does not raise", child.resolve("x") == 9, failures)
    try:
        Environment().resolve("nope")
        check("resolve() raises SemanticError for a totally undefined name", False, failures)
    except SemanticError:
        check("resolve() raises SemanticError for a totally undefined name", True, failures)

    if failures:
        print(f"\n{len(failures)} Environment check(s) failed -- fix these before check_program. No token issued.")
        return 1

    print("\nTesting check_program on valid programs...\n")
    valid_sources = [
        "let x = 5;",
        "let x = 5;\nlet y = x + 1;\nx = y * 2;",
        "let a = 1;\nlet b = a + 1;\nlet c = a + b;",
    ]
    for source in valid_sources:
        try:
            result_env = check_source(source)
            check(f"valid program checks cleanly: {source!r}", isinstance(result_env, Environment), failures)
        except SemanticError as e:
            check(f"valid program checks cleanly: {source!r} (raised {e})", False, failures)

    print("\nReplaying the Part A, Question 2 trace...\n")
    # let x = 5; let y = x + 1; x = y * 2; let x = 9;  -> the 4th line redeclares x
    try:
        check_source("let x = 5;\nlet y = x + 1;\nx = y * 2;\nlet x = 9;")
        check("redeclaring x on line 4 raises SemanticError", False, failures)
    except SemanticError as e:
        msg = str(e)
        check("redeclaring x on line 4 raises SemanticError mentioning lines 4 and 1", "4" in msg and "1" in msg, failures)

    print("\nTesting semantic errors are caught (use-before-declare, undeclared assignment)...\n")
    invalid_cases = [
        "y = x + 1;",             # use-before-declared assignment target and RHS
        "let x = x;",               # RHS resolved before x is defined -> use-before-declare
        "let x = 1;\ny = x + 1;",   # y was never declared
    ]
    for source in invalid_cases:
        try:
            check_source(source)
            check(f"'{source}' raises SemanticError", False, failures)
        except SemanticError:
            check(f"'{source}' raises SemanticError", True, failures)

    print()
    if failures:
        print(f"{len(failures)} check(s) failed. No token issued.")
        return 1

    print_success_banner(ASSIGNMENT_ID)
    return 0


if __name__ == "__main__":
    sys.exit(main())
