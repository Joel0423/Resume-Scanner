import google.generativeai as genai

genai.configure(api_key="AIzaSyA-Xrl9eqmuvOuwD3VLVmr3JGA5iX4T_-8")
model = genai.GenerativeModel("gemini-1.5-flash")
company = "Ekkenis Software Limited"
response = model.generate_content(f"is {company} a software company? respond only \"YES\" or \"NO\"")
print(response.text)