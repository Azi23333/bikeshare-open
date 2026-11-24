# Capital Bikeshare demand forecast

## Results

The task was to predict total daily rides (`cnt`) one day ahead. The training set had 348 days in 2011, the validation set had 182 days in the first half of 2012, and the test set had 184 days in the second half of 2012. Both versions used the same dates. The only feature difference was `cnt_roll_range_7`, the highest minus the lowest ride count over the previous seven calendar days. The window starts from yesterday's count, so all seven inputs are available when the forecast is made.

Both versions fit the models on raw ride counts. The mean baseline predicts the training mean, and persistence predicts the previous day's count. MAE is the average absolute error in rides per day. The before-feature rows come from the frozen starter at `67dd845`, and the after-feature rows come from the final default pipeline. The earlier test suite included a fixed Ridge threshold check. I used validation scores to choose the feature and saved the held-out score comparison for after the feature and model choices were fixed. [Final metrics](reports/metrics.json)

| Feature set | Model | Validation R² | Validation MAE | Test R² | Test MAE |
| --- | --- | ---: | ---: | ---: | ---: |
| Before | `baseline_mean` | -0.9318 | 2002.2 | -2.1441 | 2847.7 |
| Before | `baseline_persistence` | 0.4507 | 900.6 | 0.5099 | 840.1 |
| Before | `ridge` | 0.6475 | 832.9 | 0.5833 | 947.1 |
| Before | `hgb` | 0.2185 | 1296.6 | -0.4975 | 1972.6 |
| After | `baseline_mean` | -0.9318 | 2002.2 | -2.1441 | 2847.7 |
| After | `baseline_persistence` | 0.4507 | 900.6 | 0.5099 | 840.1 |
| After | `ridge` | 0.7187 | 710.3 | 0.6279 | 863.1 |
| After | `hgb` | 0.0711 | 1402.3 | -0.6792 | 2087.9 |

## Headline finding

The leakage demo reached R² 1.0000 because `casual + registered` equals `cnt`. With those columns excluded and dates kept in order, Ridge had the highest test R² at 0.6279, slightly ahead of persistence at 0.5099. HGB's test R² was negative at −0.6792, and it still beat the training-mean baseline on both R² (−2.1441) and MAE (2087.9 versus 2847.7 rides). On 104 of the 184 test days, demand exceeded the training maximum of 6,043 rides, which helps explain why HGB struggled. I kept the seven-day range because it raised Ridge's validation R² by 0.0712 and lowered its MAE by 122.6 rides, even though both HGB scores got worse.

## Exercise 4: target transformation

I tested whether HGB could learn demand relative to its recent level. The training target was the day's count divided by the mean count from the previous seven days (`cnt_roll_7`). To forecast a day, I multiplied the predicted ratio by that day's trailing mean, then computed R² and MAE in ride counts. For both HGB runs I used the same training and validation dates, the same 15 features, and the same model settings and seed.

On validation, the ratio model raised HGB's R² from 0.0711 to 0.7446 and lowered MAE from 1402.3 to 697.0 rides. It also edged out Ridge, which had an R² of 0.7187 and an MAE of 710.3 on the same dates. Mean daily rides rose from 3493.5 in training to 5152.1 in validation. The corresponding mean ratios were 1.0153 and 1.0299, so the relative level stayed closer across the two periods.

I think the ratio is a fair way to forecast one day ahead. Actual counts for the previous week are already known, so the model can use them to adjust its forecast as demand changes. The approach assumes those counts arrive on time and the past week's demand gives a useful scale for tomorrow. I kept it as a separate validation experiment. The final metrics table uses the original ride-count target. [Validation results](reports/exercise4_validation.json) · [Experiment branch](https://github.com/Azi23333/bikeshare-open/tree/exercise4-target-ratio)

## Exercise 5: ridge vs persistence

I would deploy persistence for this daily forecast. Over the 184 test days, its MAE was 840.1 rides, which was 23.0 lower than Ridge's 863.1, and it only needs yesterday's actual count. That is simpler to run and maintain than a fitted Ridge model with 15 inputs. Ridge still has a real advantage if large errors matter more. It had a higher test R² of 0.6279 versus 0.5099, meaning it had lower total squared error on those dates. Ridge also led on both validation metrics at 0.7187 R² and 710.3 MAE, compared with 0.4507 and 900.6 for persistence. For deployment, I give more weight to the lower test MAE and the simpler setup.

## Attribution

I used Claude Code 2.1.325 with Ollama Cloud's `glm-5.3-flash` (about 320B total parameters, 18B active). I kept it for Exercises 1–5 after a `gpt-oss:20b` setup check returned HTTP 402. [Model card](https://ollama.com/library/glm-5.3-flash)

**Agent work**

- Claude Code drafted the `cnt_roll_range_7` calculation in `src/features.py` and the initial `test_roll_range_7_excludes_today()` in `tests/test_leakage.py`.
- It drafted `experiments/target_ratio_validation.py` for the HGB target-ratio experiment.
- It made and repaired the seeded-fault edits in `src/features.py` and produced the peer audit findings in `docs/AUDIT.md`.

Codex helped with implementation and verification. The Agent SDK produced the self-audit in `reports/audit.jsonl`.

**Decisions I made**

- I kept one-day-ahead total rides as the target, used the starter's date split to evaluate on later dates, and kept mean and persistence as simple benchmarks.
- I kept the starter's leakage exclusions, including `casual` and `registered`, which add up to the target.
- I kept the seven-day range because it improved both Ridge validation metrics.
- I kept the HGB target ratio as a separate experiment because the past week's counts are available at forecast time.
- I chose persistence for deployment because it had lower test MAE and only needs yesterday's count.
