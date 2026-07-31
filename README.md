# UnseenBypass — Detecting Braess-Paradox Roads with Traffic Simulation + ML

**Can we predict which roads, if *removed*, would make traffic *better*?** This project reproduces the counterintuitive **Braess Paradox** in traffic simulation and trains a machine-learning model to predict when it occurs.

## The Braess Paradox

Adding a road to a network can *increase* everyone's travel time, and removing one can *decrease* it — because self-interested drivers overload a tempting shortcut, congesting the whole system. Roads whose removal improves flow are "Braess roads."

## What this project does

1. **Simulation** — builds randomized road networks and simulates traffic using **SUMO** (Simulation of Urban MObility) driven through its **TraCI** Python API.
2. **Counterfactual labeling** — for each network, runs a controlled experiment: remove the candidate edge, re-simulate, and check whether total travel time drops. If it does, the edge is labeled a Braess road.
3. **Dataset generation** — sweeps **1,200 randomized networks** (varying road lengths, speeds, and traffic demand) to build a labeled dataset (~39% Braess).
4. **Machine learning** — trains classifiers (Logistic Regression, Random Forest, Gradient Boosting) to predict Braess roads from *design features alone*, with leakage-aware, cross-validated evaluation.

## Repository contents

| File | Description |
|------|-------------|
| `Braess_Simulation_Analysis.ipynb` | Main analysis: dataset loading, leakage-safe feature selection, cross-validated modeling, interpretation |
| `braess_sweep.py` | Generates the dataset: builds randomized SUMO networks and labels each via edge-removal experiments |
| `make_braess_net.py` | Builds a single classic Braess-diamond network |
| `braess_dataset.csv` | The generated labeled dataset (1,200 networks) |

## Key methodological choices

- **Leakage control** — columns computed from the simulation outcome (`delta`, `baseline_tt`, `no_middle_tt`) are excluded from the model, so reported accuracy reflects genuine predictive skill rather than memorized answers.
- **Stratified cross-validation** — performance is averaged over 5 folds rather than a single split.
- **Interpretability** — feature importances reveal that network *structure* (the length ratio between fast and slow routes) drives the paradox more than raw demand.

## Tech stack

`Python` · `SUMO` / `TraCI` · `pandas` · `scikit-learn` · `matplotlib`

## Reproduce

```bash
pip install eclipse-sumo traci sumolib pandas scikit-learn matplotlib
python braess_sweep.py          # generate braess_dataset.csv
jupyter notebook Braess_Simulation_Analysis.ipynb
```

## Possible extensions

Larger networks imported from OpenStreetMap; multi-edge networks with several Braess candidates; graph neural networks that learn directly from network topology.
