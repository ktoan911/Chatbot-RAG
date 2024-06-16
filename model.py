from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_name = "Qwen/Qwen2-0.5B"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Load model
model_generation = AutoModelForCausalLM.from_pretrained(model_name).to(device)

if tokenizer.pad_token_id is None:
    tokenizer.pad_token_id = tokenizer.eos_token_id


def generate_text(messages: list, max_length: int = 512):
    # Apply chat template to messages
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    # Tokenize input text and move to the appropriate device
    model_inputs = tokenizer([text], return_tensors="pt").to(device)

    # Generate text with model
    with torch.no_grad():
        generated_ids = model_generation.generate(
            model_inputs.input_ids,
            max_new_tokens=max_length
        )

    # Extract generated text excluding the input tokens
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    # Decode the generated text and return the response
    response = tokenizer.batch_decode(
        generated_ids, skip_special_tokens=True)[0]
    return response
