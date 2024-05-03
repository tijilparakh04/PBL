from openai import OpenAI
from pptx import Presentation
from pptx.util import Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
import os
from dotenv import load_dotenv
import pymongo
from myproject import settings

load_dotenv()
# Replace 'your-api-key' with your actual OpenAI API key
api_key = os.getenv('api_key')

# Initialize OpenAI client with your API key
client = OpenAI(api_key=api_key)

client1 = pymongo.MongoClient(settings.MONGODB_URI)
db = client1[settings.MONGODB_NAME]
collection = db['enhanced_ppt']

def extract_text_from_ppt(ppt_file):
    # Load the PowerPoint presentation
    prs = Presentation(ppt_file)

    # Initialize an empty list to store the extracted text from each slide
    extracted_text_per_slide = []

    # Iterate through each slide in the presentation
    for slide in prs.slides:
        # Initialize an empty string to store the text of the current slide
        slide_text = ""

        # Iterate through each shape (text box) in the slide
        for shape in slide.shapes:
            # Check if the shape has text
            if hasattr(shape, "text"):
                # Concatenate the text from the shape to the slide_text string
                slide_text += shape.text + "\n"

        # Append the slide_text string to the list
        extracted_text_per_slide.append(slide_text)

    # Return the list containing the text of each slide
    return extracted_text_per_slide

def enhance_text_with_openai(text):

    # Choose an available engine for text enhancement
    engine = "gpt-3.5-turbo-1106"  # Replace with the engine you want to use

    # Generate enhanced text using the chosen engine
    response = client.chat.completions.create(model=engine,
                                              messages=[{"role": "user", "content": text}],
                                              max_tokens=150)

    # Get the enhanced text from the response
    enhanced_text = response.choices[0].message.content

    return enhanced_text

def process_ppt(ppt_file_path):
    try:
        # Load the custom PowerPoint template
        prs = Presentation(r"C:\Users\Udisha\Documents\heklelal.pptx")

        # Call the function to extract text from the PowerPoint file
        extracted_text_per_slide = extract_text_from_ppt(ppt_file_path)

        # Enhance the text of each slide using OpenAI API
        enhanced_text_per_slide = [enhance_text_with_openai(text) for text in extracted_text_per_slide]

        # Iterate through each slide in the custom template presentation
        for i, slide in enumerate(prs.slides):
            # Modify the content of each slide while keeping the layout and formatting from the template

            # For example, you can access and modify text boxes, shapes, etc.:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    # Modify text content based on enhanced_text_per_slide
                    # For example:
                    shape.text = enhanced_text_per_slide[i]

        # Save the modified PowerPoint presentation
        enhanced_ppt_path = "enhanced_presentation.pptx"
        prs.save(enhanced_ppt_path)
        print("Enhanced PowerPoint presentation saved successfully.")
        with open(enhanced_ppt_path, 'rb') as f:
            enhanced_ppt_data = f.read()
            ppt_doc = {'name': 'enhanced_presentation.pptx', 'data': enhanced_ppt_data}
            collection.insert_one(ppt_doc)
        return enhanced_ppt_path
    except Exception as e:
        print("An error occurred:", str(e))


