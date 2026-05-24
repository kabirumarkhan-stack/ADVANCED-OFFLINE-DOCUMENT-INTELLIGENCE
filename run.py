import os
import sys
import subprocess

def ensure_data_dirs():
    os.makedirs(os.path.join('data', 'documents'), exist_ok=True)

def build_index_if_needed():
    index_path = os.path.join('data', 'faiss.index')
    meta_path = os.path.join('data', 'chunks.pkl')
    if not (os.path.exists(index_path) and os.path.exists(meta_path)):
        print('No FAISS index found. Building index...')
        subprocess.run([sys.executable, os.path.join('src', 'embed.py')], check=True)
    else:
        print('FAISS index found. Skipping embedding.')
    #the main project invoke File that can run the Entire project

def run_flask():
    os.chdir('src')
    os.environ['FLASK_ENV'] = 'development'
    subprocess.run([sys.executable, 'app.py'])

def main():
    ensure_data_dirs()
    build_index_if_needed()
    run_flask()

if __name__ == '__main__':
    main()
