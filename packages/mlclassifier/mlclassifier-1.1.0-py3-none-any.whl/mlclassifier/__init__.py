from .version import VERSION
from .trainer import ImageClassifierTrainer
# from .utils import ColorFilter
from .ml import ImageClassifier
from typing import Literal

HOG: Literal[1] = 1
ORB: Literal[2] = 2
LBP: Literal[3] = 3
PICK_BEST: Literal[4] = 4

__author_info__ = "Not human."
__other_packages__ = ["sap2assembler", "rbobjecttracking", "vbsoundinference"]
__motive_for_package__ = "I was bored"
__how_i_discovered_this_technique__ = "When i was bored"
__author_age__ = 13
