import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "sales_warehouse.db"
SQL_PATH = BASE_DIR / "queries.sql"


def split_sql_statements(sql_text):
    """Split SQL statements while respecting SQL comments and quoted strings."""
    statements = []
    current = []
    in_single = False
    in_double = False
    in_backtick = False
    in_bracket = False
    in_line_comment = False
    in_block_comment = False
    i = 0

    while i < len(sql_text):
        char = sql_text[i]
        nxt = sql_text[i + 1] if i + 1 < len(sql_text) else ""

        if in_line_comment:
            if char == "\n":
                in_line_comment = False
                current.append(char)
            i += 1
            continue

        if in_block_comment:
            if char == "*" and nxt == "/":
                in_block_comment = False
                i += 2
            else:
                i += 1
            continue

        if not (in_single or in_double or in_backtick or in_bracket):
            if char == "-" and nxt == "-":
                in_line_comment = True
                i += 2
                continue
            if char == "/" and nxt == "*":
                in_block_comment = True
                i += 2
                continue

        if char == "'" and not (in_double or in_backtick or in_bracket):
            if in_single and nxt == "'":
                current.extend([char, nxt])
                i += 2
                continue
            in_single = not in_single
        elif char == '"' and not (in_single or in_backtick or in_bracket):
            in_double = not in_double
        elif char == "`" and not (in_single or in_double or in_bracket):
            in_backtick = not in_backtick
        elif char == "[" and not (in_single or in_double or in_backtick):
            in_bracket = True
        elif char == "]" and in_bracket:
            in_bracket = False

        if char == ";" and not (
            in_single or in_double or in_backtick or in_bracket
        ):
            statement = "".join(current).strip()
            if statement:
                statements.append(statement)
            current = []
        else:
            current.append(char)

        i += 1

    remainder = "".join(current).strip()
    if remainder:
        statements.append(remainder)

    return statements


def main():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_PATH}. Run load_warehouse.py first."
        )

    if not SQL_PATH.exists():
        raise FileNotFoundError(f"SQL file not found: {SQL_PATH}")

    sql_text = SQL_PATH.read_text(encoding="utf-8-sig")
    statements = split_sql_statements(sql_text)

    if not statements:
        print("No SQL statements found.")
        return

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")

        for number, statement in enumerate(statements, start=1):
            print(f"\n{'=' * 70}")
            print(f"Query {number}")
            print("=" * 70)

            cursor = conn.execute(statement)

            if cursor.description:
                columns = [item[0] for item in cursor.description]
                rows = cursor.fetchall()

                print(" | ".join(columns))
                print("-" * 70)

                for row in rows:
                    print(" | ".join(str(value) for value in row))

                print(f"\nRows returned: {len(rows)}")
            else:
                print("Statement executed successfully.")

    print(f"\nCompleted. Executed {len(statements)} SQL statements.")


if __name__ == "__main__":
    main()
