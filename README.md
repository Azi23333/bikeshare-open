# Capital Bikeshare demand forecast

This DSC 180A project forecasts total daily Capital Bikeshare rides in Washington, DC, one day ahead. It trains on 2011, validates on the first half of 2012, and tests on the second half of 2012.

[GitHub repository](https://github.com/Azi23333/bikeshare-open) · [Final report](REPORT.md)

## Run the pipeline

These commands use Ubuntu in Windows Subsystem for Linux (WSL), Python 3.14.4, Git, and GNU Make. Run them from a WSL terminal.

```bash
git clone https://github.com/Azi23333/bikeshare-open.git
cd bikeshare-open
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export OMP_NUM_THREADS=2
make all
make test
```

`make all` checks the bundled CSV's checksum, builds the feature table, and writes `reports/metrics.json`. The top-level scores use the final feature set and the original ride-count target. `exercise1_before` holds the results from the starter at `67dd845`, saved in `reports/exercise1_metrics_before.json`. `make test` runs all 18 tests, including the final Ridge threshold check. The pipeline and tests run locally after dependency installation.

Run `python -m src.leakage_demo` to reproduce the deliberately leaky example. The separate HGB target-ratio experiment can be run from its branch with `python -m experiments.target_ratio_validation`. [Experiment branch](https://github.com/Azi23333/bikeshare-open/tree/exercise4-target-ratio) · [Saved validation results](reports/exercise4_validation.json)

## Claude Code and Ollama Cloud

The exercises used Claude Code 2.1.325 in WSL with Ollama Cloud's `glm-5.3-flash`. To use the same setup, install [Claude Code](https://code.claude.com/docs/en/setup) in WSL and put this configuration in `.claude/settings.local.json`. Replace the placeholder with your Ollama Cloud API key. Git ignores the file.

```json
{
  "model": "glm-5.3-flash",
  "env": {
    "ANTHROPIC_BASE_URL": "https://ollama.com",
    "ANTHROPIC_AUTH_TOKEN": "<your Ollama Cloud key>",
    "ANTHROPIC_API_KEY": ""
  }
}
```

Start `claude` from the repository root and use `/status` to check the model. See `CLAUDE.md` for project rules and `.claude/skills/` for `/new-feature` and `/seed-fault`.

The submitted SDK self-audit is in `reports/audit.jsonl`. To rerun it after `make all`, activate the Python environment and set the cloud credentials in the shell. This example writes the repeat run to the ignored `audit.jsonl` at the repo root.

```bash
read -rsp 'Ollama Cloud API key: ' ANTHROPIC_AUTH_TOKEN
printf '\n'
export ANTHROPIC_AUTH_TOKEN
export ANTHROPIC_BASE_URL=https://ollama.com ANTHROPIC_API_KEY='' AUDIT_MODEL=glm-5.3-flash
python agent/audit.py . --out audit.jsonl --concurrency 1
unset ANTHROPIC_AUTH_TOKEN
```

## Data and evidence

`data/raw/bike_daily.csv` is the daily Bike Sharing Dataset (Fanaee-T and Gama, 2013) from the processed mirror used in Christoph Molnar's *Interpretable Machine Learning*. `src/config.py` lists how the mirror differs from the UCI release. [Processed source CSV](https://raw.githubusercontent.com/christophM/interpretable-ml-book/master/data/bike.csv)

- [Research decisions](docs/DECISIONS.md)
- [Test-first and seeded-fault evidence](docs/SEEDED_FAULTS.md)
- [Peer leakage audit](docs/AUDIT.md)
