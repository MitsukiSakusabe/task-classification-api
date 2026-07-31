from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

messages = [
    {
        "role":"system",
        "content":"あなたは親切なAIです。必ず日本語だけで回答してください。英語と中国語は使わないでください。"
    }
]


print("AIチャットを開始します。終了するには exit と入力してください。")

while True:
    user_input = input("あなた：")

    if user_input.lower() == "exit":
        print("終了します。")
        break

    messages.append({
        "role":"user",
        "content":user_input
    })

    response = client.chat.completions.create(
        model="llama3.2",
        messages=messages
    )

    ai_message = response.choices[0].message.content

    print(f"\nAI:{ai_message}\n")

    messages.append({
        "role":"assistant",
        "content":ai_message
    })