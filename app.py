import gradio as gr
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

LANGUAGES = [
    "Python", "Java", "C", "C++", "C#", "HTML", "CSS", "Javascript", "Kotlin",
    "Swift", "Rust", "PHP", "SQL", "Dart", "Flutter", "R"
]

LANG_KEYWORDS = {
    "Python": ["def", "import", "print", "self", "lambda"],
    "Java": ["public", "static", "void", "class", "System.out"],
    "C": ["#include", "printf", "scanf", "int main"],
    "C++": ["#include", "std::", "cout", "cin", "int main"],
    "C#": ["using", "namespace", "Console.WriteLine", "class"],
    "HTML": ["<html", "<body", "<div", "<head", "<title"],
    "CSS": ["{", "}", "color:", "font-size:", "margin:"],
    "Javascript": ["function", "let", "const", "console.log", "var"],
    "Kotlin": ["fun", "val", "var", "class", "object"],
    "Swift": ["func", "let", "var", "import UIKit"],
    "Rust": ["fn", "let", "mut", "println!", "use"],
    "PHP": ["<?php", "echo", "$", "function"],
    "SQL": ["SELECT", "FROM", "WHERE", "INSERT", "UPDATE"],
    "Dart": ["void main()", "import", "class", "final"],
    "Flutter": ["Widget", "MaterialApp", "Scaffold", "build"],
    "R": ["<-", "library(", "print(", "function("],
}

def matches_language(code, language):
    keywords = LANG_KEYWORDS.get(language, [])
    return any(kw in code for kw in keywords)

def process_code_completion(message, model, language):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Complete the following {language} code:\n{message}",
            }
        ],
        model=model,  
    )
    return chat_completion.choices[0].message.content  

def process_snippet_generation(message, model, language):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Generate a {language} code snippet for: {message}",
            }
        ],
        model=model,  
    )
    return chat_completion.choices[0].message.content  

def process_bug_fixes(message, model, language):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Fix the errors in the following {language} code:\n{message}",
            }
        ],
        model=model,  
    )
    return chat_completion.choices[0].message.content 

def process_explanation(message, model, language):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Explain the following {language} code:\n{message}",
            }
        ],
        model=model,  
    )
    return chat_completion.choices[0].message.content 

def create_new_chat():
    return (
        gr.update(value=""),  
        gr.update(value=""),  
        gr.update(visible=False),  
        gr.update(visible=False),  
        gr.update(visible=False),  
        gr.update(visible=False),  
        gr.update(visible=False),  
        gr.update(visible=False),  
        gr.update(value=None),     
    )

with gr.Blocks() as demo:
    gr.Markdown("# Coding Assistant")

    with gr.Row():
        code_completion_button = gr.Button("Code Completion")
        snippet_generation_button = gr.Button("Code Snippet Generation")
        bug_fixes_button = gr.Button("Bug Fixes and Explanation")

    option = gr.State()  

    bug_option = gr.Radio(
        ["Explain the code", "Fix bugs"],
        label="Choose Bug Option",
        visible=False
    )
    message = gr.Textbox(label="Enter your code or message", visible=False)
    model = gr.Dropdown(
        ["llama3-70b-8192", "whisper-large-v3-turbo", "mistral-saba-24b", "meta-llama/llama-4-maverick-17b-128e-instruct", "deepseek-r1-distill-llama-70b", "gemma2-9b-it"],
        label="Select Model",
        value="meta-llama/llama-4-maverick-17b-128e-instruct",
        visible=False
    )
    language = gr.Dropdown(
        LANGUAGES,
        label="Select Coding Language",
        value="Python",
        visible=False
    )
    response_output = gr.Textbox(label="Response", interactive=False, visible=False)
    submit_button = gr.Button("Submit", visible=False)



    def show_code_completion(_):
        return (
            gr.update(visible=False),   # bug_option
            gr.update(visible=True),    # message
            gr.update(visible=True),    # model
            gr.update(visible=True),    # language
            gr.update(visible=True),    # response_output
            gr.update(visible=True),    # submit_button
            "Code Completion"           # option
        )

    def show_snippet_generation(_):
        return (
            gr.update(visible=False),   # bug_option
            gr.update(visible=True),    # message
            gr.update(visible=True),    # model
            gr.update(visible=True),    # language
            gr.update(visible=True),    # response_output
            gr.update(visible=True),    # submit_button
            "Code Snippet Generation"   # option
        )

    def show_bug_fixes(_):
        return (
            gr.update(visible=True),    # bug_option
            gr.update(visible=True),    # message
            gr.update(visible=True),    # model
            gr.update(visible=True),    # language
            gr.update(visible=True),    # response_output
            gr.update(visible=True),    # submit_button
            "Bug Fixes and Explanation" # option
        )

    code_completion_button.click(
        show_code_completion,
        inputs=[option],
        outputs=[bug_option, message, model, language, response_output, submit_button, option]
    )
    snippet_generation_button.click(
        show_snippet_generation,
        inputs=[option],
        outputs=[bug_option, message, model, language, response_output, submit_button, option]
    )
    bug_fixes_button.click(
        show_bug_fixes,
        inputs=[option],
        outputs=[bug_option, message, model, language, response_output, submit_button, option]
    )

    def handle_submission(option_val, bug_option_val, message_val, model_val, language_val):
        if option_val == "Code Completion":
            if not matches_language(message_val, language_val):
                return f"Error: The code/message does not appear to match the selected language ({language_val}). Please check your input."
            return process_code_completion(message_val, model_val, language_val)
        elif option_val == "Code Snippet Generation":
            # No language check for snippet generation prompt
            return process_snippet_generation(message_val, model_val, language_val)
        elif option_val == "Bug Fixes and Explanation":
            if not matches_language(message_val, language_val):
                return f"Error: The code/message does not appear to match the selected language ({language_val}). Please check your input."
            if bug_option_val == "Explain the code":
                return process_explanation(message_val, model_val, language_val)
            elif bug_option_val == "Fix bugs":
                return process_bug_fixes(message_val, model_val, language_val)
            else:
                return "Please select an option: Explain the code or Fix bugs."
        else:
            return "Invalid option selected."

    submit_button.click(
        handle_submission,
        inputs=[option, bug_option, message, model, language],
        outputs=response_output
    )

    gr.Markdown("### Description: Select an option to either complete code, generate a code snippet, or fix/explain code. Choose the coding language as well.")

if __name__ == "__main__":
    demo.launch(share=True)