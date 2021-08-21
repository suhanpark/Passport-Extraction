from flask import Flask, request, make_response, jsonify, render_template
from extracter import *

UPLOAD_FOLDER = '/uploads'
EDIT_FOLDER = '/edit'

app = Flask(__name__)

log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_fmt)

@app.route('/')
def index():
    return render_template(os.path.join('templates', 'index.html'))

@app.route('/')
def status():
    return 'Welcome! The endpoint is at <b>/process</b>'

@app.route('/process', methods=['POST'])
def process():
    
    imgfile = request.files.get('imgfile', None)
    if not imgfile:
        return make_response("Missing file parameter", 400)

    filename = secure_filename(imgfile.filename)
    full_path = os.path.join(UPLOAD_FOLDER, filename)
    imgfile.save(full_path)

    # Extract informations with PassportEye
    p = MRZPipeline(full_path, extra_cmdline_params='--oem 0')
    mrz = p.result

    if mrz is None:
        return make_response("Can not read image", 400)

    mrz_data = mrz.to_dict()

    # Convert image to text
    full_content = img_to_str(full_path)
    # logging.info('full image content = %s' %(full_content))

    all_infos = {}
    all_infos['last_name'] = mrz_data['surname'].upper()
    all_infos['first_name'] = mrz_data['names'].upper()
    all_infos['country_code'] = mrz_data['country']
    all_infos['country'] = get_country(all_infos['country_code'])
    all_infos['nationality'] = get_country(mrz_data['nationality'])
    all_infos['number'] = mrz_data['number']
    all_infos['sex'] = mrz_data['sex']

    # all_infos['full_text'] = full_content
    valid_score = mrz_data['valid_score']

    # Trying to extract full name
    if all_infos['last_name'] in full_content:
        splitted_fulltext = full_content.split("\n")
        for w in splitted_fulltext:
            if all_infos['last_name'] in w:
                all_infos['last_name'] = w
                continue

    splitted_firstname = all_infos['first_name'].split(" ")
    if splitted_firstname[0] in full_content:
        splitted_fulltext = full_content.split("\n")
        for w in splitted_fulltext:
            if splitted_firstname[0] in w:
                all_infos['first_name'] = get_name(w)
                continue

    os.remove(full_path)
    return jsonify(all_infos)
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)