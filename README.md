# Text2Audio-Subtitles

This project converts PDF files into audiobooks with synchronized subtitles in `.vtt` format. It uses FastAPI for the backend and Microsoft's Edge TTS for text-to-speech conversion.

## Features

- Extracts text from PDF files.
- Converts extracted text into high-quality audio files (`.mp3`).
- Generates subtitle files (`.vtt`) for the audio to provide synchronized captions.
- Supports asynchronous processing for efficient and fast performance.
- Automatically cleans up temporary files after processing.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-repo/Text2Audio-Subtitles.git
   cd Text2Audio-Subtitles
   ```

2. Install the required dependencies:
   ```bash
   pip install -r .\requirements.txt
   ```

## Usage

1. Start the FastAPI server:

   ```bash
   python app.py
   ```

2. Open your browser and navigate to `http://127.0.0.1:8000/docs` to access the Swagger UI.

3. Use the `/convert_to_audiobook/` endpoint to upload a PDF file. The server will process the file and generate the audiobook (`.mp3`) and subtitle (`.vtt`) files.

## Output

- The generated `.mp3` and `.vtt` files will be saved in the `audiobooks` directory.
- Temporary files (e.g., uploaded PDFs) will be automatically deleted after processing.

## Requirements

- Python 3.8 or higher
- Dependencies listed in `requirements.txt`

## Contributing

Contributions are welcome! If you'd like to improve this project, feel free to fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for providing a modern web framework.
- [Microsoft Edge TTS](https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/) for text-to-speech capabilities.
- [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/) for PDF text extraction.
