from app.nlu import LocalLLM, LLMConfig

cfg = LLMConfig()
llm = LocalLLM(cfg)
print("Loaded:", bool(llm.impl))

if llm.impl:
    response = llm.generate("Generate a safe terminal command: list all files")
    print("Model Response:", response)