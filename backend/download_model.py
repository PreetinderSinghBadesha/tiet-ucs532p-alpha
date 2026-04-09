import os
import requests
import bz2

def download_file(url, filename):
    print(f"Downloading {url} to {filename}...")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print("Download complete.")
    else:
        print(f"Failed to download. Status code: {response.status_code}")

def extract_bz2(filename, output_filename):
    print(f"Extracting {filename} to {output_filename}...")
    with bz2.BZ2File(filename) as fr, open(output_filename, 'wb') as fw:
        for chunk in iter(lambda: fr.read(1024 * 1024), b''):
            fw.write(chunk)
    print("Extraction complete.")

if __name__ == "__main__":
    model_url = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
    models_dir = os.path.join("d:\\projects\\dermaai\\backend", "models")
    os.makedirs(models_dir, exist_ok=True)
    
    bz2_path = os.path.join(models_dir, "shape_predictor_68_face_landmarks.dat.bz2")
    model_path = os.path.join(models_dir, "shape_predictor_68_face_landmarks.dat")
    
    if not os.path.exists(model_path):
        if not os.path.exists(bz2_path):
            download_file(model_url, bz2_path)
        extract_bz2(bz2_path, model_path)
        os.remove(bz2_path)
        print("Model ready.")
    else:
        print("Model already exists.")
