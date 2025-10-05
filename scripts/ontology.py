import google.generativeai as genai
import json

# Initialize Gemini client
genai.configure(api_key="AIzaSyCuECKPah8MOd-kJOGLBTqB7CvHkYB-Zzw")


# for m in genai.list_models():
#     if "generateContent" in m.supported_generation_methods:
#         print(m.name)
model = genai.GenerativeModel("gemini-2.5-flash")

# Load your text or JSON
json_path="data/structured_data.json"
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Prompt Gemini to extract triplets
prompt = f"""
Extract semantic triplets (subject, relation, object) from the following text.
Output as a JSON list of triplets:
{data}
"""

response = model.generate_content(prompt)
triplets = response.text

output_path = "ontology.json"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(triplets)

# Safe print
print("Triplets saved successfully. Preview:")


print(" Triplets saved as triplets.json")
