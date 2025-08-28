import os

from transformers import AutoTokenizer, AutoModelForCausalLM

import torch

# DEFAULT_MODELS = {
#     "llama": "meta-llama/Llama-2-7b-chat-hf",
#     "mistral": "mistralai/Mistral-7B-v0.1",
#     "falcon": "tiiuae/falcon-7b-instruct",
#     "gptj": "EleutherAI/gpt-j-6B"
# }


import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class HFClient:
    def __init__(self, model_name="llama", device=None, base_url = None, api_key=None, seed = None):
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        self.model_name=model_name
        self.model, self.tokenizer = self._initialize_model()

    def _initialize_model(self):
        tokenizer = AutoTokenizer.from_pretrained(
            self.model_name, trust_remote_code=True
        )
        model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            trust_remote_code=True,
            device_map="auto" if self.device == "cuda" else None
        )

        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        # Ensure model on the right device if not using device_map
        if self.device != "cuda":
            model = model.to(self.device)

        return model, tokenizer

    def generate(self, prompt, **kwargs):
        # Construct prompt text
        input_prompt = ""
        if isinstance(prompt, list):
            for message in prompt:
                input_prompt += f"<{message['role']}>{message['content']}</{message['role']}>\n"
        elif isinstance(prompt, str):
            input_prompt = prompt

        # Tokenize input
        input_ids = self.tokenizer(
            input_prompt, return_tensors="pt", padding=True, truncation=True
        ).to(self.device)

        # Generate output
        output = self.model.generate(**input_ids)

        # Decode output
        response_text = self.tokenizer.decode(
            output[0][input_ids["input_ids"].shape[1]:], skip_special_tokens=True
        )

        return response_text