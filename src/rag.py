import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import ollama

INDEX_PATH = "../data/faiss.index"
META_PATH = "../data/chunks.pkl"
EMBED_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "gemma:2b"


def load_index():
    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH, "rb") as f:
        chunks = pickle.load(f)
    return index, chunks


def retrieve_chunks(query, index, chunks, k=10):
    embedder = SentenceTransformer(EMBED_MODEL)
    query_embedding = embedder.encode([query])
    distances, indices = index.search(np.array(query_embedding), k)

    retrieved = []
    for idx in indices[0]:
        retrieved.append(chunks[idx])

    return retrieved


def detect_query_type(query):
    """Detect if query is asking for summary, analysis, or specific lookup"""
    query_lower = query.lower()

    if any(word in query_lower for word in ['summarize', 'summary', 'overview', 'key points']):
        return 'summary'
    elif any(word in query_lower for word in ['explain', 'what does', 'meaning', 'analyze']):
        return 'explanation'
    elif any(word in query_lower for word in ['risk', 'careful', 'warning', 'important']):
        return 'risk_analysis'
    else:
        return 'lookup'


def build_prompt(context, question, query_type):
    """
    Build an advanced, intelligent prompt for deep document analysis.
    Allow creative reasoning, implications, and unique insights.
    """
    base_instructions = (
        "You are an expert AI document analyst specializing in legal, financial, and compliance documents.\n"
        "Analyze the provided document context deeply and provide intelligent, insightful answers.\n"
        "- Base your response strictly on the document context.\n"
        "- Provide detailed analysis, implications, and key considerations.\n"
        "- Use natural, professional language suitable for business decisions.\n"
        "- Include unique insights, potential impacts, and recommendations where relevant.\n"
        "- Structure your response with clear sections using Markdown headings.\n"
        "- Use bullet points for lists and key facts.\n"
        "- If information is not in the context, clearly state that.\n"
        "- Go beyond surface-level answers; provide deeper understanding and implications.\n"
        "- Consider broader business, legal, or compliance implications.\n"
    )

    if query_type == 'summary':
        prompt = f"""{base_instructions}\n\nProvide a comprehensive executive summary of the document, highlighting key elements, implications, and strategic insights.\n\nDOCUMENT CONTEXT:\n{context}\n\nQUESTION: {question}\n\nEXECUTIVE SUMMARY:"""

    elif query_type == 'explanation':
        prompt = f"""{base_instructions}\n\nExplain the concept or clause in depth, including practical implications, potential issues, and recommendations.\n\nDOCUMENT CONTEXT:\n{context}\n\nQUESTION: {question}\n\nDETAILED EXPLANATION:"""

    elif query_type == 'risk_analysis':
        prompt = f"""{base_instructions}\n\nConduct a thorough risk assessment, identifying vulnerabilities, mitigation strategies, and compliance considerations.\n\nDOCUMENT CONTEXT:\n{context}\n\nQUESTION: {question}\n\nCOMPREHENSIVE RISK ANALYSIS:"""

    else:  # lookup
        prompt = f"""{base_instructions}\n\nProvide a thoughtful, analytical answer with context, implications, and any relevant insights.\n\nDOCUMENT CONTEXT:\n{context}\n\nQUESTION: {question}\n\nANALYTICAL ANSWER:"""

    return prompt

    return prompt


def ask_gemma(context, question):
    query_type = detect_query_type(question)
    prompt = build_prompt(context, question, query_type)

    # Use system message for better reasoning
    system_message = "You are an expert AI analyst. Think step-by-step, provide unique insights, and consider broader implications. Be thorough but concise."

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        options={"temperature": 0.7, "top_p": 0.9}  # Add creativity
    )
    return response["message"]["content"]


if __name__ == "__main__":
    index, chunks = load_index()

    print("Offline Document Intelligence System")
    print("Type 'exit' to quit.\n")

    while True:
        query = input("Ask a question: ")
        if query.lower() == "exit":
            break

        retrieved_chunks = retrieve_chunks(query, index, chunks)

        context = "\n\n".join(
            f"[Source: {c['source']}]\n{c['text']}" for c in retrieved_chunks
        )

        answer = ask_gemma(context, query)

        print("\n--- ANSWER ---")
        print(answer)
        print("\n--- SOURCES ---")
        for c in retrieved_chunks:
            print(f"- {c['source']}")
        print("\n")
