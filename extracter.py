from werkzeug.utils import secure_filename
from passporteye.mrz.image import MRZPipeline
from passporteye import read_mrz
from PIL import Image
import os, json, logging, pytesseract, cv2, re, csv
import numpy as np


"""
info format: country, 2-letter-abbreviation, 3-letter-abbreviation, country code, ISO 3166 standard, 
             region, sub-region, intermediate-region, region code, sub-region code, intermediate-region code,  
"""
country_info = {"country":"","abbreviation-2":"","abbreviation-3":"","country-code":"","iso_3166-2":"","region":"","sub-region":"","intermediate-region":"","region-code":"","sub-region-code":"","intermediate-region-code":""}
countries_file = 'countries.csv'

def extract(filename, country):
    f = os.path.join('data', filename)
    fp = open(f, "r")
    reader = csv.reader(fp)
    fp.readline()
    for line in reader: 
        if line[0] == country:
            country_info["country"] = line[0]
            country_info["abbreviation-2"] = line[1]
            country_info["abbreviation-3"] = line[2]
            country_info["country-code"] = line[3]
            country_info["iso_3166-2"] = line[4]
            country_info["country"] = line[5]
            country_info["region"] = line[6]
            country_info["sub-region"] = line[7]
            country_info["intermediate-region"] = line[8]
            country_info["region-code"] = line[9]
            country_info["sub-region-code"] = line[10]
            country_info["intermediate-region-code"] = line[11]
            break


def get_name(name):
    target = re.compile("([^\s\w]|_)+")
    name = target.sub('', name).strip()
    return name


def get_country(issue_country):
    extract(countries_file, issue_country)
    if country_info["country"] == issue_country:
        return country_info["country"]
    return issue_country

def img_to_str(file_path):
    """Convert image to text using tesseract OCR"""

    img = cv2.imread(file_path)

    # Extract the file name without the file extension
    file_name = os.path.basename(file_path).split('.')[0]
    file_name = file_name.split()[0]

    # Create a directory for outputs
    output_path = os.path.join(EDIT_FOLDER, file_name)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    # Convert to gray
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply dilation and erosion to remove some noise
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)
    # Apply blur to smooth out the edges
    img = cv2.GaussianBlur(img, (5, 5), 0)
    # Apply threshold to get image with only b&w (binarization)
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    # Save the filtered image in the output directory
    save_path = os.path.join(output_path, file_name + "_filter.jpg")
    cv2.imwrite(save_path, img)

    # Recognize text with tesseract for python
    result = pytesseract.image_to_string(img, lang="eng")

    os.remove(save_path)
    return result.upper()