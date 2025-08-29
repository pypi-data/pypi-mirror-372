# from datasets import Dataset
# from sklearn.model_selection import train_test_split
# import pandas as pd
# import torch

# # Local application
# from ml_trainer.base import BaseDataset, AbstractModelArchitecture
# from ml_trainer.trainer import BaseTrainer
# from ml_trainer.tasks.task_factory import AbstractTaskFactory
# from ml_trainer.tasks.task_registry import register_task


# class LLMFineTuningDataset(BaseDataset):
#     def __init__(self, tokenizer, system_prompt, config=None, **kwargs):
#         # super().__init__(**kwargs)
#         self.tokenizer = tokenizer
#         self.system_prompt = system_prompt
#         # Fix: Store config properly
#         self.config = config or {}
#         super().__init__(config=self.config, **kwargs)


#     def load_dataset(self):
#         path = self.config.get("source")
#         if not path:
#             raise ValueError("Dataset source path not provided in config")
            
#         df = pd.read_json(path)

#         if "question" not in df.columns or "answer" not in df.columns:
#             raise ValueError("Expected 'question' and 'answer' columns.")

#         train_df, test_df = train_test_split(df, test_size=0.1, random_state=42)

#         def apply_template(question, answer=None):
#             messages = [
#                 {"role": "system", "content": self.system_prompt},
#                 {"role": "user", "content": question}
#             ]
#             if answer:
#                 messages.append({"role": "assistant", "content": answer})
#             return self.tokenizer.apply_chat_template(
#                 messages, tokenize=False, add_generation_prompt=not bool(answer)
#             )

#         train_texts = [apply_template(q, a) for q, a in zip(train_df["question"], train_df["answer"])]
#         test_texts = [apply_template(q) for q in test_df["question"]]

#         self.formatted_dataset = {
#             "train": Dataset.from_dict({"text": train_texts}),
#             "test": Dataset.from_dict({"text": test_texts, "nt": test_texts})
#         }
#         return self.formatted_dataset

# from unsloth import FastLanguageModel, is_bfloat16_supported

# class LLMModel(AbstractModelArchitecture):
#     def __init__(self, model_path, max_seq_length=2048, load_in_4bit=False, setup_lora=True, lora_r=16, lora_alpha=16):
#         self.model_path = model_path
#         self.max_seq_length = max_seq_length
#         self.load_in_4bit = load_in_4bit
#         self.dtype = None
#         self._model_loaded = False
        
#         # Initialize model and tokenizer as None
#         self.model = None
#         self.tokenizer = None
        
#         # Store LoRA config for later use
#         self.setup_lora_flag = setup_lora
#         self.lora_r = lora_r
#         self.lora_alpha = lora_alpha

#     def _load_model_if_needed(self):
#         """Load model only once when needed"""
#         if not self._model_loaded:
#             print(f"Loading model from {self.model_path}...")
            
#             # Load base model
#             self.model, self.tokenizer = FastLanguageModel.from_pretrained(
#                 model_name=self.model_path,
#                 max_seq_length=self.max_seq_length,
#                 dtype=self.dtype,
#                 load_in_4bit=self.load_in_4bit,
#             )
#             print(f"Model loaded with device map: {getattr(self.model, 'hf_device_map', 'Unknown')}")

#             # Set chat template
#             self.tokenizer.chat_template = (
#                 "<|im_start|>system\n{{ system_message }}<|im_end|>\n"
#                 "<|im_start|>user\n{{ user_message }}<|im_end|>\n"
#                 "<|im_start|>assistant\n"
#             )
            
#             # Setup LoRA if requested
#             if self.setup_lora_flag:
#                 self.setup_lora(self.lora_r, self.lora_alpha)
            
#             self._model_loaded = True

#     def setup_lora(self, r=16, lora_alpha=16):
#         """Setup LoRA fine-tuning"""
#         if self.model is None:
#             raise ValueError("Model not loaded yet")
            
#         print("Setting up LoRA fine-tuning...")
#         self.model = FastLanguageModel.get_peft_model(
#             self.model,
#             r=r,
#             target_modules=[
#                 "q_proj", "k_proj", "v_proj", "o_proj",
#                 "gate_proj", "up_proj", "down_proj",
#             ],
#             lora_alpha=lora_alpha,
#             lora_dropout=0,  # 0 is optimized
#             bias="none",     # "none" is optimized
#             use_gradient_checkpointing="unsloth",  # Uses 30% less VRAM
#             random_state=3407,
#             use_rslora=False,  # Rank stabilized LoRA
#             loftq_config=None,  # LoftQ configuration
#         )

