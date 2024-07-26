#from decouple import config
import gradio as gr
from gradio_multimodalchatbot import MultimodalChatbot
from apputil import query
from fastapi import FastAPI
import os

#app = FastAPI()
CUSTOM_PATH = "/gradio"
def invoke_agent(input,chatbot=[]):
    messages = []
    print(chatbot)
    
        # Process previous chatbot messages if present
    if len(chatbot) != 0:
        for user, bot in chatbot:
            user, bot = user.text, bot.text
            messages.extend([
                {'role': 'user', 'parts': [user]},
                {'role': 'model', 'parts': [bot]}
            ])
        messages.append({'role': 'user', 'parts': [input]})
    else:
        messages.append({'role': 'user', 'parts': [input]})
        # Construct list of messages in the required format
    agent_resp =  query(input)   
    user_msg = {"text": input, "files": []}
    bot_msg = {"text": agent_resp['output'], "files": []}
    chatbot.append([user_msg, bot_msg])    
    return chatbot, "", None
# Define the Gradio Blocks interface
with gr.Blocks() as demo:
    # Add a centered header using HTML
    gr.HTML("<center><h1>Merck-AI</h1></center>")

    # Initialize the MultimodalChatbot component
    multi = MultimodalChatbot(value=[], height=800)

    with gr.Row():
        # Textbox for user input with increased scale for better visibility
        tb = gr.Textbox(scale=4, placeholder='Input text and press Enter')

        # Upload button for image files
        #up = gr.UploadButton("Upload Image", file_types=["image"], scale=1)

    # Define the behavior on text submission
    tb.submit(invoke_agent, [tb, multi], [multi, tb])

    # Define the behavior on image upload
    # Using chained then() calls to update the upload button's state
    #up.upload(lambda: gr.UploadButton("Uploading Image..."), [], up) \
    #   .then(lambda: gr.UploadButton("Image Uploaded"), [], up) \
    #   .then(lambda: gr.UploadButton("Upload Image"), [], up)
#app = gr.mount_gradio_app(app,demo,path=CUSTOM_PATH)

# Launch the demo with a queue to handle multiple users
demo.queue().launch(share=False,server_name="0.0.0.0",server_port=int(os.getenv("PORT",9000)))



