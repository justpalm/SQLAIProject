# AI SQL Pantry Database

This project compares zero-shot, single-domain, and cross-domain prompting for questions about food stored in pantries. The Schema itself is not complicated, as I wanted to compare it in a very controlled environment. It seemeed to help with testing very well!

## Files  (description from AI)

- `setup.sql`: SQLite schema. Existing table names `adress` and `shelfs` are retained so queries match your database.
- `setupData.sql`: Sample data for three pantries, with unique shelf and cupboard primary keys.
- `db_bot.py`: Builds an in-memory SQLite database and runs four common questions under all three strategies. It does not delete or modify an existing database file.
- `config.json`: Optional API key configuration. Do not commit real keys; alternatively set `OPENAI_API_KEY`.
- `response_*_pantry.json`: Verified offline reference responses for the new pantry data.
- Older JSON files without the `_pantry` suffix: Historical model runs, retained for reference.

## Queries Performances

The queries themselves ran relatively well! Here's a table of how the responses compared against the actual answers

| Question | Zero-shot | Single-domain | Cross-domain |
|---|---|---|---|
| Pantries per city | Correct | Correct | Correct |
| Total food per pantry | Incorrect | Correct | Incorrect |
| Foods with zero quantity | Correct | Correct | Correct |
| Pantry with the most food | Correct | Correct | Correct pantry, incorrect total |


Single domain seemed to be most dominant one. It is fascinating to me that just because SQL code runs correctly, this doesn't mean that it retrieves the right information. This can cause some confusion for the user, but it does seem that providing rellevant context helps the AI alot. Whereas a cross-domain and zero shot seem to mess it up a little bit.

Fun to mess around with though. It does seem we haven't made it to offloading all SQL work to LLM models.


