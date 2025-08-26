import numpy as np
import pandas as pd

STAGES = ["Materials","Manufacturing","Transport","Use","End-of-life"]
PRODUCTS = [f"Product {c}" for c in list("ABCDEFGH")]
REACTANTS = ["Methanol","Ethanol","Ammonia","Toluene"]
PROCESSES = ["Electricity","Heat","Steam cracker"]

_rng = np.random.default_rng(42)
BASE_EF = pd.Series({s: _rng.uniform(0.6,1.8) for s in STAGES}, name="ef")
BASE_ACTIVITY = pd.DataFrame(_rng.uniform(10,100,(len(PRODUCTS),len(STAGES))),
                             index=PRODUCTS, columns=STAGES)
PRODUCT_MAT_SHARES = pd.DataFrame(
    _rng.dirichlet(np.ones(len(REACTANTS)), size=len(PRODUCTS)),
    index=PRODUCTS, columns=REACTANTS
)
MAT_PROC_SHARES = pd.DataFrame(
    _rng.dirichlet(np.ones(len(PROCESSES)), size=len(REACTANTS)),
    index=REACTANTS, columns=PROCESSES
)

def compute_footprint(products: list[str]) -> pd.DataFrame:
    impact = BASE_ACTIVITY.loc[products].mul(BASE_EF, axis=1)
    return (impact.stack().rename("value")
            .rename_axis(["product","stage"]).reset_index())