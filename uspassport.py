from passporteye import read_mrz  # passport verification api
import sys, re, csv, os

"""
info format: country, 2-letter-abbreviation, 3-letter-abbreviation, country code, ISO 3166 standard, 
             region, sub-region, intermediate-region, region code, sub-region code, intermediate-region code,  
"""
country_info = {"country":"","abbreviation-2":"","abbreviation-3":"","country-code":"","iso_3166-2":"","region":"","sub-region":"","intermediate-region":"","region-code":"","sub-region-code":"","intermediate-region-code":""}
countries_file = 'countries.csv'

# parsing information from passport using mrz
def parser(file):
    try:
        file = sys.argv[1] # getting file name
        mrz = read_mrz(file)
        data = mrz.to_dict()

        holder = dict()
        holder["Given names"] = get_first_name(data.get("names").upper())
        holder["Surname"] = data.get("surname").upper()
        holder["country code"] = data.get("country_code")
        holder["country"] = check_country(holder.get("country_code"))
        holder["nationality"] = check_country(data.get("nationality"))
        holder["id"] = data.get("number")
        holder["sex"] = data.get("sex")
        return holder

    except FileNotFoundError:
        return print("File Does Not Exist")
    except TypeError:
        return print("Image Unreadable")

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


def get_first_name(name):
    target = re.compile("([^\s\w]|_)+")
    name = target.sub(", name").strip()
    return name


def check_country(issue_country):
    extract(countries_file, issue_country)
    for item in country_info:
        if item["abbreviation-3"] == issue_country:
            return item["country"]
    return issue_country


if __name__ == "__main__":
    file = os.path.join('data', 'sample-passport.jpg')
    parsed = parser(file)
    print(parsed)