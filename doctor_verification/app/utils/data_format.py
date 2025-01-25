import os
import google.generativeai as genai
from datetime import datetime
from app.utils.file_reading import read_text_file
import json

genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

try:
    generation_config = {
        "response_mime_type": "application/json",
    }

    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        generation_config=generation_config,
    )

    chat = model.start_chat(history=[])

except Exception as e:
    raise RuntimeError(f"Failed to initialize the generative model: {e}")

def get_relative_path(*path_segments):
    """Resolve file path relative to the script's directory."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), *path_segments)

def format_data(data):
    global chat
    try:
        current_date = datetime.now().date()
        promt_path = get_relative_path("static", "promts", "promt.txt")
        promt_contents = read_text_file(promt_path)
        response = chat.send_message(
            f'''text: {data}, {promt_contents}, {current_date}.''',
            stream=False,
        )
        response.resolve()

        try:
            result = json.loads(response.text)
            print("response:", result)
            return result
        except json.JSONDecodeError:
            return {"error": "Failed to decode the response as JSON. The response might not be valid JSON."}

    except FileNotFoundError:
        return {"error": "The specified file was not found."}
    except ValueError as ve:
        return {"error": f"Value error occurred: {ve}"}
    except Exception as e:
        return {"error": f"Error generating content: {e}. Kindly refresh and try again."}
