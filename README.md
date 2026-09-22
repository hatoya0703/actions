Personal GitHub Actions for reuse across repositories.

## translate-readme

Translates `README.md` to another language using DeepL. Only runs if the target file already exists (opt-in).

**Usage** — add to `.github/workflows/translate-readme.yml` in any repo:

```yaml
name: Translate README
on:
  push:
    branches: [main]
    paths: [README.md]
jobs:
  translate:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - uses: hatoya0703/actions/translate-readme@main
        with:
          deepl_api_key: ${{ secrets.DEEPL_API_KEY }}
```

**Opt-in:** create an empty `README.ja.md` in your repo to activate translation. Delete it to opt out.

**Inputs:**

| Input | Default | Description |
|-------|---------|-------------|
| `deepl_api_key` | required | DeepL API key (store as repo secret) |
| `source` | `README.md` | Source file |
| `target` | `README.ja.md` | Target file |
| `target_lang` | `JA` | DeepL language code |
