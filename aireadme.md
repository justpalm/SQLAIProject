# AI SQL Pantry Database

This project compares zero-shot, single-domain, and cross-domain prompting for questions about food stored in pantries.

## Files

- `setup.sql`: SQLite schema. Existing table names `adress` and `shelfs` are retained so queries match your database.
- `setupData.sql`: Sample data for three pantries, with unique shelf and cupboard primary keys.
- `db_bot.py`: Builds an in-memory SQLite database and runs four common questions under all three strategies. It does not delete or modify an existing database file.
- `config.json`: Optional API key configuration. Do not commit real keys; alternatively set `OPENAI_API_KEY`.
- `response_*_pantry.json`: Verified offline reference responses for the new pantry data.
- Older JSON files without the `_pantry` suffix: Historical model runs, retained for reference.

## Generate reference files without an API key

```powershell
python db_bot.py --offline
```

This regenerates:

- `response_zero_shot_pantry.json`
- `response_single_domain_double_shot_pantry.json`
- `response_cross_domain_double_shot_pantry.json`

These are **hand-authored SQL reference answers executed against the sample data**, not model-generated experimental results. Their `generation_mode` is `offline_reference`. They intentionally have the same answers across strategies; only the prompt prefixes differ. Do not use these files to claim that one prompting strategy performs better.

## Run a model comparison

Install the `openai` Python package, then set your API key through the environment or `config.json`:

```powershell
python -m pip install openai
$env:OPENAI_API_KEY = 'your-key'
.\.venv\Scripts\python.exe db_bot.py
```

You can select a model with `--model`. Live runs make paid API requests and save separate timestamped JSON files with `generation_mode` set to `openai`.

## Strategies and results

- Zero-shot: target schema and instructions, with no question/SQL examples.
- Single-domain double-shot: two examples using the pantry schema.
- Cross-domain double-shot: two examples using sales and library schemas, followed by the target pantry schema.

All strategies answer the same four questions about city counts, total inventory, out-of-stock food, and which pantry has the most food. Totals combine shelves and cupboards using `UNION ALL`; quantity means stored units, not weight.

For readability, new outputs store `prompt_prefix` as an array of short text lines instead of one long escaped string. Read the lines from top to bottom: examples (if any), target schema, then instructions. Join them with `"\n".join(data["prompt_prefix"])` if you need text from a saved file. The bot still sends its original full text prompt to the model. Older historical files retain their original format.

The `questionResults` entries contain `question`, `sql`, `queryRawResponse`, `friendlyResponse`, and `error`. Additional `columns`, `generation_mode`, and `model` fields clarify the results. Queries run with SQLite query-only mode enabled. Failed questions record an error with freshly initialized result fields.
