from openai import OpenAI
from pptx import Presentation
from pptx.util import Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
import os
from dotenv import load_dotenv

load_dotenv()
# Replace 'your-api-key' with your actual OpenAI API key
api_key = os.getenv('api_key')

# Initialize OpenAI client with your API key
client = OpenAI(api_key=api_key)

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
        # Call the function to extract text from the PowerPoint file
        extracted_text_per_slide = extract_text_from_ppt(ppt_file_path)

        # Enhance the text of each slide using OpenAI API
        enhanced_text_per_slide = [enhance_text_with_openai(text) for text in extracted_text_per_slide]

        # Load the PowerPoint presentation
        prs = Presentation(ppt_file_path)

        # Iterate through each slide in the presentation
        for i, slide in enumerate(prs.slides):
            # Remove existing shapes from the slide layout
            for placeholder in slide.placeholders:
                if placeholder.is_placeholder:
                    slide.shapes._spTree.remove(placeholder._element)

            # Get the slide dimensions
            slide_width = prs.slide_width
            slide_height = prs.slide_height

            # Concatenate enhanced text for the slide
            enhanced_slide_text = ""
            if i < len(enhanced_text_per_slide):
                enhanced_slide_text = enhanced_text_per_slide[i]

            # Add a new text box covering the entire slide
            left = top = 0
            width = slide_width
            height = slide_height
            txBox = slide.shapes.add_textbox(left, top, width, height)
            tf = txBox.text_frame

            # Set the text box properties
            tf.word_wrap = True
            tf.fit_text(max_size=Pt(20))  # Fit text to box and set max size to 20 points
            tf.paragraphs[0].alignment = PP_ALIGN.LEFT  # Left align the text

            # Set the font properties for the entire text box
            for paragraph in tf.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(20)  # Set text size to 20 points
                    run.font.name = "Times New Roman"  # Set font to Times New Roman
                    
                    # Set font color to a predefined theme color
                    run.font.color.rgb = RGBColor(0,0,0)  # Example theme color
                    
                    # Alternatively, set font color using hex color code
                    # run.font.color.rgb = RGBColor.from_string('FF5733')  # Example hex color code

            # Set slide background color to black
            background = slide.background
            fill = background.fill
            fill.solid()
            fill.fore_color.rgb = RGBColor(255,255,255)  # Set RGB color for black

            # Set the enhanced text for the entire slide in the text box
            tf.text = enhanced_slide_text

        # Save the modified PowerPoint presentation
        enhanced_ppt_path = "enhanced_presentation.pptx"
        prs.save(enhanced_ppt_path)
        print("Enhanced PowerPoint presentation saved successfully.")
        return enhanced_ppt_path
    except Exception as e:
        print("An error occurred:", str(e))

# Prompt the user to input the path to the PowerPoint file
#ppt_file_path = input("Enter the path to the PowerPoint file: ")
#enhanced_ppt_path = process_ppt(ppt_file_path)

