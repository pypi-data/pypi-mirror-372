from transformers import AutoModelForCausalLM
from datasets import load_dataset, Image as HfImage
from transformers import AutoProcessor
import torch
import json
import time
from tqdm import tqdm
import subprocess
import platform
import sys

from evaluate import load

bleu = load("bleu")
rouge = load("rouge")
meteor = load("meteor")


ds = load_dataset("SimulaMet/Kvasir-VQA-x1")["test"]
ds_shuffled = ds.shuffle(seed=42) # Shuffle with fixed seed for reproducibility
val_dataset = ds_shuffled.select(range(1500)) # Select first 1500 after shuffle
val_dataset = val_dataset.cast_column("image", HfImage())
predictions = []  # List to store predictions

gpu_name = torch.cuda.get_device_name(
    0) if torch.cuda.is_available() else "cpu"
device = "cuda" if torch.cuda.is_available() else "cpu"


def get_mem(): return torch.cuda.memory_allocated(device) / \
    (1024 ** 2) if torch.cuda.is_available() else 0


initial_mem = get_mem()

# ✏️✏️--------EDIT SECTION 1: SUBMISISON DETAILS and MODEL LOADING --------✏️✏️#

SUBMISSION_INFO = {
    # 🔹 TODO: PARTICIPANTS MUST ADD PROPER SUBMISSION INFO FOR THE SUBMISSION 🔹
    # This will be visible to the organizers
    # DONT change the keys, only add your info
    "Participant_Names": "Sushant Gautam, Steven Hicks and Vajita Thambawita",
    "Affiliations": "SimulaMet",
    "Contact_emails": ["sushant@simula.no", "steven@simula.no"],
    # But, the first email only will be used for correspondance
    "Team_Name": "SimulaMetmedVQA Rangers",
    "Country": "Norway",
    "Notes_to_organizers": '''
        eg, We have finetund XXX model
        This is optional . .
        Used data augmentations . .
        Custom info about the model . .
        Any insights. .
        + Any informal things you like to share about this submission.
        '''
}
# 🔹 TODO: PARTICIPANTS MUST LOAD THEIR MODEL HERE, EDIT AS NECESSARY FOR YOUR MODEL 🔹
# can add necessary library imports here

model_hf = AutoModelForCausalLM.from_pretrained(
    "SushantGautam/Florence-2-vqa-demo", trust_remote_code=True).to(device)
processor = AutoProcessor.from_pretrained(
    "microsoft/Florence-2-base-ft", trust_remote_code=True)

model_hf.eval()  # Ensure model is in evaluation mode
# 🏁----------------END  SUBMISISON DETAILS and MODEL LOADING -----------------🏁#

start_time, post_model_mem = time.time(), get_mem()
total_time, final_mem = round(
    time.time() - start_time, 4), round(get_mem() - post_model_mem, 2)
model_mem_used = round(post_model_mem - initial_mem, 2)

for idx, ex in enumerate(tqdm(val_dataset, desc="Validating")):
    question = ex["question"]
    image = ex["image"].convert(
        "RGB") if ex["image"].mode != "RGB" else ex["image"]
    # you have access to 'question' and 'image' variables for each example

# ✏️✏️___________EDIT SECTION 2: ANSWER GENERATION___________✏️✏️#
    # 🔹 TODO: PARTICIPANTS CAN MODIFY THIS TOKENIZATION STEP IF NEEDED 🔹
    inputs = processor(text=[question], images=[image],
                       return_tensors="pt", padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()
              if k not in ['labels', 'attention_mask']}

    # 🔹 TODO: PARTICIPANTS CAN MODIFY THE GENERATION AND DECODING METHOD HERE 🔹
    with torch.no_grad():
        output = model_hf.generate(**inputs)
    answer = processor.tokenizer.decode(output[0], skip_special_tokens=True)
    # make sure 'answer' variable will hold answer (sentence/word) as str
# 🏁________________ END ANSWER GENERATION ________________🏁#

# ⛔ DO NOT EDIT any lines below from here, can edit only upto decoding step above as required. ⛔
    # Ensures answer is a string
    assert isinstance(
        answer, str), f"Generated answer at index {idx} is not a string"
    # Appends prediction
    predictions.append(
        {"index": idx, "img_id": ex["img_id"], "question": ex["question"], "answer": answer})

# Ensure all predictions match dataset length
assert len(predictions) == len(
    val_dataset), "Mismatch between predictions and dataset length"

total_time, final_mem = round(
    time.time() - start_time, 4), round(get_mem() - post_model_mem, 2)
model_mem_used = round(post_model_mem - initial_mem, 2)

# caulcualtes metrics
references = [[e] for e in val_dataset['answer']]
preds = [pred['answer'] for pred in predictions]

bleu_result = bleu.compute(predictions=preds, references=references)
rouge_result = rouge.compute(predictions=preds, references=references)
meteor_result = meteor.compute(predictions=preds, references=references)
bleu_score = round(bleu_result['bleu'], 2)
rouge1_score = round(float(rouge_result['rouge1']), 2)
rouge2_score = round(float(rouge_result['rouge2']), 2)
rougeL_score = round(float(rouge_result['rougeL']), 2)
meteor_score = round(float(meteor_result['meteor']), 2)

public_scores = {
    'bleu': bleu_score,
    'rouge1': rouge1_score,
    'rouge2': rouge2_score,
    'rougeL': rougeL_score,
    'meteor': meteor_score
}
print("✨Public scores: ", public_scores)

# Saves predictions to a JSON file

output_data = {"submission_info": SUBMISSION_INFO, "public_scores": public_scores,
               "predictions": predictions, "total_time": total_time, "time_per_item": total_time / len(val_dataset),
               "memory_used_mb": final_mem, "model_memory_mb": model_mem_used, "gpu_name": gpu_name,
               "debug": {
                   "packages": json.loads(subprocess.check_output([sys.executable, "-m", "pip", "list", "--format=json"])),
                   "system": {
                       "python": platform.python_version(),
                       "os": platform.system(),
                       "platform": platform.platform(),
                       "arch": platform.machine()
                   }}}


with open("predictions_1.json", "w") as f:
    json.dump(output_data, f, indent=4)
print(f"Time: {total_time}s | Mem: {final_mem}MB | Model Load Mem: {model_mem_used}MB | GPU: {gpu_name}")
print("✅ Scripts Looks Good! Generation process completed successfully. Results saved to 'predictions_1.json'.")
print("Next Step:\n 1) Upload this submission_task1.py script file to HuggingFace model repository.")
print('''\n 2) Make a submission to the competition:\n Run:: medvqa validate_and_submit --competition=medico-2025 --task=1 --repo_id=...''')
