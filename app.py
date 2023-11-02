import os
import requests
from flask import Flask, render_template, request, redirect, url_for, send_file
from PIL import Image

app = Flask(__name__)

# Replace 'INSERT_YOUR_API_KEY_HERE' with your actual Remove.bg API key
REMOVE_BG_API_KEY = 'jJ4k6R3Sd2z2xd6waXWqW41m'

# Define the folder where uploaded images will be stored
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create the uploads folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Create a dictionary to store original filenames and their processed versions
original_filenames = {}

def remove_background_with_remove_bg(api_key, input_image_path, output_image_path):
    headers = {'X-Api-Key': api_key}

    with open(input_image_path, 'rb') as image_file:
        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            headers=headers,
            files={'image_file': image_file},
            data={'size': 'auto'},
        )

        if response.status_code == requests.codes.ok:
            with open(output_image_path, 'wb') as out:
                out.write(response.content)
            return True
        else:
            return False

@app.route('/', methods=['GET', 'POST'])
def index():
    progress = 0
    processed_images = {}

    if request.method == 'POST':
        if 'image' not in request.files:
            return redirect(url_for('index'))

        image_file = request.files['image']
        if image_file.filename == '':
            return redirect(url_for('index'))
        original_filename = image_file.filename
        input_image_path = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
        image_file.save(input_image_path)
        output_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.png')
        success = remove_background_with_remove_bg(REMOVE_BG_API_KEY, input_image_path, output_image_path)

        if success:
            desired_sizes = [(240, 240), (320, 320), (512, 512), (2880 , 1800) ]

            for size in desired_sizes:
                resized_image = Image.open(output_image_path)
                resized_image.thumbnail(size, Image.BILINEAR)  
                processed_filename = f'{os.path.splitext(original_filename)[0]}_{size[0]}x{size[1]}.png'

                resized_image_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
                resized_image.save(resized_image_path, format="PNG")
                original_filenames[original_filename] = processed_filename
                processed_images[f"{size[0]}x{size[1]}"] = resized_image_path

            progress = 100

    return render_template('index.html', processed_images=processed_images, progress=progress)

@app.route('/processed_images/<filename>')
def processed_image(filename):
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(image_path, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
