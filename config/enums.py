# config/enums.py
from enum import Enum, auto


class AlgorithmType(Enum):
    MINIMAX = "minimax"
    ALPHA_BETA = "alphabeta"


class HeuristicType(Enum):
    CLOSENESS = "closeness"
    AGGRESSIVE = "aggressive"
    CAUTIOUS = "cautious"
    BALANCED = "balanced"
    CUSTOM = "custom"


class StackType(Enum):
    RANDOM = "random"
    BALANCED = "balanced"
    BIASED_HIGH = "biased_high"
    BIASED_LOW = "biased_low"
    ALTERNATING = "alternating"
    INCREASING = "increasing"
    CUSTOM = "custom"


class StackGenerationStrategy(Enum):
    UNIFORM = "uniform"  # All values equally likely
    BIASED = "biased"    # Biased toward certain values
    PATTERNED = "patterned"  # Follows a pattern
    REALISTIC = "realistic"  # Simulates real dice distribution