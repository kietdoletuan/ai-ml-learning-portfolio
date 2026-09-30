# Defect Detector

## 1. Overview
A personal project defect detector trained to detect defects in a type of bolt using self-captured images of products from real machine components.
The detector can be accessed through Streamlit Community Cloud, and currently, it supports one bolt configuration.
## 2. Shared Inspection System
### PatchCore
The model used here is PatchCore, which uses a pretrained feature extractor to obtain normal patch features. These are retained in a "memory bank" so that at inference time, new patches are then compared with the saved normal memory to calculate the anomaly score - the more unfamiliar the patches, the higher the anomaly score they receive. 
### Part Configurations and Inference Flow
At app startup, `.yaml` files each containing a component type's configuration are validated and loaded into a registry. Once inputs are submitted, an Engine receives the part ID and performs a lookup in the registry.
To make a prediction, the Engine must first validate its inputs and corresponding model status. After validations are through, the appropriate checkpoint is loaded to score views and produce an anomaly map. `aggregate.py` makes the final verdict based on whether the highest anomaly view score is greater than the part's threshold. The result consisting of a summary table and an image of the anomaly map is then prepared by `service.py` before being displayed through `app.py`.
## 3. Supported Parts and Data
| Part / view | Status | Configuration |
| --- | --- | --- | 
| Bolt | Live | 2-3 views |

### Bolt Image Collection

| Group | Physical parts | Images | Views per part | Role |
| --- | ---: | ---: | --- | --- |
| Normal bolts | 47 | 141 | 3 | Training |
| Separate normal bolts | 24 | 48 | 2 | Evaluation; Threshold Selection |
| Surface defective bolts | 14 | 41 | 2-3 | Evaluation |
| Thread defective bolts | 13 | 39 | 3 | Evaluation |
### Evaluation Protocol
- Views are grouped by physical part (labeled p01, p02, p03, ...)
- A part is assumed to be defective if its maximum view anomaly score is greater than 12.38
## 4. Results
### Bolt: Frame-Level AUROC
| Images compared | Normal Images | Defect Images | AUROC | 
| --- | ---: | ---: | --- |
| Normal vs surface defect | 48 | 41 | 0.988 |
| Normal vs thread defect | 48 | 39 | 0.819 |
### Bolt: Part-Level Decisions
| Evaluation group | Outcome | Rate | 95% Wilson interval | 
| --- | ---: | ---: | --- |
| False positive | 1/24 | 4.2% | 0.7-20.2% |
| Surface defective parts caught | 14/14 | 100% | 78.5-100% |
| Thread defective parts caught | 12/13 | 92.3% | 66.7-98.6% |
- The model's threshold `12.38` was chosen with the 24 separate normal held-out set.
## 5. Live App
[Try the live app](https://kietdo-defect-detector.streamlit.app/)
## 6. Limitations, Design Decisions, and Next Steps
- Due to difficulties with obtaining normal and defect samples without disrupting production, the data volume per component can be modest.
- PaDiM was originally chosen for this defect detection problem. However, it is unsuitable for the obtained amount of data and configuration (`03_padim_bolt.ipynb`).