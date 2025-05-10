from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import asyncio
import edge_tts
import fitz, re
import os

app = FastAPI(title='Text2Audio')
VOICE = 'en-AU-NatashaNeural'  # Change here
OUTPUT_DIR = 'audiobooks'
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def generate_audio(text: str, output_file: str, vtt_file: str):
    try:
        communicate = edge_tts.Communicate(text, VOICE)
        submaker = edge_tts.SubMaker()
        with open(output_file, "wb") as file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    file.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    submaker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])
        
        with open(vtt_file, "w", encoding="utf-8") as file:
            file.write(submaker.generate_subs())
    except Exception as e:
        print('Exception:', e)

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    with fitz.open(pdf_path) as doc: 
        for page in doc:
            text += page.get_text("text")  
    text = re.sub(r'[^A-Za-z0-9\s.,?!]','',text) 
    return text.replace('\n', ' ') 

async def cleanup_file(file_name: str):
    await asyncio.sleep(5)  
    if os.path.exists(file_name):
        os.remove(file_name)

@app.post('/convert_to_audiobook/')
async def convert_pdf_to_audio(file: UploadFile = File(...)):
    if file.filename == '':
        raise HTTPException(status_code=400, detail="No file selected")
    pdf_path = 'temp_input.pdf'
    with open(pdf_path, 'wb') as f:
        content = await file.read()
        f.write(content)
    try :
        text = extract_text_from_pdf(pdf_path)
    except Exception as e :
        raise HTTPException(status_code=400, detail="Error came")
    if not text:
        os.remove(pdf_path)
        raise HTTPException(status_code=400, detail="No text found in PDF")

    base_filename, _ = os.path.splitext(file.filename)
    output_file = f"{OUTPUT_DIR}/{base_filename}.mp3"
    vtt_file = f"{OUTPUT_DIR}/{base_filename}.vtt"
    await generate_audio(text, output_file, vtt_file)
    os.remove(pdf_path)
    
    return {"Audio generated successfully."}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)