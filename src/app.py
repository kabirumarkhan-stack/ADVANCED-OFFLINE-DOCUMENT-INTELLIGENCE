from flask import Flask, request, jsonify, render_template_string
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from werkzeug.utils import secure_filename
from rag import load_index, retrieve_chunks, ask_gemma
import embed
import ingest
import faiss
import pickle

app = Flask(__name__, static_folder='static')

# Configuration
UPLOAD_FOLDER = '../data/documents'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Global variables for index and chunks
index = None
chunks = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_or_create_index():
    global index, chunks
    try:
        index, chunks = load_index()
    except:
        # If no index exists, create empty ones
        index = None
        chunks = []

load_or_create_index()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Offline Document Intelligence</title>
    <link rel="stylesheet" href="/static/css/styles.css">
    <script src="/static/js/scripts.js" defer></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
</head>
<body>
    <div class="container">
        <section class="hero">
            <h1>Advanced Offline Document Intelligence Platform</h1>
            <hr><br>
            <p>Securely analyze your documents with AI. Upload PDFs and ask intelligent questions—all processing happens locally on your device.</p>
            <div class="guide">
            <center>
                <h3>How to Use:</h3>
                </center>
                <ol>
                    <li>Click the 📎 button to upload PDF documents</li>
                    <li>Type your questions in the chat below</li>
                    <li>Get instant, AI-powered answers with source references</li>
                </ol>
            </div>
        </section>

        <section class="section">
            <div class="card chat-card">
                <div id="chat-messages" class="chat-messages"></div>
                <div class="chat-input-container">
                    <input type="file" id="file-input" accept=".pdf" multiple style="display: none;">
                    <button id="upload-btn" class="upload-btn">📎</button>
                    <input type="text" id="message-input" class="message-input" placeholder="Ask a question..." required>
                    <button id="send-btn" class="send-btn">Send</button>
                </div>
            </div>
        </section>

    </div>

    <script>
        // No status loading needed
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/status', methods=['GET'])
def get_status():
    global index, chunks

    documents = []
    if chunks:
        # Count documents by source
        doc_counts = {}
        for chunk in chunks:
            source = chunk['source']
            doc_counts[source] = doc_counts.get(source, 0) + 1

        documents = [
            {'name': source, 'chunks': count}
            for source, count in doc_counts.items()
        ]

    return jsonify({
        'total_chunks': len(chunks) if chunks else 0,
        'total_documents': len(documents),
        'documents': documents,
        'index_loaded': index is not None
    })

@app.route('/upload', methods=['POST'])
def upload_files():
    global index, chunks

    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files')

    if not files or all(file.filename == '' for file in files):
        return jsonify({'error': 'No files selected'}), 400

    uploaded_files = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            uploaded_files.append(filename)

    if not uploaded_files:
        return jsonify({'error': 'No valid PDF files uploaded'}), 400

    # Re-index all documents
    try:
        file_paths = [os.path.join(app.config['UPLOAD_FOLDER'], f) for f in uploaded_files]
        documents = ingest.load_pdfs(file_paths)
        chunks = ingest.chunk_documents(documents)
        embeddings = embed.create_embeddings(chunks)
        index = embed.build_faiss_index(embeddings)

        # Save the updated index
        faiss.write_index(index, embed.INDEX_PATH)
        with open(embed.META_PATH, "wb") as f:
            pickle.dump(chunks, f)

        return jsonify({
            'message': f'Successfully uploaded and indexed {len(uploaded_files)} document(s). Total chunks: {len(chunks)}'
        })

    except Exception as e:
        return jsonify({'error': f'Indexing failed: {str(e)}'}), 500

@app.route('/ask', methods=['POST'])
def ask():
    global index, chunks

    if index is None or not chunks:
        return jsonify({
            'answer': 'No documents have been indexed yet. Please upload some PDF documents first.',
            'sources': []
        })

    data = request.get_json()
    query = data.get('query', '')

    if not query:
        return jsonify({'error': 'No query provided'}), 400

    # Retrieve relevant chunks
    retrieved_chunks = retrieve_chunks(query, index, chunks, k=10)

    # Build context
    context = "\n\n".join(
        f"[Source: {c['source']}]\n{c['text']}" for c in retrieved_chunks
    )

    # Get answer from Gemma
    answer = ask_gemma(context, query)

    # Detect query type for display
    from rag import detect_query_type
    query_type = detect_query_type(query)

    # Extract unique sources
    sources = list(set(c['source'] for c in retrieved_chunks))

    return jsonify({
        'answer': answer,
        'sources': sources,
        'query_type': query_type
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)