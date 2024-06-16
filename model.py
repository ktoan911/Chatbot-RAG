from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_name = "Qwen/Qwen2-1.5B"

tokenizer = AutoTokenizer.from_pretrained(model_name)
# CPU Enabled uncomment below 👇🏽
# model = AutoModelForCausalLM.from_pretrained("google/gemma-2b-it")
# GPU Enabled use below 👇🏽
model_generation = AutoModelForCausalLM.from_pretrained(
    model_name, device_map='auto' if torch.cuda.is_available() else 'cpu')

if tokenizer.pad_token_id is None:
    tokenizer.pad_token_id = tokenizer.eos_token_id


def generate_text(messages: list, max_length: int = 512):
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(
        'cuda' if torch.cuda.is_available() else 'cpu')

    generated_ids = model_generation.generate(
        model_inputs.input_ids,
        max_new_tokens=max_length
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = tokenizer.batch_decode(
        generated_ids, skip_special_tokens=True)[0]
    return response
