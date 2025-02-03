#Llama-3.2-3b fine-tuning

from datasets import load_dataset

def formatting_prompts_func(examples):
    eos_token = '<|end_of_text|>' 	
    korQuAD_prompt = """		  	
        ### Question:
        {}

        ### Context:
        {}

        ### Answer:
        {}
    """
	
    instructions = examples["question"]
    inputs = examples["context"]
    outputs = [item['text'][0] for item in examples["answers"]]
    texts = []
	
    for instruction, input, output in zip(instructions, inputs, outputs):
        text = korQuAD_prompt.format(instruction, input, output) + eos_token
        texts.append(text)

    return {"text": texts}

dataset = load_dataset("KorQuAD/squad_kor_v1", split = "train")
dataset = dataset.map(
    formatting_prompts_func,
    batched=True,        
)
print(dataset[:1])

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TrainingArguments
)
import torch
from peft import prepare_model_for_kbit_training, LoraConfig, get_peft_model
from trl import SFTTrainer

model_path = "meta-llama/Llama-3.2-3B-Instruct"

model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)
tokenizer = AutoTokenizer.from_pretrained(
              model_path              
              )
tokenizer.pad_token = '<|end_of_text|>'

model = prepare_model_for_kbit_training(model)


# LoRA 설정
lora_config = LoraConfig(
    r=16,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "down_proj", "up_proj"],
    lora_dropout=0.01,
    bias="none",
    task_type="CAUSAL_LM",
)

# LoRA 적용
model = get_peft_model(model, lora_config)


training_params = TrainingArguments(
    output_dir="./results3_korquad",
    num_train_epochs=3,	
    per_device_train_batch_size=1,	
    gradient_accumulation_steps=1,	
    optim="paged_adamw_32bit",
    save_steps=10000,
    logging_steps=25,
    learning_rate=2e-4,
    weight_decay=0.001,
    fp16=False,
    bf16=False,
    max_grad_norm=0.3,
    max_steps=-1,
    warmup_ratio=0.03,
    group_by_length=True,
    lr_scheduler_type="constant",
)
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    peft_config=lora_config,
    tokenizer=tokenizer,
    args=training_params
)

trainer.train()
ADAPTER_MODEL = "lora_adapter_korquad"
trainer.model.save_pretrained(ADAPTER_MODEL)

