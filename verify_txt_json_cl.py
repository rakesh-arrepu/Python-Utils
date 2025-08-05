import json
import csv
from datetime import datetime

def read_json_file(json_file_path):
    """Read and parse the JSON file"""
    try:
        with open(json_file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return None

def read_txt_file(txt_file_path):
    """Read the pipe-delimited TXT file"""
    try:
        with open(txt_file_path, 'r') as file:
            reader = csv.DictReader(file, delimiter='|')
            return list(reader)
    except Exception as e:
        print(f"Error reading TXT file: {e}")
        return None

def extract_json_fields(json_data):
    """Extract key fields from JSON data"""
    try:
        vitals = json_data.get('Vitals', {})
        clinical_doc = vitals.get('ClinicalDocument', [{}])[0]
        patient_id = clinical_doc.get('PatientIdentification', {})
        
        # Extract patient identifiers
        identifiers = patient_id.get('Identifiers', [])
        mrn = None
        medicare_id = None
        encounter_id = None
        
        for identifier in identifiers:
            if identifier.get('Type') == 'MRN':
                mrn = identifier.get('IdNumber')
            elif identifier.get('Type') == 'Medicare ID':
                medicare_id = identifier.get('IdNumber')
            elif identifier.get('Type') == 'Encounter ID':
                encounter_id = identifier.get('IdNumber')
        
        # Extract name
        names = patient_id.get('Name', [{}])
        first_name = None
        last_name = None
        if names:
            name = names[0]
            last_name = name.get('Family')
            given_names = name.get('given', [])
            if given_names:
                first_name = given_names[0].get('valueString')
        
        # Extract address
        addresses = patient_id.get('Address', [{}])
        address_line = None
        city = None
        state = None
        zip_code = None
        if addresses:
            address = addresses[0]
            address_line = address.get('AddressLine')
            city = address.get('City')
            state = address.get('State')
            zip_code = address.get('ZipCode')
        
        # Extract other fields
        birth_date = patient_id.get('BirthDate')
        gender = patient_id.get('Gender')
        
        # Extract phone
        telecoms = patient_id.get('Telecommunication', [])
        phone = None
        for telecom in telecoms:
            if telecom.get('System') == 'Phone':
                phone = telecom.get('ValueSt')
                break
        
        # Extract practitioner tax ID
        practitioners = clinical_doc.get('Practitioner', [])
        tax_id = None
        if practitioners:
            tax_id = practitioners[0].get('TaxIdentificationNumber')
        
        # Extract vitals key
        vitals_key = vitals.get('VitalsKey')
        
        return {
            'VitalsKey': vitals_key,
            'MRN': mrn,
            'MedicareID': medicare_id,
            'EncounterID': encounter_id,
            'FirstName': first_name,
            'LastName': last_name,
            'BirthDate': birth_date,
            'Gender': gender,
            'AddressLine': address_line,
            'City': city,
            'State': state,
            'ZipCode': zip_code,
            'Phone': phone,
            'TaxID': tax_id
        }
    except Exception as e:
        print(f"Error extracting JSON fields: {e}")
        return None

def format_date(date_str):
    """Format date string for comparison"""
    if not date_str:
        return None
    try:
        # Handle different date formats
        if ' ' in date_str:
            date_str = date_str.split(' ')[0]  # Remove time part
        return date_str
    except:
        return date_str

def verify_record_match(json_fields, txt_record):
    """Verify if a TXT record matches the JSON data"""
    matches = {}
    
    # Check MRN (EntityPatientID in TXT)
    matches['MRN'] = json_fields.get('MRN') == txt_record.get('EntityPatientID')
    
    # Check First Name
    matches['FirstName'] = json_fields.get('FirstName') == txt_record.get('FirstName')
    
    # Check Last Name
    matches['LastName'] = json_fields.get('LastName') == txt_record.get('LastName')
    
    # Check Birth Date
    json_dob = format_date(json_fields.get('BirthDate'))
    txt_dob = format_date(txt_record.get('DOB'))
    matches['BirthDate'] = json_dob == txt_dob
    
    # Check Gender
    matches['Gender'] = json_fields.get('Gender') == txt_record.get('Gender')
    
    # Check Address
    matches['Address'] = json_fields.get('AddressLine') == txt_record.get('Address1')
    
    # Check City
    matches['City'] = json_fields.get('City') == txt_record.get('City')
    
    # Check State
    matches['State'] = json_fields.get('State') == txt_record.get('State')
    
    # Check Zip Code
    matches['ZipCode'] = json_fields.get('ZipCode') == txt_record.get('Zip')
    
    # Check Phone
    matches['Phone'] = json_fields.get('Phone') == txt_record.get('Phone1')
    
    # Check Tax ID (RenderingProviderTaxID in TXT)
    matches['TaxID'] = json_fields.get('TaxID') == txt_record.get('RenderingProviderTaxID')
    
    return matches

def main():
    """Main function to verify matching records"""
    print("=== JSON to TXT Record Verification ===\n")
    
    # File paths
    json_file = 'Sample.json'
    txt_file = 'Sample.txt'
    
    # Read files
    print("Reading JSON file...")
    json_data = read_json_file(json_file)
    if not json_data:
        return
    
    print("Reading TXT file...")
    txt_data = read_txt_file(txt_file)
    if not txt_data:
        return
    
    # Extract JSON fields
    print("Extracting fields from JSON...")
    json_fields = extract_json_fields(json_data)
    if not json_fields:
        return
    
    print("\n=== JSON Fields Extracted ===")
    for key, value in json_fields.items():
        print(f"{key}: {value}")
    
    print(f"\n=== Verifying {len(txt_data)} TXT Records ===\n")
    
    # Track statistics
    total_records = len(txt_data)
    matching_records = 0
    partial_matches = 0
    
    # Verify each record
    for i, txt_record in enumerate(txt_data, 1):
        print(f"--- Record {i} ---")
        print(f"EntityPatientID: {txt_record.get('EntityPatientID')}")
        print(f"Name: {txt_record.get('FirstName')} {txt_record.get('LastName')}")
        
        # Verify matches
        matches = verify_record_match(json_fields, txt_record)
        
        # Count matching fields
        matching_fields = sum(1 for match in matches.values() if match)
        total_fields = len(matches)
        
        # Determine match status
        if matching_fields == total_fields:
            status = "FULL MATCH ✓"
            matching_records += 1
        elif matching_fields > 0:
            status = f"PARTIAL MATCH ({matching_fields}/{total_fields} fields)"
            partial_matches += 1
        else:
            status = "NO MATCH ✗"
        
        print(f"Status: {status}")
        
        # Print detailed field comparison for matches
        if matching_fields > 0:
            print("Field Matches:")
            for field, is_match in matches.items():
                symbol = "✓" if is_match else "✗"
                json_val = json_fields.get(field, 'N/A')
                txt_field_map = {
                    'MRN': 'EntityPatientID',
                    'FirstName': 'FirstName',
                    'LastName': 'LastName',
                    'BirthDate': 'DOB',
                    'Gender': 'Gender',
                    'Address': 'Address1',
                    'City': 'City',
                    'State': 'State',
                    'ZipCode': 'Zip',
                    'Phone': 'Phone1',
                    'TaxID': 'RenderingProviderTaxID'
                }
                txt_field = txt_field_map.get(field, field)
                txt_val = txt_record.get(txt_field, 'N/A')
                print(f"  {field}: {symbol} JSON='{json_val}' | TXT='{txt_val}'")
        
        print()  # Empty line for readability
    
    # Print summary
    print("=== VERIFICATION SUMMARY ===")
    print(f"Total records processed: {total_records}")
    print(f"Full matches found: {matching_records}")
    print(f"Partial matches found: {partial_matches}")
    print(f"No matches: {total_records - matching_records - partial_matches}")
    
    if matching_records > 0:
        print(f"\n✓ SUCCESS: Found {matching_records} complete matching record(s)!")
    else:
        print(f"\n⚠ WARNING: No complete matches found. Check data consistency.")

if __name__ == "__main__":
    main()
