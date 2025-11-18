# AiiDA Human-in-the-Loop

An AiiDA plugin demonstrating human-in-the-loop workflows that pause and wait for user input before continuing execution.

## Overview

This plugin provides a `HumanLoopWorkChain` that implements a simple number-guessing game to demonstrate how AiiDA workflows can pause execution, request human input, and resume based on that input.
This pattern is useful for workflows that require human decision-making, validation, or intervention at specific points.

## Features

- Pause workflow execution at specified points
- Request user input via workflow extras
- Resume execution after receiving input
- Track interaction history
- Configurable maximum iterations

## Installation

```bash
git clone https://github.com/GeigerJ2/aiida-human-in-the-loop.git
cd aiida-human-in-the-loop
pip install -e .
```

## Usage

### Basic Example

```python
from aiida_humanintheloop import HumanLoopWorkChain
from aiida.orm import Int
from aiida.engine import submit

# Submit the workflow
node = submit(HumanLoopWorkChain, max_iters=Int(10))
print(f"Submitted workflow with PK={node.pk}")
```

### Interacting with the Workflow

The workflow pauses and stores questions in the node's extras. To interact:

```python
from aiida.orm import load_node
from aiida.engine.processes import control

# Load the paused workflow
wf = load_node(PK)  # Replace PK with your workflow's PK

# Read the question
question = wf.base.extras.get('question')
print(f"Question: {question}")

# Provide your answer
wf.base.extras.set('answer', '42')

# Resume the workflow
control.play_processes([wf])
```

### Automated Interaction

See `examples/auto_guess.py` for a script that automatically interacts with a running workflow.

## How It Works

1. The workflow generates a random number and asks the user to guess it
2. The workflow pauses using `self.pause()`
3. The question is stored in `node.base.extras['question']`
4. User provides answer via `node.base.extras['answer']`
5. When resumed, the workflow processes the answer and provides feedback
6. The loop continues until the correct number is guessed or max iterations reached

## Entry Points

The plugin registers the following AiiDA workflow entry point:

- `humanintheloop.humanloop` → `HumanLoopWorkChain`

## Requirements

- `aiida-core >= 2.5`

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Acknowledgments

This plugin was originally developed by [Giovanni Pizzi](https://github.com/giovannipizzi) as an example of human-in-the-loop workflows in AiiDA.

## Contact

For questions or support, please contact the AiiDA team.
