# import libs

# local

# SECTION: available llm providers
llm_providers = ["openai", "google", "anthropic", "grok"]

# SECTION: token metadata
# set default values for input and output tokens
default_token_metadata = {
    "input_tokens": -1,
    "output_tokens": -1
}

# set default temperature and max tokens
default_model_settings = {
    "temperature": 0.0,
    "max_tokens": 2048
}


# SECTION: default api config
default_api_config = {
    "port": 8000,
    "host": "127.0.0.1",
    "apiUrl": "http://127.0.0.1:8000"
}