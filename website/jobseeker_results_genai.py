import google.generativeai as genai
import json

def get_recommendations(scores, resume, job_desc):
    genai.configure(api_key="AIzaSyA-Xrl9eqmuvOuwD3VLVmr3JGA5iX4T_-8")
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""Compare this resume and job description to answer the following to create a recommendation for the user.

    1. What's wrong with the resume?
    2. How can it be fixed?
    3. Skills that could help.

    Use the scores given for each section of the resume.
    Write one to two sentences for each question.

    Resume: {resume}
    Job Description: {job_desc}
    Scores: {scores}

    Use this JSON schema:

    response = {{'What's wrong with the resume?': str, 'How can it be fixed?': str,'Skills that could help.': str}}
    Return: response
    """

    response = model.generate_content(prompt)
    response_text = response.text
    response_text = response_text.replace("```json","")
    response_text = response_text.replace("```", "")
    
    response_dict = json.loads(response_text)
    return response_dict
