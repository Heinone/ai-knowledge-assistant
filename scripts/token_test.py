import tiktoken

encoding = tiktoken.encoding_for_model("gpt-4.1-mini")

text = "🤳"

tokens = encoding.encode(text)

print("TOKENS:")
print(tokens)

print("\nTOKEN COUNT:")
print(len(tokens))