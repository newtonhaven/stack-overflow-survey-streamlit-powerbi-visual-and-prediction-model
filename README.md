# Stack Overflow Survey — Power BI visual & prediction model

This repository contains a Power BI project and an accompanying prediction model built from the Stack Overflow Developer Survey 2024 data. The repository includes the Power BI report file, exported project PDF, a project report PDF, and a Jupyter notebook used for the prediction model.

## Files of interest
- `ProjeST.pbix` — Power BI report (Power BI Desktop file).
- `ProjeST.pdf` — Exported PDF of the Power BI report (embedded below).
- `Stack Overflow Developer Survey 2024 – Power BI Project Report.pdf` — Written project report (embedded below).
- `PredictionModel.ipynb` — Jupyter notebook with the prediction model and experiments.

## How to view

1. PDF: contains pages of PowerBI.
2. Power BI: open `ProjeST.pbix` with Power BI Desktop (Windows).

---

## Project report (Power BI)

<iframe src="ProjeST.pdf" width="100%" height="600px">This browser does not support embedded PDFs. You can download the file directly: <a href="ProjeST.pdf">Download ProjeST.pdf</a>.</iframe>

---

## Prediction model

The `PredictionModel.ipynb` notebook contains the data-preparation steps, model training, and evaluation used to predict outcomes from the Stack Overflow survey data. Open it with Jupyter or VS Code's notebook support.


![notebook](https://img.shields.io/badge/notebook-Jupyter-orange)

## Notebook summary
The `PredictionModel.ipynb` notebook contains the model pipeline and experiments used to predict annual developer compensation from the Stack Overflow survey. Main sections:

- Lib Imports — Import standard data science libraries and configure warnings.
- Data Fetch — (Optional) download dataset with `kagglehub` and load the CSV.
- Basic Data Clean — Selects relevant columns and filters salary outliers.
- Feature Preprocessing | Data Augmentation — Convert and simplify features (experience, education, dev type, country, employment) and keep top countries.
- Pipe Line — Build preprocessing pipelines (imputation, scaling, one-hot encoding) and a GradientBoostingRegressor; includes evaluation and plotting helpers plus a `main` runner.
- Model Run — Calls `main(df)` to execute the full training/evaluation flow.

### Quick start (run the notebook)
1. You can easily run model on [Google Colab](https://colab.research.google.com/drive/1Csb408I8FLWqtjWbjY59pQBRL6olaucD?usp=sharing).
