# Submitted Phase 1 verification (v3)

Verified on 2026-11-03 using the user's uploaded `GE2340 Phase 1.zip`, containing `Phase1_Proposal.pdf`.

- PDF page 1 explicitly defines mean squared error, L(theta) = (1/N) sum((theta^T x_i - y_i)^2), and sets its derivative to zero. The implemented squared-error OLS is consistent with this specification. No L1-to-OLS change is needed.
- Page 1 already notes fixed-sum collinearity and that correlation is not causation. The reference-feature OLS parameterization handles that fixed sum; all five inputs remain in shared datasets.
- Page 1 specifies MAE/RMSE/R2 and Accuracy/Macro-F1. Value success is MAE(model) < MAE(mean baseline); grade success is Macro-F1(model) > Macro-F1(majority baseline).
- Page 2 names A/B/C/D/F but gives no numeric boundaries. The user-selected training-only quintile definition remains project-defined, not official grading.
- The user-uploaded ZIP name and 170227-byte size match the Canvas record reported during verification. Canvas's original attachment bytes were not retrieved for hash comparison; this is not proof of byte-for-byte identity with Canvas.
- Uploaded ZIP SHA256: 5bc9ed545c116430dcbddd26d3078f840fef731157f8d020d84b144060595d55
- Extracted proposal PDF SHA256: 790cc5a42dc6a6c759844d4fdcd6b709294f92ffb0a86e9cf1e70e5ced8becd9

The source upload contains team personal details and is not redistributed in this technical data package. Earlier versions' provisional-loss warning was based on a different live document and is superseded by this submitted-PDF evidence. V3 changes documentation and model metadata only; data, splits, labels, predictions and numerical metrics remain unchanged from v2.
