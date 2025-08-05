import json

JSON_PATH = "Sample.json"
TXT_PATH = "Sample.txt"

MATCH_FIELDS = [
    'FirstName', 'LastName', 'DOB', 'Gender', 'Address1', 'City', 'State', 'Zip',
    'Phone1', 'SubscriberID', 'EncounterId', 'MedicareHIC'
]

def load_json(json_path):
    print(f"Loading JSON file: {json_path}")
    with open(json_path, 'r') as f:
        data = json.load(f)
    print("JSON file loaded successfully.")
    return data

def load_txt(txt_path):
    print(f"Loading TXT file: {txt_path}")
    with open(txt_path, 'r') as f:
        lines = f.readlines()
    header = lines[0].strip().split('|')
    rows = [dict(zip(header, line.strip().split('|'))) for line in lines[1:]]
    print(f"Loaded {len(rows)} rows from TXT file.")
    return rows

def extract_json_patient(json_data):
    print("Extracting patient data from JSON...")
    doc = json_data['Vitals']['ClinicalDocument'][0]
    patient = doc['PatientIdentification']
    name = patient['Name'][0]
    given = name['given'][0]['valueString']
    family = name['Family']
    birth_date = patient['BirthDate']
    gender = patient['Gender']
    address = patient['Address'][0]
    phone = patient['Telecommunication'][0]['ValueSt']
    identifiers = {id['Type']: id['IdNumber'] for id in patient['Identifiers']}
    patient_dict = {
        'FirstName': given,
        'LastName': family,
        'DOB': birth_date.split()[0],
        'Gender': gender,
        'Address1': address['AddressLine'],
        'City': address['City'],
        'State': address['State'],
        'Zip': address['ZipCode'],
        'Phone1': phone,
        'SubscriberID': identifiers.get('MRN', ''),
        'EncounterId': identifiers.get('Encounter ID', ''),
        'MedicareHIC': identifiers.get('Medicare ID', ''),
    }
    print("Patient data extracted from JSON.")
    return patient_dict

def verify_txt_with_json(json_patient, txt_rows):
    print("Starting verification of TXT rows against JSON patient data...")
    for idx, row in enumerate(txt_rows, 1):
        match = True
        for key in MATCH_FIELDS:
            txt_value = str(row.get(key, '')).strip()
            json_value = str(json_patient.get(key, '')).strip()
            if txt_value != json_value:
                match = False
                print(f"Row {idx}: Field '{key}' does not match. TXT='{txt_value}' JSON='{json_value}'")
        if match:
            print(f"Row {idx}: All matching fields found!")
        else:
            print(f"Row {idx}: Not all fields match JSON patient.")

def main():
    json_data = load_json(JSON_PATH)
    txt_rows = load_txt(TXT_PATH)
    json_patient = extract_json_patient(json_data)
    verify_txt_with_json(json_patient, txt_rows)

if __name__ == "__main__":
    main()