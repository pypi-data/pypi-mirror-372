# sparse_mil/sawmil.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Sequence, List, Tuple
import numpy as np
import numpy.typing as npt

from .bag import Bag, BagDataset
from .smil import sMIL
from .svm import SVM
from .kernels import KernelType

@dataclass
class sAwMIL:
    """
    Sparse-Aware MIL (two-stage):
      Stage 1 (bag-level):  sMIL scores instances by treating each instance as a singleton bag.
      Stage 2 (instance-level): label top-η fraction of positive-bag instances as +1
        (but ONLY those with intra_bag_labels==1). Others are −1. Train a standard SVM.
      Prediction (bag-level): max over instance decision scores in each bag.

    Parameters
    ----------
    C : float
        Regularization for both stages (effective C in sMIL still uses its scaling).
    base_kernel : KernelType
        Single-instance kernel spec for both stages ("linear", "rbf", etc., or a BaseKernel).
    gamma, degree, coef0 : Optional[float]/int
        Kernel hyperparameters for instance kernels.
    eta : float
        Fraction of positive-bag instances to tag as positive in stage 2 (0 < eta ≤ 1).
        We also ensure at least `num_pos_bags` positives (classic sbMIL heuristic).
    min_pos_ratio : float
        If after applying intra_bag_labels fewer than this ratio of positives are chosen,
        we fall back to ignoring intra labels for selection (choose top-n regardless of mask).
    scale_C : bool
        Passed into sMIL (stage 1) to scale its per-block C as in the paper/code.
        Stage 2 uses unscaled C on instances (simple & effective).
    tol, verbose : standard SVM tolerances/verbosity.

    Notes
    -----
    - For sMIL stage we strongly recommend bag kernel `normalizer="none"` and
      `use_intra_labels=False` to avoid double-averaging; set via smil_normalizer/use_intra_labels.
    - Stage 2 uses the *instance* SVM, so only the single-instance kernel matters there.
    """
    C: float = 1.0
    base_kernel: KernelType = "linear"
    gamma: Optional[float] = None
    degree: Optional[int] = 3
    coef0: Optional[float] = 0.0

    # selection + fallback knobs
    eta: float = 0.1
    min_pos_ratio: float = 0.05

    # Stage-1 (sMIL) bag-kernel knobs
    smil_normalizer: str = "none"
    smil_use_intra_labels: bool = False
    smil_p: float = 1.0
    smil_fast_linear: bool = True
    scale_C: bool = True

    # solver / numerics
    tol: float = 1e-6
    verbose: bool = False

    # (optional) pass-through gurobi env/params if you wired quadprog to accept them
    _gurobi_env: object | None = None
    _gurobi_params: dict | None = None

    # fitted artifacts
    smil_: sMIL | None = None
    sil_: SVM | None = None

    # ---------- utilities ----------
    @staticmethod
    def _coerce_bags(bags: Sequence[Bag] | BagDataset | Sequence[np.ndarray],
                     y: Optional[npt.NDArray[np.float64]] = None) -> List[Bag]:
        if isinstance(bags, BagDataset):
            return list(bags.bags)
        if len(bags) > 0 and isinstance(bags[0], Bag):  # type: ignore[index]
            return list(bags)  # type: ignore[return-value]
        if y is None:
            raise ValueError("When passing raw arrays for bags, you must also pass y.")
        return [Bag(X=np.asarray(b, dtype=float), y=float(lbl)) for b, lbl in zip(bags, y)]

    @staticmethod
    def _flatten_instances(ds: List[Bag]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Returns:
            X_all   : (N, d) all instances in all bags
            y_bag   : (N,) bag label of each instance (0/1 or -1/+1 as in input)
            mask    : (N,) intra_bag_label (0/1) for each instance
            bag_idx : (N,) index of parent bag per instance
        """
        Xs, ys, ms, bi = [], [], [], []
        for i, b in enumerate(ds):
            if b.n == 0:
                continue
            Xs.append(b.X)
            ys.append(np.full(b.n, float(b.y), dtype=float))
            ms.append(b.mask.astype(float))
            bi.append(np.full(b.n, i, dtype=int))
        if not Xs:
            return (np.zeros((0, 0)), np.zeros((0,)), np.zeros((0,)), np.zeros((0,), dtype=int))
        return (np.vstack(Xs),
                np.concatenate(ys),
                np.concatenate(ms),
                np.concatenate(bi))

    @staticmethod
    def _singletonize(X: np.ndarray, y: float) -> List[Bag]:
        return [Bag(X=X[j:j+1, :], y=y) for j in range(X.shape[0])]

    # ---------- core ----------
    def fit(self,
            bags: Sequence[Bag] | BagDataset | Sequence[np.ndarray],
            y: Optional[npt.NDArray[np.float64]] = None) -> "sAwMIL":
        # 0) input
        blist = self._coerce_bags(bags, y)
        if len(blist) == 0:
            raise ValueError("No bags provided.")

        # 1) Stage 1: sMIL on (neg singletons vs pos bags)
        smil = sMIL(
            C=self.C,
            base_kernel=self.base_kernel,
            gamma=self.gamma,
            degree=self.degree,
            coef0=self.coef0,
            normalizer=self.smil_normalizer,
            p=self.smil_p,
            use_intra_labels=self.smil_use_intra_labels,
            fast_linear=self.smil_fast_linear,
            scale_C=self.scale_C,
            tol=self.tol,
            verbose=self.verbose,
        )
        # forward gurobi env/params if present
        if self._gurobi_env is not None:
            setattr(smil, "_gurobi_env", self._gurobi_env)
        if self._gurobi_params is not None:
            setattr(smil, "_gurobi_params", self._gurobi_params)

        smil.fit(blist)
        self.smil_ = smil

        # 2) Build instance universe
        X_all, y_bag, mask, bag_idx = self._flatten_instances(blist)
        if X_all.shape[0] == 0:
            # degenerate
            self.sil_ = SVM(C=self.C, kernel="linear")
            self.sil_.coef_, self.sil_.intercept_ = np.zeros((blist[0].d,)), 0.0
            return self

        # split pos/neg by bag label > 0
        pos_inst = (y_bag > 0)
        X_pos = X_all[pos_inst]
        mask_pos = mask[pos_inst]
        X_neg = X_all[~pos_inst]

        # 3) Score ALL positive-bag instances with sMIL by treating each as a singleton bag
        pos_singletons = self._singletonize(X_pos, y=+1.0)
        # sMIL decision on singleton bags == instance scores under stage-1 model
        f_pos = smil.decision_function(pos_singletons).ravel()

        # 4) Choose top-η positives, but only those allowed by intra bag labels
        L_p = X_pos.shape[0]
        B_p = sum(1 for b in blist if float(b.y) > 0.0)
        n_select = max(B_p, int(round(self.eta * L_p)))
        n_select = min(max(n_select, 1), L_p)

        # nth largest cutoff
        order = np.argsort(-f_pos)  # descending
        cutoff = f_pos[order[n_select - 1]]
        take = f_pos >= cutoff  # boolean over positive instances
        # apply intra-bag constraint: only keep those with mask==1
        chosen = take & (mask_pos >= 0.5)

        # fallback: if too few chosen, ignore intra labels (classic sbMIL fallback)
        if chosen.sum() < max(1, int(self.min_pos_ratio * L_p)):
            chosen = take

        self.cutoff_ = float(cutoff)
        self.selected_mask_ = chosen.copy()

        # 5) Build SIL training set
        y_pos = np.full(L_p, -1.0, dtype=float)
        y_pos[chosen] = +1.0
        X_sil = np.vstack([X_neg, X_pos])
        y_sil = np.hstack([-np.ones(X_neg.shape[0], dtype=float), y_pos])

        # 6) Train instance SVM
        sil = SVM(
            C=self.C,
            kernel=self.base_kernel,
            gamma=self.gamma,
            degree=self.degree,
            coef0=self.coef0,
            tol=self.tol,
            verbose=self.verbose,
        )
        if self._gurobi_env is not None:
            setattr(sil, "_gurobi_env", self._gurobi_env)
        if self._gurobi_params is not None:
            setattr(sil, "_gurobi_params", self._gurobi_params)
        sil.fit(X_sil, y_sil)
        self.sil_ = sil
        return self

    # ---------- inference ----------
    def _decision_instances(self, X: np.ndarray) -> np.ndarray:
        if self.sil_ is None:
            raise RuntimeError("sAwMIL is not fitted.")
        # Instance-level decision values
        return self.sil_.decision_function(X).ravel()

    def decision_function(self, bags: Sequence[Bag] | BagDataset | Sequence[np.ndarray]) -> npt.NDArray[np.float64]:
        blist = self._coerce_bags(bags)
        if self.sil_ is None:
            raise RuntimeError("sAwMIL is not fitted.")
        # MIL assumption: bag score = max instance score
        scores = np.empty(len(blist), dtype=float)
        for i, b in enumerate(blist):
            if b.n == 0:
                scores[i] = float(self.sil_.intercept_) if self.sil_.intercept_ is not None else 0.0
            else:
                s = self._decision_instances(b.X)
                scores[i] = float(np.max(s))
        return scores

    def predict(self, bags: Sequence[Bag] | BagDataset | Sequence[np.ndarray]) -> npt.NDArray[np.float64]:
        # Map sign to original bag labels {classes_[0], classes_[1]} is not tracked here,
        # so we default to {0,1} mapping by threshold at 0.
        s = self.decision_function(bags)
        return (s >= 0.0).astype(float)

    def score(self, bags, y_true) -> float:
        y_pred = self.predict(bags)
        y_true = np.asarray([b.y for b in bags.bags], dtype=float) if isinstance(bags, BagDataset) \
                 else (np.asarray([b.y for b in bags], dtype=float) if len(bags) and isinstance(bags[0], Bag) \
                       else np.asarray(y_true, dtype=float))
        return float((y_pred == y_true).mean())
