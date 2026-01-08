from pathlib import Path
import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter

DATA_DIR = Path("../data/documents")

def load_pdfs(file_paths=None):
    if file_paths is None:
        file_paths = list(DATA_DIR.glob("*.pdf"))
    
    documents = []
    for pdf_file in file_paths:
        pdf_path = Path(pdf_file) if isinstance(pdf_file, str) else pdf_file
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                if page.extract_text():
                    text += page.extract_text() + "\n"
        documents.append(
            {
                "source": pdf_path.name,
                "content": text
            }
        )
    return documents


def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )

    chunks = []
    for doc in documents:
        split_texts = splitter.split_text(doc["content"])
        for text in split_texts:
            chunks.append(
                {
                    "text": text,
                    "source": doc["source"]
                }
            )
    return chunks


if __name__ == "__main__":
    docs = load_pdfs()
    chunks = chunk_documents(docs)

    print(f"Loaded documents: {len(docs)}")
    print(f"Created chunks: {len(chunks)}")

    print("\nSample chunk:\n")
    print(chunks[0]["text"][:500])
