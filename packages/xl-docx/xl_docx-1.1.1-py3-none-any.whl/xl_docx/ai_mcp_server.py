
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from xl_docx.sheet import Sheet
import openai
import re

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Pydantic model for the request body
class AutomateRequest(BaseModel):
    command: str
    template_path: str
    output_path: str

@app.post("/automate")
async def automate_word(request: AutomateRequest):
    """
    Receives a natural language command to automate a Word document.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        raise HTTPException(status_code=500, detail="OpenAI API key not found. Please set it in the .env file.")

    try:
        # 1. Initialize the Sheet object with the template
        if not os.path.exists(request.template_path):
            raise HTTPException(status_code=404, detail=f"Template file not found: {request.template_path}")
        
        sheet = Sheet(tpl_path=request.template_path)

        # 2. Define the AI's "manual" for the custom XML syntax
        system_prompt = """
        You are an expert assistant that generates a custom XML structure for a .docx file based on user commands.
        Your output MUST be only the raw XML, with no explanations, comments, or markdown formatting.
        The user will provide a command, and you will translate it into the following XML format.

        --- XML SYNTAX REFERENCE ---

        1. PARAGRAPHS (`<xl-p>`):
           - Use `<xl-p>` to create a new paragraph.
           - Example: `<xl-p>This is a paragraph.</xl-p>`
           - STYLING: Use the `style` attribute with CSS-like syntax.
             - `align`: "left", "center", "right", "justify".
             - `font-size`: e.g., "28" (for 14pt font), "32" (for 16pt).
             - `font-weight`: "bold".
             - `color`: Hex color code, e.g., "FF0000" for red.
             - `margin-top`, `margin-bottom`: e.g., "200".
           - Style Example: `<xl-p style="align:center;font-size:32;font-weight:bold;">Centered Bold Title</xl-p>`

        2. TEXT SPANS (`<xl-span>`):
           - Use `<xl-span>` inside `<xl-p>` for styling parts of the text.
           - It supports `style` with `font-size`, `font-weight`, `color`, and `underline`.
           - Underline values: "single", "double", "dash", "dot-dash", etc.
           - Example: `<xl-p>This is <xl-span style="font-weight:bold;color:FF0000;">red and bold</xl-span> text.</xl-p>`

        3. TABLES (`<xl-table>`):
           - Use `<xl-table>` to create a table.
           - `grid`: Defines column widths. e.g., `grid="4500/4500"` for two equal columns.
           - `width`: Total table width. e.g., `width="9000"`.
           - `style`:
             - `align`: "center", "left", "right".
             - `border`: "none" to hide all borders.
           - Example: `<xl-table grid="3000/3000/3000" style="align:center;"> ... table content ... </xl-table>`

        4. TABLE ROWS (`<xl-tr>`):
           - Use `<xl-tr>` for table rows.
           - `header="1"`: Marks the row as a table header (repeats on new pages).
           - `height`: Row height, e.g., `height="500"`.

        5. TABLE CELLS (`<xl-tc>`):
           - Use `<xl-tc>` for table cells.
           - `span`: Column span. e.g., `span="2"`.
           - `merge`: Vertical merge. "start" for the first cell, "continue" for subsequent cells in the merge.
           - `align`: Vertical alignment inside the cell. "center", "top", "bottom".
           - `border-top`, `border-bottom`, `border-left`, `border-right`: "none" to hide a specific border.
           - Content inside `<xl-tc>` MUST be wrapped in `<xl-p>`.
           - Example: `<xl-tc span="2"><xl-p>This cell spans two columns.</xl-p></xl-tc>`

        --- END OF REFERENCE ---

        Now, generate the XML for the user's command. Remember, ONLY output the XML code.
        """

        # 3. Call OpenAI API to generate the xl-xml
        client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://api.laozhang.ai/v1"
        )
        response = client.chat.completions.create(
            model="qwen-turbo-latest",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.command}
            ],
            temperature=0.1,
        )
        ai_generated_xml = response.choices[0].message.content.strip()
        
        # Clean up potential markdown code fences
        if ai_generated_xml.startswith("```xml"):
            ai_generated_xml = ai_generated_xml[6:]
        if ai_generated_xml.startswith("```"):
            ai_generated_xml = ai_generated_xml[3:]
        if ai_generated_xml.endswith("```"):
            ai_generated_xml = ai_generated_xml[:-3]
        ai_generated_xml = ai_generated_xml.strip()


        # 4. Compile the AI-generated XML to WordprocessingML
        # Wrap the AI's output in a single root element to ensure valid XML for the parser.
        wrapped_xml = f"<root>{ai_generated_xml}</root>"
        # The render_template function handles the compilation from xl-* to w:*
        compiled_body_content = sheet.render_template(wrapped_xml, {})
        # Remove the temporary wrapper tag after compilation.
        compiled_body_content = compiled_body_content.replace("<root>", "").replace("</root>", "").strip()

        # 5. Inject the compiled content into the main document.xml
        doc_xml_str = sheet['word/document.xml'].decode('utf-8')
        
        # Find the body tag and replace its content
        body_pattern = re.compile(r'(<w:body>)(.*)(</w:body>)', re.DOTALL)
        if body_pattern.search(doc_xml_str):
            new_doc_xml_str = body_pattern.sub(f'{compiled_body_content}', doc_xml_str)
        else:
            # If no body tag, something is wrong with the template
            raise HTTPException(status_code=500, detail="Invalid template: <w:body> tag not found in document.xml.")

        sheet['word/document.xml'] = new_doc_xml_str.encode('utf-8')

        # 6. Save the final document
        sheet.save(request.output_path)

        return {
            "status": "success",
            "output_path": request.output_path,
            "generated_xml": ai_generated_xml
        }

    except HTTPException as e:
        # Re-raise FastAPI's HTTP exceptions
        raise e
    except Exception as e:
        # Catch any other error and return a 500
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
