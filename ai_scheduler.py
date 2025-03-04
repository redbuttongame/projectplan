import os
import json
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def generate_schedule(preferences):
    try:
        # Configure the model
        model = genai.GenerativeModel('gemini-2.0-flash')

        prompt = """
        You are an AI schedule generator. Create a detailed daily schedule based on the following preferences.
        Return the schedule as a JSON object with time slots and activities.
        The output should be strictly in JSON format with this structure:
        {
            "schedule": [
                {"time": "HH:MM", "activity": "description"},
                ...
            ]
        }

        User preferences:
        """ + preferences

        # Generate the schedule
        response = model.generate_content(prompt)

        # Extract JSON from the response
        # Remove any markdown formatting if present
        content = response.text.replace("```json", "").replace("```", "").strip()

        # Parse the JSON response
        schedule_data = json.loads(content)
        return schedule_data

    except Exception as e:
        raise Exception(f"Failed to generate schedule: {e}")