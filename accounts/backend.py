import copy
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


def SlideCopyFromPasteInto(copyFromPres, slideIndex,  pasteIntoPres):

    # specify the slide you want to copy the contents from
    slide_to_copy = copyFromPres.slides[slideIndex]

    # Define the layout you want to use from your generated pptx

    slide_layout = pasteIntoPres.slide_layouts.get_by_name("Blank") # names of layouts can be found here under step 3: https://www.geeksforgeeks.org/how-to-change-slide-layout-in-ms-powerpoint/
    # it is important for slide_layout to be blank since you dont want these "Write your title here" or something like that textboxes
    # alternative: slide_layout = pasteIntoPres.slide_layouts[copyFromPres.slide_layouts.index(slide_to_copy.slide_layout)]
    
    # create now slide, to copy contents to 
    new_slide = pasteIntoPres.slides.add_slide(slide_layout)

    # create images dict
    imgDict = {}

    # now copy contents from external slide, but do not copy slide properties
    # e.g. slide layouts, etc., because these would produce errors, as diplicate
    # entries might be generated
    for shp in slide_to_copy.shapes:
        if 'Picture' in shp.name:
            # save image
            with open(shp.name+'.jpg', 'wb') as f:
                f.write(shp.image.blob)

            # add image to dict
            imgDict[shp.name+'.jpg'] = [shp.left, shp.top, shp.width, shp.height]
        else:
            # create copy of elem
            el = shp.element
            newel = copy.deepcopy(el)

            # add elem to shape tree
            new_slide.shapes._spTree.insert_element_before(newel, 'p:extLst')
    
    # things added first will be covered by things added last => since I want pictures to be in foreground, I will add them after others elements
    # you can change this if you want
    # add pictures
    for k, v in imgDict.items():
        new_slide.shapes.add_picture(k, v[0], v[1], v[2], v[3])
        os.remove(k)

    return new_slide # this returns slide so you can instantly work with it when it is pasted in presentation


def process_ppt(ppt_file_path):
  try:
    prs = Presentation(r"C:\Users\Udisha\Documents\heklelal.pptx")
    extracted_text_per_slide = extract_text_from_ppt(ppt_file_path)
    enhanced_text_per_slide = [enhance_text_with_openai(text) for text in extracted_text_per_slide]
    for enhanced_text in enhanced_text_per_slide:
      # Add a new slide with a layout (adjust layout as needed)
      new_slide = SlideCopyFromPasteInto(prs, 0, prs)  # Title and Content layout
      for shape in new_slide.shapes:
          if hasattr(shape, "text"):
              shape.text = enhanced_text
              for paragraph in shape.text_frame.paragraphs:
                        for run in paragraph.runs:
                            run.font.size = Pt(18)

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
