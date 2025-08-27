---
sdk: gradio
sdk_version: 5.41.1
app_file: gradio_launcher.py
---
# MedVQA

A CLI tool used for multiple MedVQA competitions:
 [ImageCLEFmed-MEDVQA-GI-2025] (https://github.com/simula/ImageCLEFmed-MEDVQA-GI-2025) and [MediaEval-Medico-2025](https://github.com/simula/MediaEval-Medico-2025).

## Installation

```bash
pip install -U medvqa
```
The library is under heavy development. So, we recommend to always make sure you have the latest version installed.

## Example Usage
Check respective competition repo for detailed submission instructions. For example: 
 [MediaEval-Medico-2025 competition repo](https://github.com/simula/MediaEval-Medico-2025#-submission-system).

```bash
medvqa validate_and_submit --competition=medico-2025 --task=1 --repo_id=...
```
where repo_id is your HuggingFace Model repo id (like SushantGautam/XXModelCheckpoint) with the submission script as required by the competition organizers, for eg, submission_task1.py file for task 1 and submission_task2.py for task 2.