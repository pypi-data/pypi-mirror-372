from .utils import get_outer_directory
import os

SRC_PATH = get_outer_directory(os.path.dirname(__file__), 2)
LIB_PATH = get_outer_directory(os.path.dirname(__file__))
DOCS_PATH = os.path.join(SRC_PATH, "docs")
IMG_PATH = os.path.join(DOCS_PATH, "img")

DEFAULT_GRAPH_ATTRIBUTES = {
    "nodesep": "1",
    "ranksep": "1",
    "label": "",
    "fontsize": "16",
}

SEC_PER_DAY = 86400
G_PER_KG = 1000
KG_PER_TON = 1000
LIT_PER_M3 = 1000
SEC_PER_MIN = 60
SEC_PER_HOUR = 3600

D0_TOWER_VOLUME = 316  # m3
OEP_TOWER_VOLUME = 758  # m3
D1_TOWER_VOLUME = 1116  # m3
D2_TOWER_VOLUME = 1116  # m3

TRAIN_RATE = 0.7
VALIDATION_RATE = 0.15
TEST_RATE = 0.15

NUM_HIDDEN_NEURONS = 64
ACTIVATION_FUNCTION = "tanh"
DROP_RATE = 0
TRAIN_RATE = 0.7
VALIDATION_RATE = 0.15
OPTIMIZER = "adam"
LOSS = "mse"
LEARNING_RATE = 0.001
BATCH_SIZE = 32
EPOCHS = 50
PATIENCE = 5

COLOR_MAP = {
    "blue": {"color": "#1f77b4", "linestyle": "-", "marker": "o"},
    "light_blue": {"color": "#aec7e8", "linestyle": "--", "marker": "s"},
    "orange": {"color": "#ff7f0e", "linestyle": "-.", "marker": "D"},
    "light_orange": {"color": "#ffbb78", "linestyle": ":", "marker": "^"},
    "green": {"color": "#2ca02c", "linestyle": "-", "marker": "v"},
    "light_green": {"color": "#98df8a", "linestyle": "--", "marker": "<"},
    "red": {"color": "#d62728", "linestyle": "-.", "marker": ">"},
    "light_red": {"color": "#ff9896", "linestyle": ":", "marker": "p"},
    "purple": {"color": "#9467bd", "linestyle": "-", "marker": "*"},
    "light_purple": {"color": "#c5b0d5", "linestyle": "--", "marker": "h"},
    "brown": {"color": "#8c564b", "linestyle": "-.", "marker": "H"},
    "light_brown": {"color": "#c49c94", "linestyle": ":", "marker": "X"},
    "pink": {"color": "#e377c2", "linestyle": "-", "marker": "d"},
    "light_pink": {"color": "#f7b6d2", "linestyle": "--", "marker": "8"},
    "gray": {"color": "#7f7f7f", "linestyle": "-.", "marker": "+"},
    "light_gray": {"color": "#c7c7c7", "linestyle": ":", "marker": "x"},
    "olive": {"color": "#bcbd22", "linestyle": "-", "marker": "|"},
    "light_olive": {"color": "#dbdb8d", "linestyle": "--", "marker": "_"},
    "cyan": {"color": "#17becf", "linestyle": "-.", "marker": "1"},
    "light_cyan": {"color": "#9edae5", "linestyle": ":", "marker": "2"},
}
