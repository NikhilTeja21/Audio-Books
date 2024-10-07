from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import asyncio
import edge_tts
import fitz, re
from zipfile import ZipFile
import os

app = FastAPI()
VOICE = 'en-AU-NatashaNeural'  # en-AU-WilliamNeural - for Male voice

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
    output_file = f"output/{base_filename}.mp3"
    vtt_file = f"output/{base_filename}.vtt"
    await generate_audio(text, output_file, vtt_file)
    os.remove(pdf_path)
    
    download_mp3 = f"http://192.168.50.180:8000/download/{os.path.basename(output_file)}"
    download_vtt = f"http://192.168.50.180:8000/download/{os.path.basename(vtt_file)}"
    print(download_mp3,download_vtt)
    return {"download_mp3": download_mp3, "download_vtt": download_vtt}

@app.get("/download/{file_name}")
async def download_file(file_name: str, background_tasks: BackgroundTasks):
    file_location = os.path.join('output', file_name)
    background_tasks.add_task(cleanup_file, file_location)
    if os.path.exists(file_location):
        return FileResponse(path=file_location, filename=file_name)
    else:
        return {"error": "File not found"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)