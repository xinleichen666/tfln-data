"""Fixed seeds and run config for qcnn_protocol. Do not change seeds after a run is locked."""
SEED_DATA = 2408
SEED_INIT = 8701
SEED_TRAIN = 2026
SEED_SPLIT = 42

N_QUBITS = 4
IMG_SIZE = 4  # 4x4 locally generated binary images
N_TRAIN = 96
N_TEST = 48
EPOCHS = 20
LR_Q = 0.12
LR_C = 0.08
BATCH_SIZES = [16, 32]
ENCODINGS = ["angle4", "amplitude"]  # only encodings we actually finish
LOSSES = ["mse", "bce"]  # only losses we actually finish

SIMULATOR_NAME = "numpy_statevector_v1"
PRIOR_ARXIV = "2408.08701"
OPTIMIZER = "SPSA"  # 2-eval/step; fixed seeds
