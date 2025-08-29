# ProcessFlow

A Python package for creating process flow diagrams and BPMN-style workflow visualizations.

## Features

- Create process maps with pools and lanes
- Add various elements: start/end events, tasks, gateways, etc.
- Connect elements with labeled connections
- Export to PNG, SVG, and other formats
- Export to BPMN XML and Draw.io formats
- Customizable themes and styling

## Installation

```bash
pip install processflow
```

## Quick Start

```python
import processflow

# Create a process map
with processflow.ProcessMap(title="Order Processing") as pm:
    # Add a lane
    lane = pm.add_lane("Customer Service")
    
    # Add elements
    start = lane.add_element("Receive Order", processflow.EventType.START)
    task = lane.add_element("Process Order", processflow.ActivityType.TASK)
    end = lane.add_element("Order Complete", processflow.EventType.END)
    
    # Connect elements
    start.connect(task)
    task.connect(end)

# Draw and save
pm.draw()
pm.save("process_diagram.png")
```

## Documentation

For detailed documentation and examples, visit the project repository.

## License

MIT License