import os
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from tqdm import tqdm
import textwrap
from PyPDF2 import PdfReader


def main(file_struct):
    print("hello")

    cwd = os.getcwd()

    stat_file = f"{cwd}/statfile.txt"
    

    for directory, files in file_struct.items():
        
        
        in_dir = f"{cwd}/txtfiles_{directory}"
        out_dir = f"{cwd}/pdfs_{directory}"

        
        create_dir = os.path.isdir(out_dir)
        if not create_dir:
            os.system(f"mkdir {cwd}/pdfs_{directory}")
        else:
            rm_cmd = f"rm -rf {cwd}/pdfs_{directory}"
            os.system(rm_cmd)
            os.system(f"mkdir {cwd}/pdfs_{directory}")
    
        if os.path.isdir(in_dir):
            total_data_size = batch_convert_txt_to_pdf(in_dir, out_dir)
            print(f"All .txt files have been converted and saved in '{out_dir}'.")
            data_size_total_mb = total_data_size/1048576
            with open(stat_file, "at") as statwriter:
                statwriter.write(f"{directory} --- contained {data_size_total_mb}MB as pdf\n")
            
        else:
            print(f"Invalid input directory. {in_dir}")

        if not out_dir:
            print("No folder selected.")
            return []
        
        file_paths = []
        for dirpath, _, filenames in os.walk(out_dir):
            for file in filenames:
                file_paths.append(os.path.join(dirpath, file))

        page_count = 0
        for path in file_paths:
            page_count += count_pages(path)

        with open(stat_file, "at") as statwriter:
            statwriter.write(f"{directory} --- contained {page_count} pdf-pages\n")
        




def get_all_file_paths():
    # Create a tkinter root window (hidden)
    root = Tk()
    root.withdraw()  # Hide the root window
    root.attributes('-topmost', True)  # Bring the dialog to the front

    # Open a dialog to select a folder
    folder_path = askdirectory(title="Select a Folder")

    if not folder_path:
        print("No folder selected.")
        return []

    # Walk through the directory and collect all file paths
    file_paths = []
    for dirpath, _, filenames in os.walk(folder_path):
        for file in filenames:
            file_paths.append(os.path.join(dirpath, file))

    return file_paths


def count_pages(path):
    reader = PdfReader(path)
    return len(reader.pages)

def convert_txt_to_pdf(txt_file_path, output_folder):
    """
    Converts a .txt file to a PDF with uniform formatting.

    Args:
        txt_file_path (str): Path to the .txt file.
        output_folder (str): Folder to save the generated PDF.

    Returns:
        str: Path to the generated PDF.
    """
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Extract the filename without the extension
    base_name = os.path.splitext(os.path.basename(txt_file_path))[0]
    pdf_file_path = os.path.join(output_folder, f"{base_name}.pdf")

    # Create a PDF canvas
    c = canvas.Canvas(pdf_file_path, pagesize=LETTER)
    width, height = LETTER

    # Set up formatting
    font_name = "Helvetica"
    font_size = 12
    line_height = font_size + 2
    margin = 50
    current_y = height - margin

    c.setFont(font_name, font_size)

    # Read the text file and write content to the PDF

    with open(txt_file_path, "r", encoding="utf-8") as txt_file:
        for line in txt_file:
            chunk_size = 10000  # Process 10,000 characters at a time
            chunks = [line[i:i + chunk_size] for i in range(0, len(line), chunk_size)]

            wrapped_data = []
            for chunk in chunks:
                wrapped_data.extend(textwrap.wrap(chunk, width=70, break_long_words=True, break_on_hyphens=True))


            for wrap in wrapped_data:
        
        
                # Check if the line fits on the page, if not, create a new page
                if current_y < margin:
                    c.showPage()
                    c.setFont(font_name, font_size)
                    current_y = height - margin

                # Write the line to the PDF
                c.drawString(margin, current_y, wrap.strip())
                current_y -= line_height

    # Save the PDF
    c.save()
    return pdf_file_path

def batch_convert_txt_to_pdf(input_folder, output_folder):
    """
    Converts all .txt files in the input folder to PDFs in the output folder.

    Args:
        input_folder (str): Folder containing .txt files.
        output_folder (str): Folder to save the generated PDFs.
    """
    data_size_total = 0
    for dirpath, _, filenames in os.walk(input_folder):
        for file in tqdm(filenames):
            if file.lower().endswith(".txt"):
                txt_file_path = os.path.join(dirpath, file)
                data_size_total += os.path.getsize(convert_txt_to_pdf(txt_file_path, output_folder))
    return data_size_total

if __name__ == "__main__":
    main()
