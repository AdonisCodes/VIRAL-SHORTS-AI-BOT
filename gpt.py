import datetime
import json
import time
from datetime import date

import openai
from transformers import GPT2Tokenizer

import constants

# Setting the OpenAI API key
openai.api_key = constants.op_apikey


# Function to generate a SEO optimized Title for Youtube Video
def gen_optimized_title(prompt):
    print("Generating title for YouTube video...")

    # Generating Title
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user",
                 "content": f"Can you use this text to just generate a seo optimized title, your response should only have the title in format 'title here', without the quotation marks\n here is the captions of the video: \n {prompt}"}
            ]
        )
        return completion.choices[0].message.content
    # Retrying When There is any error
    except:
        time.sleep(20)
        gen_optimized_description(prompt)


# Function to generate a SEO optimized Description for YouTube
def gen_optimized_description(prompt):
    print("Generating YouTube video description...")

    # Generating Description
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user",
                 "content": f"Can you use this text to just generate a seo optimized description, your response should "
                            f"only have the description in format 'description here' no quotations\n here is the captions "
                            f"of the video: \n {prompt}"}
            ]
        )
        return completion.choices[0].message.content
    # On any Error Retry the generation
    except:
        time.sleep(20)
        gen_optimized_description(prompt)


# Function to create a New Date, from the Provided previous Date
def gen_new_date(current_date):
    print("Generating new scheduling date...")

    # Generating New Date
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f'the date and time should stay in the '
                               f'same format, can you please add 8 hours to the provided response, Only send the '
                               f'response, as a json object \n{current_date}. Just Note If the date is behind the current {datetime.date}, return the current date + 1 day in the format of `{current_date}`. No extra boilerplate! only the new object. '
                               f'And in the exact format I gave you.'
                }
            ]
        )
    # On any Error, retry the Generation
    except:
        time.sleep(20)
        gen_new_date(current_date)

    # Convert the Response to JSON
    try:
        res = json.loads(completion.choices[0].message.content)
        test_date = res["new_date"]
        test_time = res["new_time"]

    # If there was any Error, retry the Generation
    except:
        time.sleep(20)
        gen_new_date(current_date)

    # Return the Response
    return res


# Function to check Date and respond using 1 or 0
def check_date(d):
    print("Comparing Dates of video...")

    # Checking if the Date is 30 Days ahead or behind the Current Date
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user",
                 "content": f"Are these two dates 30 days or more apart? {d} to {date.today()}, only reply with 1 if more than 30, and 0 if less. ONly use the number to reply, nothing else."}
            ]
        )
    # On any Error, retry the generation
    except:
        time.sleep(20)
        check_date(d)

    # Convert the response To an Integer

    try:
        res = int(completion.choices[0].message.content)
    # IF any Error, retry the generation
    except:
        time.sleep(20)
        check_date(d)

    # Return the Response
    return res


# An example Resonpose Object for the Function Below
response_obj = '''[
  {
    "start_time": 97.19 # time in seconds,
    "end_time": 127.43 # time in seconds,
    "duration":36 #Length in seconds
  },
  {
    "start_time": 169.58,
    "end_time": 199.10 ,
    "duration":33
  }, ...
]'''


# Function to analyze a given input, and return the appropriate Timestamps
def analyze_interesting_parts(transcript):
    # Setting the Prompt up
    prompt = f'''
                You are ViralGPT. This is a transcript of a video. Your task is to identify the most viral sections from the video. Ensure that the selected sections are at least 30 seconds in duration. Please provide your response in the following format:

                {response_obj}
                Here is the transcript for reference:
                
                {transcript}
                Please respond with the answer only, using the start_time and end_time formatted in seconds, formatted in seconds, formatted in seconds. The transcript is divided into chunks And uses a minute:second format , so use the provided timestamps and convert them into seconds.'''

    messages = [
        {"role": "system",
         "content": prompt}]

    # Get the Timestamps Of the Interesting Parts
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stop=None,
            n=1
        )
    # On any errors, retry the Generation
    except:
        time.sleep(20)
        analyze_interesting_parts(transcript)

    res = response.choices[0]['message'].content
    # Loop over the response
    while True:
        # Try to convert the response int JSON
        try:
            # convert the response to json
            return json.loads(res)
        # IF A JSON ERROR occurs, do some VooDoo Magic and retry
        except json.decoder.JSONDecodeError:
            if res == "]":
                return None
            res = res[:-2]
            res += "]"
            print("Retrying to parse the response...")


# Function to Split up A Massive Input, and Analyze it in chunks
def split_analyze(string):
    # Splitting Input into Chunks
    print("Splitting Input into Chunks...")
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    tokens = tokenizer.encode(string, add_special_tokens=False)
    chunk_size = 500
    chunks = [tokens[i:i + chunk_size] for i in range(0, len(tokens), chunk_size)]
    chunk_strings = [tokenizer.decode(chunk) for chunk in chunks]
    parts = []

    # Generating the Response
    print("Generating Response...")
    for chunk_string in chunk_strings:
        time.sleep(20)
        part = analyze_interesting_parts(chunk_string)

        if part is not None:
            for p in part:
                parts.append(p)
    # Return the Response In one Massive List of Dicts
    return parts


# Function To generate unique Images Based on input
def generate_image(caption):
    print("Generating Prompt for Image...")

    # Generate the Prompt For Image Generation
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user",
                 "content": f'''You are the Image Prompt Generator! Your role is to create detailed prompts for an image generator based on a given input text. Your goal is to provide specific instructions and details that will help the image generator accurately create an image based on the input. Remember to be as descriptive as possible, including important visual elements, colors, composition, and any other relevant details. Here's an example of how you can generate a prompt:
                Input: "finch"
                
                Prompt for Image Generator:
                a tiny finch on a branch with spring flowers on background:1.O, aesthetically inspired by Evelyn De Morgan, art by Gill Sienkiewicz and Dr-Seuss, realistic, Sigma 85 mm f/1.4, 
                
                Your prompt should provide clear instructions and vivid descriptions to guide the image generator in creating the 
                desired image. Remember, the more detailed and specific your prompt is, the better the chances of getting the image 
                you envision. Make the prompt simple and not more than 2 sentences, and use common words for the generation!
                
                My prompt: {caption}'''}
            ]
        )
    # If any errors occur, retry the generation
    except:
        time.sleep(20)
        generate_image(caption)

    # Generating the Image
    print("Generating Image...")
    try:
        req = openai.Image.create(
            prompt=completion.choices[0]['message'].content,
            n=1,
            size="256x256"
        )
    # If any errors occur, retry the generation
    except:
        time.sleep(20)
        generate_image(caption)

    # Return the generated Image Url
    return req.data[0].url


# Function to generate Emoji from A given Input
def generate_emoji(caption):
    # Generate the Emoji
    print("Generating Emoji...")

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user",
                 "content": f'''
                  You are the Emoji Generator! Your task is to generate the perfect emoji based on a given input text. Your response should consist only of the emoji itself, without any additional text or context. Make sure to capture the tone and meaning of the input text with your emoji selection. Remember, your goal is to provide a visual representation of the input text using emojis. Let's see what you come up with!
                    
                  Remember, your response should only include the emoji and nothing else. Have fun generating expressive emojis!
                  Remember, your response should only include the emoji and nothing else.
                  Remember, your response should only include the emoji and nothing else.
                    
                  My input:
                  {caption}'''}])

    # If any error occurs, retry the Generation
    except:
        time.sleep(20)
        generate_emoji(caption)

    # Return the Generated Emoji
    return completion.choices[0]['message'].content
