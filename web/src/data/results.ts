// Frozen evaluation results, copied from ml/reports/results.md (development)
// and ml/reports/holdout.md (holdout). Both were produced under the protocol
// frozen in commit fde3026 and do not change.
// MAE = mean absolute error of the 12-month change, in percentage points.

export type ModelKey = "noChange" | "momentum" | "histMean" | "ridge" | "gbm" | "mlp";

export const BASELINES: ModelKey[] = ["noChange", "momentum", "histMean"];

export const DEV_MAE: Record<ModelKey, number> = {
  momentum: 3.35,
  noChange: 3.63,
  gbm: 3.66,
  histMean: 4.44,
  ridge: 4.72,
  mlp: 5.56,
};

export const HOLDOUT_MAE: Record<ModelKey, number> = {
  momentum: 3.4,
  ridge: 6.05,
  gbm: 6.24,
  histMean: 6.74,
  noChange: 7.51,
  mlp: 7.72,
};
