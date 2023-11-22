import os
import openai
import json


openai.api_key = os.getenv("OPENAI_API_KEY")


def create_poem_1():
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Your name is Alice. You create poems. Alice, a beautiful young girl with curly blonde hair, loves to write uplifting and cheery poetry, that may have a dark or an ironic twist"},
            {"role": "user", "content": "Create a poem inspired by the following text: small tree frog. Explain why you created the poem the way you did."}
        ],
        functions=[
            {
                "name": "create_poem",
                "description": "generate poetry and explain why it was created",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "poem": {
                            "type": "string",
                            "description": "a poem",
                        },
                        "explanation": {
                            "type": "string",
                            "description": "explanation of the poem"
                        }
                    },
                    "required": ["poem", "explanation"],
                }
            }
        ],
        function_call="auto",
        temperature=1.2,
    )
    message = completion.choices[0].message
    arguments = json.loads(message.function_call.arguments)
    return arguments['poem']

poem = create_poem_1()
print(poem)


#def test_create_poem():
#    response = openai.ChatCompletion.create(
#        model="gpt-3.5-turbo",
#        messages=[{"role": "user", "content": "Create a poem about love"}], # include the keyword in the user message
#        max_tokens=3600,
#        n=1,
#        stop=None,
#        temperature=1.2,
#        functions=[create_poem]
    #)
    # Return API response
 #   print(response['choices'][0]['message']['content'])
 #   return response
