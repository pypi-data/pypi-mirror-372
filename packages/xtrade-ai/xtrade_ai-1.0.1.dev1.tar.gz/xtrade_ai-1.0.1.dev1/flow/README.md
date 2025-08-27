# XTrade-AI Flow Diagrams

This directory contains Mermaid diagrams documenting the architecture and modes of the framework.

## Files
- `architecture.mmd`: High-level architecture and data flow
- `end_to_end_flowchart.mmd`: End-to-end flow (training, inference, fine-tune)
- `end_to_end_sequence.mmd`: Detailed sequence across phases (incl. meta-learning)
- `training_mode.mmd`: Training sequence with reward shaping
- `fine_tune_mode.mmd`: Fine-tuning sequence (safe)
- `action_selection.mmd`: Ensemble decision process (policy/TA/risk/close/calibration)
- `monitoring_flow.mmd`: Monitoring capture points and outputs
- `data_pipeline_flow.mmd`: Data pipeline, alignment, scaling, and leakage prevention
- `multi_asset_timeframe_flow.mmd`: Multi-asset/timeframe strategies
- `risk_reward_flow.mmd`: Reward shaping and penalties
- `meta_learning_flow.mmd`: Simulation-driven meta-learning and comparison reports
- `save_persistence_flow.mmd`: Model saving, encryption, and config-driven persistence

## Legend
- Rectangles: components/modules
- Parallelograms: data/artifacts
- Rounded rectangles: decisions/actions
- Dotted arrows: optional/alternate paths

## Render
You can render Mermaid files using VSCode Mermaid preview, GitHub flavored Markdown, or CLI tools such as `mmdc`.

Example (with mermaid-cli):
```bash
mmdc -i architecture.mmd -o architecture.png
mmdc -i end_to_end_flowchart.mmd -o end_to_end_flowchart.png
mmdc -i end_to_end_sequence.mmd -o end_to_end_sequence.png
mmdc -i training_mode.mmd -o training_mode.png
mmdc -i fine_tune_mode.mmd -o fine_tune_mode.png
mmdc -i action_selection.mmd -o action_selection.png
mmdc -i monitoring_flow.mmd -o monitoring_flow.png
mmdc -i data_pipeline_flow.mmd -o data_pipeline_flow.png
mmdc -i multi_asset_timeframe_flow.mmd -o multi_asset_timeframe_flow.png
mmdc -i risk_reward_flow.mmd -o risk_reward_flow.png
mmdc -i meta_learning_flow.mmd -o meta_learning_flow.png
mmdc -i save_persistence_flow.mmd -o save_persistence_flow.png
```
