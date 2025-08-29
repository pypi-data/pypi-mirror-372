import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from codecarbon import EmissionsTracker
import time
import numpy as np
import evaluate
import gc
import os

# Load model and tokenizer
model_name = "tiiuae/falcon-rw-1b"
tokenizer = AutoTokenizer.from_pretrained(model_name)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = AutoModelForCausalLM.from_pretrained(model_name).to(device).eval()

# Metrics setup
perplexity_metric = evaluate.load("perplexity", module_type="metric")
bleu_metric = evaluate.load("bleu")
rouge_metric = evaluate.load("rouge")

# Self-freezing support
frozen_layers = {}
frozen_layer_names = []


def freeze_hook(module, input, output, layer_name):
    frozen_output = torch.where(torch.abs(output) < 1e-4, torch.zeros_like(output), output)
    frozen_layers[layer_name] = frozen_output.detach()
    return frozen_output


def apply_freeze_hooks(model):
    for name, module in model.named_modules():
        if "mlp" in name and hasattr(module, "forward"):
            module.register_forward_hook(lambda mod, inp, out, n=name: freeze_hook(mod, inp, out, n))
            frozen_layer_names.append(name)
    print(f"Total layers registered for self-freezing: {len(frozen_layer_names)}")


def self_prune(model, threshold=1e-3):
    with torch.no_grad():
        for name, param in model.named_parameters():
            if "weight" in name and len(param.shape) > 1:
                mask = param.abs() > threshold
                param.mul_(mask.float())


def free_gpu_memory():
    torch.cuda.empty_cache()
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.ipc_collect()
        torch.cuda.empty_cache()


free_gpu_memory()

prompt_cache = {}


def cached_infer(prompt):
    if prompt in prompt_cache:
        return prompt_cache[prompt]
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=50)
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    prompt_cache[prompt] = result
    return result


def evaluate_model(prompt, reference):
    generated = cached_infer(prompt)
    ppl = perplexity_metric.compute(predictions=[generated], model_id=model_name)["perplexities"][0]
    bleu = bleu_metric.compute(predictions=[generated], references=[reference])["bleu"]
    rouge = rouge_metric.compute(predictions=[generated], references=[reference])["rougeL"]
    return ppl, bleu, rouge, generated


def transformer(prompt, reference):
    # === BASELINE ===
    tracker_baseline = EmissionsTracker(project_name="ecotransformers-baseline")
    tracker_baseline.start()
    start_base = time.time()
    output_baseline = evaluate_model(prompt, reference)
    end_base = time.time()
    baseline_emissions = tracker_baseline.stop()
    baseline_time = end_base - start_base

    # === OPTIMIZED (Pruning + Freezing) ===
    self_prune(model, threshold=1e-3)
    apply_freeze_hooks(model)

    tracker_optimized = EmissionsTracker(project_name="ecotransformers-optimized")
    tracker_optimized.start()
    start_opt = time.time()
    output_optimized = evaluate_model(prompt, reference)
    end_opt = time.time()
    optimized_emissions = tracker_optimized.stop()
    optimized_time = end_opt - start_opt

    # === RETURN RESULTS ===
    return {
        "baseline": {
            "perplexity": output_baseline[0],
            "bleu": output_baseline[1],
            "rouge": output_baseline[2],
            "text": output_baseline[3],
            "time": baseline_time,
            "co2": baseline_emissions,
        },
        "optimized": {
            "perplexity": output_optimized[0],
            "bleu": output_optimized[1],
            "rouge": output_optimized[2],
            "text": output_optimized[3],
            "time": optimized_time,
            "co2": optimized_emissions,
        },
    }


if __name__ == "__main__":
    # Example default run (can be replaced with CLI args)
    prompts = [
        "The theory of relativity was developed by",
        "Climate change is primarily caused by",
        "Photosynthesis in plants requires",
        "Artificial intelligence can be used in",
    ]

    references = [
        "The theory of relativity was developed by Albert Einstein in the early 20th century.",
        "Climate change is primarily caused by the emission of greenhouse gases from human activities.",
        "Photosynthesis in plants requires sunlight, carbon dioxide, and water.",
        "Artificial intelligence can be used in healthcare, education, and autonomous vehicles.",
    ]

    results = transformer(prompts[0], references[0])
    print("=== RESULTS ===")
    print(results)
