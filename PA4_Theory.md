# PA 4 Theory: The USILang Symbol Table

## 1. Binding Times (15 pts)

For `let x = 5;`:

**(a) The fact that `x` is a name that can be bound at all** — *language design time*. USILang's grammar decided, when the language itself was designed, that a `let` statement introduces a new bindable name. This isn't decided per-program or per-run; it's a fixed rule of the language that any identifier following `let` is eligible to become a binding.

**(b) The specific storage cell `x` occupies during execution** — *run time*. `symtable.py`'s `Environment` is a dictionary built up dynamically as `check_program` walks the statement list; the entry for `x` doesn't exist until `Environment.define` actually executes that line. There is no fixed address assigned earlier (no compile-time layout pass), so the storage association is made while the program is running.

**(c) The value `5` stored in that cell** — *run time*. The literal is evaluated and attached to `x` only at the moment the declaration statement executes; nothing about the value `5` is known or reserved before that point.

**Type binding:** USILang has no static type declarations, so there is no compile-time type binding at all. If USILang's interpreter attached types to values (it doesn't, at this stage — PA 4 only resolves names), that binding would happen dynamically, at run time, and would be a property of the *value* currently in the cell rather than a fixed property of the *name* `x`. Since PA 4 doesn't check or record types, `x` currently has no type binding of any kind — only a name binding.

## 2. Symbol Table State Tracing (15 pts)

```
let x = 5;       (line 1)
let y = x + 1;   (line 2)
x = y * 2;       (line 3)
let x = 9;       (line 4)
```

| After statement | Symbol table (`name -> declaration line`) |
|---|---|
| `let x = 5;` | `{x: 1}` |
| `let y = x + 1;` | `{x: 1, y: 2}` |
| `x = y * 2;` | `{x: 1, y: 2}` (an assignment resolves an existing binding — it never mutates the symbol table) |

The fourth statement, `let x = 9;`, is where the semantic error occurs. `x` is already declared in this same scope (line 1), so `Environment.define` raises a **duplicate declaration** error. The message must reference **line 4** (where the conflicting redeclaration appears) and **line 1** (where `x` was originally declared), e.g. `"Duplicate declaration of 'x' (line 4; originally declared line 1)."`.

## 3. Syntax Errors vs. Semantic Errors (10 pts)

`y = x + 1;` is syntactically well-formed because it matches PA 3's grammar rule `<assignment> ::= IDENT '=' <expr> ';'` exactly — an identifier, `=`, an expression, `;`. The parser's job is purely structural: it checks that tokens appear in a shape the grammar allows, node by node, with no memory of what happened in earlier statements. It has no symbol table and no concept of "has `x` been declared yet," so it has nothing to check the reference against and happily builds a valid `Assignment` node.

The bug is instead a **semantic error** — specifically a *use-before-declaration* (undeclared-name) error. It's semantic because it isn't a question about the shape of this one statement; it's a question about the *meaning* of the name `x` at this specific point in the program, which depends on everything that came before it.

This category of error can only be caught by a stage that tracks **order** and **state** because "has `x` been declared yet" is not a property of an isolated AST node — it's a property of the accumulated set of declarations processed so far. A parse tree is static structure with no running memory between nodes; only a stage like `check_program`, which walks statements in source order and threads an `Environment` through that walk (mutating it via `define` as declarations are processed), can answer a question that depends on "what has already happened" rather than "what does this one statement look like."

## 4. Designing for the Future (10 pts)

`Environment` carries a `parent` pointer starting this week specifically so that PA 5's scope resolver can *extend* the class rather than *replace* it. If PA 4 used a single flat dictionary with no parent link, "just add nesting later" would mean going back and changing `Environment`'s fundamental shape: `resolve` would need to be rewritten from a flat dict lookup into a chain-walking lookup, `define` would need to be re-scoped to "the current frame" instead of "the only frame," and every test that already passes against the flat version would need to be re-verified against the new nested version — all while PA 5 is due in exactly one week.

Building the parent pointer in now means the *lookup strategy* (`resolve` climbs from the current scope outward, stopping at the first match; `define` only ever writes to the current scope's own dict) is already correct and already tested, even though every PA 4 test case only ever exercises one global scope with `parent=None`. PA 5 can then introduce new scopes (e.g., one per block or function) by constructing new `Environment(parent=enclosing_env)` instances and reusing the exact same `resolve`/`define` methods, instead of solving "how do nested scopes hand off lookups to their enclosing scope" for the first time under next week's deadline.
