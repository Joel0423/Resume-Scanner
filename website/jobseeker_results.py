import google.generativeai as genai
import json

def get_recommendations(scores, resume, job_desc):
    genai.configure(api_key="AIzaSyA-Xrl9eqmuvOuwD3VLVmr3JGA5iX4T_-8")
    model = genai.GenerativeModel("gemini-1.5-flash")
    company = "Ekkenis Software Limited"
    prompt = f"""Compare this resume and job description to answer the following to create a recommendation for the user. Return the response as a JSON object with keys Q1, Q2, and Q3, and the answers as the values.

    1. What's wrong with the resume?
    2. How can it be fixed?
    3. Skills that could help.

    Use the scores given for each section of the resume.
    Write one to two sentences for each question.

    Resume: {resume}
    Job Description: {job_desc}
    Scores: {scores}

    Use this JSON schema:

    response = {{'Q1': str, 'Q2': str,'Q3': str}}
    Return: response
    """

    response = model.generate_content(prompt)
    response_text = response.text
    response_text = response_text.replace("```json","")
    response_text = response_text.replace("```", "")
    
    response_dict = json.loads(response_text)
    return response_dict
