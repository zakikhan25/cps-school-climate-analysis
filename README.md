# CPS School Climate & Attendance Analysis

A data project built around the skills in the CPS Data Strategist posting:
writing analysis code, statistics on multicolumn public data, data quality
checks, and training non-technical audiences to use data.

**Data:** Chicago Public Schools School Progress Reports, from the Chicago Data Portal (dataset 2dn2-x66j). Public, school-level, no student records.
Landing page: https://data.cityofchicago.org/d/2dn2-x66j

## What's here
| File | Purpose |
|---|---|
| `analysis.py` | Python (pandas, scipy, statsmodels): cleaning, data quality log, correlations, regression, charts |
| `analysis.sas` | The same analysis in SAS, for the "use or learn SAS" requirement. **Untested.** |
| `training_guide.md` | 30-minute workshop plan, handout, and feedback survey for non-technical staff |
| `requirements.txt` | Python packages |

## Run it
```
pip install -r requirements.txt
python analysis.py
```
Results and charts land in `outputs/`. If the download fails, save the CSV from the landing page and run `python analysis.py yourfile.csv`.

For SAS, create a free account at SAS OnDemand for Academics, upload `analysis.sas`, run it, and read the log.

## Status of the code
- `analysis.py` ran successfully on a synthetic test file with the same columns. **It has not been run on the real CPS file yet.** If a column name differs, the script will error and tell you which one.
- `analysis.sas` has not been run at all.
- No real findings exist yet. Run it, then read `outputs/summary.txt`.
