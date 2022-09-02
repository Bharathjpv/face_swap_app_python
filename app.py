from face_swap_app.face_app import face_app
import os
from flask import Flask, render_template, request
import cv2
import logging


logger = logging.getLogger(__name__)


app = Flask('__name__')

IMG_FOLDER = os.path.join('static', 'images')

app.config['UPLOAD_FOLDER'] = IMG_FOLDER

ROOT = os.getcwd()

source_path = os.path.join(ROOT, 'images/src_img.jpg')
dest_path = os.path.join(ROOT, 'images/dst_img.jpg')

# source_path = os.path.join(ROOT, 'DiCaprio.jpg')
# dest_path = os.path.join(ROOT, 'photo.jpg')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/temp', methods=['GET', 'POST'])
def temp():
    source_img = request.files['img1']
    destination_img = request.files['img2']
    source_img.save(os.path.join(ROOT, 'images/src_img.jpg'))
    destination_img.save(os.path.join(ROOT, 'images/dst_img.jpg'))
    logger.info('Image accepted form user')
    fp = face_app(source_path, dest_path)
    fp.run()

    display_image = os.path.join(app.config['UPLOAD_FOLDER'], 'modified.jpg')
    logger.info('generated image returned')
    return render_template("result.html", user_image=display_image)


# def main():
#     fp = face_app(source_path, dest_path)
#     fp.run()


if __name__ == "__main__":
    app.run(debug=True)