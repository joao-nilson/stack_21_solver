```tack_21_solver/
│
├── src/
│   ├── __init__.py
│   ├── game/
│   │   ├── __init__.py
│   │   ├── game_state.py      # Game state representation                      *
│   │   ├── stack_manager.py   # Stack generation and management                *   
│   │   └── rules.py          # Game rules and validation                       *
│   │
│   ├── algorithms/
│   │   ├── __init__.py
│   │   ├── minimax.py        # Basic minimax implementation                    *
│   │   ├── alphabeta.py      # Alpha-beta pruning implementation               *
│   │   └── solution_tracker.py # Track optimal solution path                   *
│   │
│   ├── visualization/
│   │   ├── __init__.py
│   │   ├── tree_visualizer.py # Game tree visualization                        *
│   │   └── path_visualizer.py # Solution path visualization                    *
│   │
│   └── utils/
│       ├── __init__.py
│       ├── performance.py    # Timing and memory tracking                      *
│       └── logger.py         # Logging setup                                   *
│
├── tests/
│   ├── __init__.py
│   ├── test_game_state.py                                                      *
│   ├── test_minimax.py                                                         *
│   └── test_alphabeta.py                                                       *
│
├── examples/
│   ├── simple_demo.py       # Basic demonstration                              *
│   ├── full_analysis.py     # Complete game analysis                           *
│   └── solution_walkthrough.py # Step-by-step solution                         *
│
├── data/
│   └── sample_stacks.json   # Pre-generated stacks for testing                 *
│
├── requirements.txt                                                            *
├── main.py                  # Main entry point                                 *
└── README.md                                                                   *
```


# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v

# Run example
python examples/solution_walkthrough.py

# Run main solver
python main.py --stack "3,5,2,6,4,1" --algorithm alphabeta --depth-limit 10

# Run simple demonstration
python examples/simple_demo.py

# Run comprehensive analysis
python examples/full_analysis.py

# Run main solver with custom stack
python main.py --stack "3,5,2,6,4,1" --algorithm alphabeta
