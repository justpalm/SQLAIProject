"""Pantry prompting comparison. Use --offline for verified reference outputs."""
import argparse
import json
import os
from pathlib import Path
import sqlite3
import textwrap
from time import time

ROOT = Path(__file__).resolve().parent
INVENTORY = 'WITH inventory AS (SELECT pantry_id, food_name, quantity, best_by_date FROM shelfs UNION ALL SELECT pantry_id, food_name, quantity, best_by_date FROM cupboards) '
CASES = [
    ('How many pantries are in each city?', 'SELECT a.city, COUNT(*) AS pantry_count FROM pantry p JOIN adress a ON a.address_id = p.address_id GROUP BY a.city ORDER BY a.city;'),
    ('What is the total quantity of food in each pantry, including shelves and cupboards?', INVENTORY + 'SELECT p.pantry_id, a.city, COALESCE(SUM(i.quantity), 0) AS total_quantity FROM pantry p JOIN adress a ON a.address_id = p.address_id LEFT JOIN inventory i ON i.pantry_id = p.pantry_id GROUP BY p.pantry_id, a.city ORDER BY p.pantry_id;'),
    ('Which foods have a quantity of zero, and in which pantry?', INVENTORY + 'SELECT pantry_id, food_name, quantity FROM inventory WHERE quantity = 0 ORDER BY pantry_id, food_name;'),
    ('Which pantry has the most food?', INVENTORY + 'SELECT p.pantry_id, a.city, COALESCE(SUM(i.quantity), 0) AS total_quantity FROM pantry p JOIN adress a ON a.address_id = p.address_id LEFT JOIN inventory i ON i.pantry_id = p.pantry_id GROUP BY p.pantry_id, a.city ORDER BY total_quantity DESC, p.pantry_id LIMIT 1;'),
]


def strategies(schema):
    instruction = '\nReturn exactly one read-only SQLite SELECT query (WITH is allowed). Return SQL only, without Markdown. Use the exact target table names.\n'
    same = '''Examples from the pantry database:
Question: What foods are on shelves in pantry 1?
SQL: SELECT food_name, quantity FROM shelfs WHERE pantry_id = 1 ORDER BY food_name;
Question: Which pantries are in Utah?
SQL: SELECT p.pantry_id FROM pantry p JOIN adress a ON a.address_id = p.address_id WHERE a.state = 'UT' ORDER BY p.pantry_id;
'''
    cross = '''Examples from other databases (these tables are NOT in the target database):
Schema: CREATE TABLE customer (customer_id INTEGER PRIMARY KEY, name TEXT); CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, amount REAL);
Question: Which customers have orders totaling more than 100 dollars?
SQL: SELECT c.customer_id, c.name, SUM(o.amount) AS total_amount FROM customer c JOIN orders o ON o.customer_id = c.customer_id GROUP BY c.customer_id, c.name HAVING SUM(o.amount) > 100 ORDER BY c.customer_id;
Schema: CREATE TABLE book (book_id INTEGER PRIMARY KEY, title TEXT); CREATE TABLE loan (loan_id INTEGER PRIMARY KEY, book_id INTEGER, returned_date TEXT);
Question: Which books have an unreturned loan?
SQL: SELECT b.book_id, b.title FROM book b WHERE EXISTS (SELECT 1 FROM loan l WHERE l.book_id = b.book_id AND l.returned_date IS NULL) ORDER BY b.book_id;
'''
    target = '\nTarget pantry database schema:\n' + schema + instruction
    return {'zero_shot': target, 'single_domain_double_shot': same + target, 'cross_domain_double_shot': cross + target}


def sanitizeForJustSql(value):
    value = value.strip()
    if value.startswith('```'):
        value = value.split('\n', 1)[1].rsplit('```', 1)[0]
    return value.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--model', default='gpt-4o')
    args = parser.parse_args()
    client = None
    if not args.offline:
        key = os.environ.get('OPENAI_API_KEY') or json.loads((ROOT / 'config.json').read_text())['openaiKey']
        if not key or key == 'need to replace with your open ai key':
            parser.error('Set OPENAI_API_KEY or config.json openaiKey, or use --offline.')
        from openai import OpenAI
        client = OpenAI(api_key=key)

    def ask(prompt):
        result = client.chat.completions.create(model=args.model, messages=[{'role': 'user', 'content': prompt}])
        return result.choices[0].message.content or ''

    schema = (ROOT / 'setup.sql').read_text()
    # Rebuild in memory without deleting an existing database file.
    with sqlite3.connect(':memory:') as connection:
        connection.execute('PRAGMA foreign_keys = ON')
        connection.executescript(schema)
        connection.executescript((ROOT / 'setupData.sql').read_text())
        assert not connection.execute('PRAGMA foreign_key_check').fetchall()
        connection.execute('PRAGMA query_only = ON')
        for strategy, prefix in strategies(schema).items():
            results = []
            for question, reference_sql in CASES:
                sql, raw, friendly, columns = '', '', '', []
                error = 'None'
                try:
                    sql = reference_sql if args.offline else sanitizeForJustSql(ask(prefix + '\nQuestion: ' + question))
                    cursor = connection.execute(sql)
                    if cursor.description is None:
                        raise ValueError('Expected a SELECT query with result columns')
                    columns = [column[0] for column in cursor.description]
                    rows = cursor.fetchall()
                    raw = str(rows)
                    if args.offline:
                        friendly = '; '.join(', '.join(f'{name}: {value}' for name, value in zip(columns, row)) for row in rows) if rows else 'No matching results.'
                    else:
                        friendly = ask('Answer concisely using only these results. Do not invent details.\n' + json.dumps(dict(question=question, columns=columns, rows=rows)))
                except Exception as exc:
                    error = str(exc)
                results.append(dict(question=question, sql=sql, queryRawResponse=raw, friendlyResponse=friendly, error=error, columns=columns))
            # Save short lines for reading in the editor; API calls still use prefix above.
            prompt_lines = [part for line in prefix.splitlines()
                            for part in (textwrap.wrap(line, width=100,
                                                      break_long_words=False,
                                                      break_on_hyphens=False) or [''])]
            output = dict(strategy=strategy, prompt_prefix=prompt_lines, generation_mode='offline_reference' if args.offline else 'openai', model=None if args.offline else args.model, questionResults=results)
            filename = f'response_{strategy}_pantry.json' if args.offline else f'response_{strategy}_{time()}.json'
            (ROOT / filename).write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')
            print(filename)
            if args.offline and any(row['error'] != 'None' for row in results):
                raise RuntimeError('Reference query validation failed')


if __name__ == '__main__':
    main()
