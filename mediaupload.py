import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image
from github import Github

# Configuration
GITHUB_TOKEN = "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"  # Replace with your GitHub token
REPO_NAME = "snaps"  # Replace with your repository name
BRANCH = "main"  # Replace with your branch name
IMAGE_QUALITY = 40  # Quality for compressed images (0-100)
VIDEO_CRF = 40  # CRF value for video compression (lower = better quality)

# Supported file extensions
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif")
VIDEO_EXTENSIONS = (".mp4", ".mov", ".webm")

# Create media folder
MEDIA_FOLDER = "media"
os.makedirs(MEDIA_FOLDER, exist_ok=True)

def compress_image(input_path, output_path):
    """Compress an image using PIL"""
    try:
        with Image.open(input_path) as img:
            img.save(output_path, quality=IMAGE_QUALITY, optimize=True)
        return True
    except Exception as e:
        log_message(f"Failed to compress image {input_path}: {str(e)}")
        return False

def compress_video(input_path, output_path):
    """Compress a video using ffmpeg"""
    try:
        command = [
            "ffmpeg", "-i", input_path, "-vcodec", "libx264", "-crf", str(VIDEO_CRF), "-preset", "medium", output_path
        ]
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        log_message(f"Failed to compress video {input_path}: {str(e)}")
        return False

def upload_to_github():
    """Upload the media folder to GitHub repository"""
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_user().get_repo(REPO_NAME)
        
        for file_name in os.listdir(MEDIA_FOLDER):
            file_path = os.path.join(MEDIA_FOLDER, file_name)
            with open(file_path, "rb") as file:
                content = file.read()
            
            repo_path = f"{MEDIA_FOLDER}/{file_name}"
            try:
                repo.get_contents(repo_path)
                log_message(f"File {file_name} already exists in the repository. Skipping upload.")
            except:
                repo.create_file(repo_path, f"Upload {file_name}", content, branch=BRANCH)
                log_message(f"Uploaded {file_name} to GitHub.")

        messagebox.showinfo("Success", "All files uploaded to GitHub successfully!")
    except Exception as e:
        messagebox.showerror("GitHub Error", f"Failed to upload files: {str(e)}")

def select_files():
    """Open a file dialog to select multiple files"""
    file_paths = filedialog.askopenfilenames(
        title="Select Media Files",
        filetypes=[("All Files", "*.*"), ("Image Files", "*.jpg;*.jpeg;*.png;*.gif"), ("Video Files", "*.mp4;*.mov;*.webm")]
    )
    return file_paths

def compress_and_upload():
    """Compress selected files and upload to GitHub"""
    file_paths = select_files()
    if not file_paths:
        messagebox.showwarning("No Files Selected", "Please select at least one file.")
        return
    
    for file in os.listdir(MEDIA_FOLDER):
        os.remove(os.path.join(MEDIA_FOLDER, file))
    
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_name)[1].lower()
        output_path = os.path.join(MEDIA_FOLDER, file_name)

        if file_ext in IMAGE_EXTENSIONS:
            if compress_image(file_path, output_path):
                log_message(f"Compressed image: {file_name}")
        elif file_ext in VIDEO_EXTENSIONS:
            if compress_video(file_path, output_path):
                log_message(f"Compressed video: {file_name}")
    
    upload_to_github()

def log_message(message):
    log_text.insert(tk.END, message + "\n")
    log_text.yview(tk.END)

# GUI Setup
root = tk.Tk()
root.title("Media Compressor and Uploader")
root.geometry("600x400")

tk.Label(root, text="Media Compressor and Uploader", font=("Arial", 14)).pack(pady=10)

log_text = scrolledtext.ScrolledText(root, height=10, width=70)
log_text.pack(pady=10)

tk.Button(root, text="Select Files and Upload", command=compress_and_upload).pack(pady=10)

root.mainloop()
