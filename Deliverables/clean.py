import csv

# Input and output file names
input_file = r"D:\Final Year Project\Final-Year-Project-Shared\automate_scrapping\GPR.csv"  # Replace with your actual file name
output_file = "clean_data.csv"

def is_valid_facebook_link(link):
    """
    Check if the provided link is a valid Facebook link.
    """
    return "facebook.com" in link.lower()

def clean_csv(input_file, output_file):
    with open(input_file, mode='r', newline='', encoding='utf-8') as infile, \
         open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # Write the header for the output file
        writer.writerow(["Email", "Name", "FB Link", "Personality"])

        # Skip the header in the input file
        next(reader)

        for row in reader:
            try:
                email = row[1].strip()
                name = row[2].strip()
                fb_link = row[3].strip()
                personality = row[29].strip()  # Adjusting for 0-based index

                if is_valid_facebook_link(fb_link):
                    writer.writerow([email, name, fb_link, personality])
            except IndexError:
                # Skip rows that don't have enough columns
                continue

# Run the cleaning process
clean_csv(input_file, output_file)
print(f"Cleaned data has been saved to {output_file}.")
