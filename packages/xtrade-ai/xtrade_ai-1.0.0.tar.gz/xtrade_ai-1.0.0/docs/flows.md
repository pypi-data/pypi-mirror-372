# Flows Guide

See `clients/vendor/xtrade-ai/flow/` for Mermaid diagrams:
- `architecture.mmd`: arsitektur utama dan alur data
- `end_to_end_flowchart.mmd`: flow menyeluruh (training, inference, fine-tune)
- `end_to_end_sequence.mmd`: sequence lengkap antar komponen
- `training_mode.mmd`: sequence pelatihan (tanpa kebocoran)
- `fine_tune_mode.mmd`: sequence fine-tuning
- `action_selection.mmd`: ensemble keputusan
- `monitoring_flow.mmd`: titik capture monitoring

Render (opsional):
```bash
mmdc -i clients/vendor/xtrade-ai/flow/end_to_end_flowchart.mmd -o end_to_end_flowchart.png
```
