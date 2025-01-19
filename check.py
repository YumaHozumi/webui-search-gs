import os
import multiprocessing
import psutil
import ollama
import asyncio  # 追加
from long_time_decorator.ntfy_decorator import measure_time, ntfy
from concurrent.futures import ThreadPoolExecutor

async def translate_text(text, model='aya:8b'):
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, lambda: ollama.chat(model=model, messages=[
        {
            "role": "user",
            "content": f"Please translate this text from English to Japanese and respond with only the translated text.\nText:{text}"
        }
    ], options={"cache": False}))
    return response["message"]["content"]

def get_cpu_info():
    cpu_count = os.cpu_count()
    thread_count = multiprocessing.cpu_count()
    return cpu_count, thread_count

async def parallel_translate_texts(texts, model='aya:8b'):
    loop = asyncio.get_event_loop()
    tasks = [loop.create_task(translate_text(text, model)) for text in texts]
    results = await asyncio.gather(*tasks)
    return results

async def sequential_translate_texts(texts, model='aya:8b'):
    results = []
    for text in texts:
        results.append(await translate_text(text, model))
    return results

if __name__ == "__main__":
    cpu_count, thread_count = get_cpu_info()
    print(f"Available CPU cores: {cpu_count}")
    print(f"Available threads: {thread_count}")

    texts = [
        "Let's see how well this translation works.",
        "Adding more sentences to test the parallel processing.",
        "This is the last sentence.",
        "I hope this works well.",
        "This is an additional sentence for testing.",
        "Another sentence to check the translation accuracy.",
        "Testing with more sentences to see the performance.",
        "Adding yet another sentence to the list.",
        "This should be translated correctly.",
        "Let's add more sentences to the test.",
        "How well does this translation handle different sentences?",
        "This is a simple sentence for translation.",
        "Checking the translation of this sentence.",
        "Adding more sentences to increase the load.",
        "This is a test sentence for translation.",
        "Let's see how this sentence is translated.",
        "Another test sentence for the translation function.",
        "Adding more sentences to test the function.",
        "This is a longer sentence to see how well the translation works with more complex structures.",
        "Testing the translation with a variety of sentences.",
        "Adding different types of sentences to the test.",
        "This is a short sentence.",
        "This is a medium-length sentence for testing.",
        "This is a very long sentence to see how well the translation function handles sentences of varying lengths and complexities.",
        "Adding more sentences to thoroughly test the translation function.",
        "This is another example sentence.",
        "Testing with a different sentence.",
        "Adding more variety to the test sentences.",
        "This is a simple test sentence.",
        "Checking the translation accuracy with this sentence.",
        "Adding more sentences to the test case.",
        "This is a straightforward sentence for translation.",
        "Testing the translation with this sentence.",
        "Adding one more sentence to the list."
    ]
    
    import time 
    start = time.time()
    print("Parallel Translation:")
    parallel_translations = asyncio.run(parallel_translate_texts(texts))
    for original, translated in zip(texts, parallel_translations):
        print(f"{original} -> {translated}")

    print(f"Time taken: {time.time() - start:.2f} seconds")
    
    start = time.time()
    print("\nSequential Translation:")
    sequential_translations = asyncio.run(sequential_translate_texts(texts))
    for original, translated in zip(texts, sequential_translations):
        print(f"{original} -> {translated}")

    print(f"Time taken: {time.time() - start:.2f} seconds")

