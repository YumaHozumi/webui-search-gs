import ollama

response = ollama.chat(model='aya:8b', messages=[
    {
        "role": "user",
        "content": "Please translate this text from English to Japanese and respond with only the translated text.\nText:Hello, World!"
    }
])

print(response["message"]["content"])