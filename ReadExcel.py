import pyexcel

# Read the data from an Excel file (can be .xls, .xlsx, .ods, .csv)
records = pyexcel.get_records(file_name="your_file.xlsx")

for record in records:
    print(record)
