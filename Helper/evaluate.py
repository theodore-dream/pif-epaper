import openai
import os
openai.api_key = os.environ["OPENAI_API_KEY"]

text = "(The green lizard basks " \
        "in the warmth of the sun. " \
        "Nature's vibrant brushstrokes, " \
        "displayed for all to admire.)"







def evaluation_api(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Evaluate the following text: "
            },
            {
                "role": "user",
                "content": text
            },
            {
                "role": "user",
                "content": "rate the text from 1 to 10"
            }
        ],
        max_tokens=500,
        temperature=(1),
        top_p=1,
    )
    
    api_response = response['choices'][0]['message']['content']
    print (api_response)
    return api_response

evaluation_api(text)
