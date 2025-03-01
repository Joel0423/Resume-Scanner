import google.generativeai as genai

def get_recommendations(scores, resume, job_desc):
    genai.configure(api_key="AIzaSyA-Xrl9eqmuvOuwD3VLVmr3JGA5iX4T_-8")
    model = genai.GenerativeModel("gemini-1.5-flash")
    company = "Ekkenis Software Limited"
    response = model.generate_content(f"""Compare this resume and job description to answer the following to create a recommendation for the user-
        1. What's wrong with the resume ?
        2. How can it be fixed ?
        3. Skills that could help
        \nUse the scores given for each section of the resume
        \nwrite one to two sentences for each question
        \nResume-{resume}
        \njob description-{job_desc}
        \nscores-{scores}""")
    
    
    print(response.text)
    return response.text