#     def prepare_for_inference(self):
#         """Prepare model for inference"""
#         self._load_model_if_needed()
#         FastLanguageModel.for_inference(self.model)

#     def get_tokenizer(self):
#         self._load_model_if_needed()
#         return self.tokenizer

#     def get_model(self):
#         self._load_model_if_needed()
#         return self.model

#     def forward(self, x):
#         self._load_model_if_needed()
#         return self.model(x)

#     def save(self, path):
#         self._load_model_if_needed()
#         self.model.save_pretrained(path)
#         self.tokenizer.save_pretrained(path)

#     def load(self, path):
#         raise NotImplementedError("Loading from checkpoint not yet implemented.")


# from trl import SFTTrainer
# from transformers import TrainingArguments

# class LLMTrainer(BaseTrainer):
#     def __init__(self, model, tokenizer, train_dataset, val_dataset, output_dir, **kwargs):
#         # Store references
#         self.model = model
#         self.tokenizer = tokenizer
        
#         self.trainer = SFTTrainer(
#             model=model,
#             tokenizer=tokenizer,
#             train_dataset=train_dataset,
#             eval_dataset=val_dataset,
#             dataset_text_field="text",
#             max_seq_length=kwargs.get("max_seq_length", 2048),
#             dataset_num_proc=8,
#             packing=True,
#             args=TrainingArguments(
#                 per_device_train_batch_size=kwargs.get("batch_size", 32),
#                 per_device_eval_batch_size=kwargs.get("batch_size", 32),
#                 gradient_accumulation_steps=1,
#                 warmup_steps=kwargs.get("warmup_steps", 10),
#                 num_train_epochs=kwargs.get("epochs", 1),
#                 eval_strategy="steps",
#                 eval_steps=kwargs.get("eval_steps", 0.2),
#                 group_by_length=True,
#                 learning_rate=kwargs.get("learning_rate", 2e-4),
#                 fp16=not is_bfloat16_supported(),
#                 bf16=is_bfloat16_supported(),
#                 logging_steps=10,
#                 optim="adamw_8bit",
#                 weight_decay=kwargs.get("weight_decay", 0.01),
#                 lr_scheduler_type="linear",
#                 output_dir=output_dir,
#                 seed=3407,
#                 report_to=[],
#             )
#         )

#     def training_step(self, batch):
#         pass

#     def validation_step(self, batch):
#         pass

#     def run(self):
#         result = self.trainer.train()
#         # Prepare for inference after training
#         FastLanguageModel.for_inference(self.model)
#         return result


# @register_task("llm_finetuning")
# class LLMTaskFactory(AbstractTaskFactory):
#     def __init__(self):
#         self._model_instance = None  # Cache the model instance
    
#     def create_dataset(self, config):
#         # Create model first to get tokenizer
#         model = self.create_model(config)
#         tokenizer = model.get_tokenizer()

#         # Fix: Pass the correct config structure
#         dataset_config = config.get("dataset_config", {})
#         if "source" not in dataset_config and "source" in config:
#             dataset_config["source"] = config["source"]

#         return LLMFineTuningDataset(
#             tokenizer=tokenizer,
#             system_prompt=config.get("system_prompt", "You are a helpful assistant."),
#             config=dataset_config,
#         )

#     def create_model(self, config):
#         # Return cached model if it exists, otherwise create new one
#         if self._model_instance is None:
#             self._model_instance = LLMModel(
#                 model_path=config["model_path"],
#                 max_seq_length=config.get("max_seq_length", 2048),
#                 load_in_4bit=config.get("load_in_4bit", False),
#                 setup_lora=config.get("setup_lora", True),
#                 lora_r=config.get("lora_r", 16),
#                 lora_alpha=config.get("lora_alpha", 16)
#             )
#         return self._model_instance

#     def create_trainer(self, model, dataset, config):
#         formatted = dataset.load_dataset()
        
#         # Better config handling
#         trainer_config = {
#             "batch_size": config.get("batch_size", 32),
#             "epochs": config.get("epochs", 1),
#             "learning_rate": config.get("learning_rate", 2e-4),
#             "weight_decay": config.get("weight_decay", 0.01),
#             "warmup_steps": config.get("warmup_steps", 10),
#             "eval_steps": config.get("eval_steps", 0.2),
#             "max_seq_length": config.get("max_seq_length", 2048),
#         }

#         return LLMTrainer(
#             model=model.get_model(),
#             tokenizer=model.get_tokenizer(),
#             train_dataset=formatted["train"],
#             val_dataset=formatted["test"],
#             output_dir=config["output_dir"],
#             **trainer_config
#         )