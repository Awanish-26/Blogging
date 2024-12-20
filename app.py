import os
import markdown
import requests
from flask import Flask, flash, request, redirect, render_template, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__, static_url_path='/static')

app.config['SECRET_KEY'] = 'cishbcib3iu!ubficlwebjbiuc'

UPLOAD_FOLDER = "markdowns"  # Relative path
ALLOWED_EXTENSIONS = {"md"}

# Correct configuration key
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# Check if the file has an allowed extension
def allowed_files(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# routes
# Serve the uploaded files
@app.route('/')
def index():
    notes = os.listdir(UPLOAD_FOLDER)
    return render_template("index.html", notes=notes)

# upload file


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        # Check if the 'file' part is in the request
        if 'file' not in request.files:
            flash('No file part', "error")
            return redirect(request.url)

        file = request.files['file']

        # Save the file if it has an allowed extension
        if file and allowed_files(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash(f'File "{filename}" uploaded successfully.', "success")
            return redirect(url_for('index'))

    return render_template("upload.html")


# serve the markdown file
@app.route("/markdown/<filename>")
def render_markdown(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            content = file.read()
            html_content = markdown.markdown(content)
            return render_template("markdown.html", content=html_content, filename=filename)
    else:
        flash('File not found', "error")
        return redirect(url_for('index'))


# check grammar
@app.route("/grammar/<filename>", methods=["GET", "POST"])
def check_grammar(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            content = file.read()
            response = requests.post(
                'https://api.languagetool.org/v2/check',
                data={'text': content, 'language': 'en'}
            )
            result = response.json()
            matches = result.get('matches', [])
            return render_template("grammar_check.html", content=content, matches=matches)
    else:
        flash('File not found', "error")
        return redirect(url_for('index'))
