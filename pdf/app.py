from flask import Flask, render_template, request, send_file
import os
from PIL import Image
from fpdf import FPDF
import json
import pikepdf # Added for PDF compression
import fitz  # PyMuPDF for better compression
from io import BytesIO
import secrets

app = Flask(__name__)

# Configuration for different environments
if os.environ.get('PYTHONANYWHERE_DOMAIN'):
    # Production settings for PythonAnywhere
    app.config['UPLOAD_FOLDER'] = '/home/nity70/mysite/uploads'
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
    app.config['DEBUG'] = False
else:
    # Development settings
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
    app.config['SECRET_KEY'] = 'dev-secret-key'
    app.config['DEBUG'] = True

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# File validation
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

# Error handlers for production
@app.errorhandler(404)
def not_found_error(error):
    return "Page not found", 404

@app.errorhandler(500)
def internal_error(error):
    return "Internal server error", 500

@app.errorhandler(413)
def too_large(error):
    return "File too large. Maximum size is 50MB.", 413

@app.route('/pdfcompress', methods=['GET', 'POST'])
def pdfcompress():
    if request.method == 'POST':
        uploaded_file = request.files.get('pdf_file')
        compression_level = request.form.get('compression_level', 'medium')

        if not uploaded_file or uploaded_file.filename == '':
            return "No file selected!", 400

        # Validate file type
        if not allowed_file(uploaded_file.filename):
            return "Invalid file type! Only PDF files are allowed.", 400

        original_filename = uploaded_file.filename
        temp_pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
        uploaded_file.save(temp_pdf_path)

        compressed_pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], f"compressed_{original_filename}")
        
        try:
            # Open the PDF with PyMuPDF
            pdf_doc = fitz.open(temp_pdf_path)
            
            # Get original file size for comparison
            original_size = os.path.getsize(temp_pdf_path)
            print(f"Original PDF size: {original_size / 1024 / 1024:.2f} MB")
            
            # Aggressive image compression for each page
            for page_num in range(pdf_doc.page_count):
                page = pdf_doc[page_num]
                
                # Get all images on the page
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    try:
                        # Get image data
                        xref = img[0]
                        base_image = pdf_doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        
                        # Convert to PIL Image for compression
                        img_data = BytesIO(image_bytes)
                        pil_image = Image.open(img_data)
                        
                        # Compress image based on compression level
                        output = BytesIO()
                        if compression_level == 'low':
                            quality = 85
                            optimize = True
                        elif compression_level == 'medium':
                            quality = 70
                            optimize = True
                        else:  # high compression
                            quality = 50
                            optimize = True
                            # Convert to RGB if RGBA (removes transparency)
                            if pil_image.mode in ('RGBA', 'LA'):
                                pil_image = pil_image.convert('RGB')
                        
                        # Save compressed image
                        if image_ext.upper() in ['PNG', 'TIFF']:
                            # Convert PNG/TIFF to JPEG for better compression
                            if pil_image.mode in ('RGBA', 'LA'):
                                pil_image = pil_image.convert('RGB')
                            pil_image.save(output, format='JPEG', quality=quality, optimize=optimize)
                            new_image_bytes = output.getvalue()
                        else:
                            pil_image.save(output, format='JPEG', quality=quality, optimize=optimize)
                            new_image_bytes = output.getvalue()
                        
                        # Replace image in PDF only if compression actually reduced size
                        if len(new_image_bytes) < len(image_bytes):
                            pdf_doc.update_stream(xref, new_image_bytes)
                            print(f"Compressed image {img_index} on page {page_num}: {len(image_bytes)} -> {len(new_image_bytes)} bytes")
                        
                    except Exception as img_error:
                        print(f"Error processing image {img_index} on page {page_num}: {img_error}")
                        continue
            
            # Set compression parameters based on level
            if compression_level == 'low':
                garbage_level = 1
            elif compression_level == 'medium':
                garbage_level = 3
            else:  # high compression
                garbage_level = 4
            
            # Save with aggressive compression options
            pdf_doc.save(
                compressed_pdf_path,
                garbage=garbage_level,           # Remove unused objects
                deflate=True,                    # Compress streams
                clean=True,                      # Clean up the file structure
                linear=True if compression_level == 'high' else False,  # Linearize for high compression
                no_new_id=True,                  # Don't generate new ID
                appearance=False,                # Remove appearance streams
                encryption=fitz.PDF_ENCRYPT_NONE # No encryption
            )
            
            pdf_doc.close()
            
            # Check compressed file size
            if os.path.exists(compressed_pdf_path):
                compressed_size = os.path.getsize(compressed_pdf_path)
                compression_ratio = (1 - compressed_size / original_size) * 100
                print(f"Compressed PDF size: {compressed_size / 1024 / 1024:.2f} MB")
                print(f"Compression ratio: {compression_ratio:.1f}%")
            
        except Exception as e:
            return f"Error during compression: {str(e)}", 500
        finally:
            # Clean up temp file
            if os.path.exists(temp_pdf_path):
                try:
                    os.remove(temp_pdf_path)
                except PermissionError as pe:
                    print(f"Could not remove temp file {temp_pdf_path} immediately: {pe}")

        if os.path.exists(compressed_pdf_path):
            try:
                return send_file(compressed_pdf_path, as_attachment=True, 
                                 download_name=f"compressed_{original_filename}", 
                                 mimetype='application/pdf')
            finally:
                if os.path.exists(compressed_pdf_path):
                    try:
                        os.remove(compressed_pdf_path)
                    except PermissionError as pe_comp:
                        print(f"Could not remove compressed file {compressed_pdf_path} after sending: {pe_comp}")
        else:
            return "Error during compression, compressed file not found.", 500

    return render_template('pdfcompress.html')

@app.route('/create_pdf_from_images', methods=['GET', 'POST'])
def create_pdf_from_images():
    if request.method == 'POST':
        uploaded_files = request.files.getlist('images')
        orientation = request.form.get('orientation', 'P') # P for Portrait, L for Landscape
        page_size = request.form.get('page_size', 'A4') # e.g., A4, Letter
        margin = float(request.form.get('margin', 10)) # in mm
        image_order_json = request.form.get('image_order', '[]')
        image_order = json.loads(image_order_json)

        if not uploaded_files or uploaded_files[0].filename == '':
            return "No images selected!", 400

        # Validate file types
        for uploaded_file in uploaded_files:
            if not allowed_file(uploaded_file.filename):
                return f"Invalid file type for {uploaded_file.filename}! Only PNG, JPG, JPEG files are allowed.", 400

        pdf = FPDF(orientation=orientation, unit='mm', format=page_size)
        pdf.set_auto_page_break(auto=True, margin=margin)
        pdf.set_margin(margin)

        # Create a dictionary of uploaded files for easy lookup
        files_dict = {f.filename: f for f in uploaded_files}
        
        # Process images in the order specified by image_order
        for filename_in_order in image_order:
            img_file = files_dict.get(filename_in_order)
            if img_file:
                # Save the file temporarily to process it
                temp_filename = os.path.join(app.config['UPLOAD_FOLDER'], img_file.filename)
                img_file.save(temp_filename)

                try:
                    with Image.open(temp_filename) as pil_img:
                        width, height = pil_img.size
                    
                    available_width = pdf.w - 2 * margin
                    available_height = pdf.h - 2 * margin
                    aspect_ratio = width / height

                    if width > height: # Landscape image
                        img_width_on_pdf = available_width
                        img_height_on_pdf = img_width_on_pdf / aspect_ratio
                        if img_height_on_pdf > available_height:
                            img_height_on_pdf = available_height
                            img_width_on_pdf = img_height_on_pdf * aspect_ratio
                    else: # Portrait or square image
                        img_height_on_pdf = available_height
                        img_width_on_pdf = img_height_on_pdf * aspect_ratio
                        if img_width_on_pdf > available_width:
                            img_width_on_pdf = available_width
                            img_height_on_pdf = img_width_on_pdf / aspect_ratio
                    
                    x_pos = (pdf.w - img_width_on_pdf) / 2
                    y_pos = (pdf.h - img_height_on_pdf) / 2

                    pdf.add_page()
                    pdf.image(temp_filename, x=x_pos, y=y_pos, w=img_width_on_pdf, h=img_height_on_pdf)
                except Exception as e:
                    print(f"Error processing image {temp_filename}: {e}")
                finally:
                    if os.path.exists(temp_filename): # Clean up uploaded image
                        os.remove(temp_filename)
            else:
                print(f"Warning: Image {filename_in_order} not found in uploaded files.")

        pdf_output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.pdf')
        pdf.output(pdf_output_path, 'F')
        
        # Send the file and then attempt to clean it up
        try:
            return send_file(pdf_output_path, as_attachment=True, download_name='created_pdf.pdf')
        finally:
            if os.path.exists(pdf_output_path):
                try:
                    os.remove(pdf_output_path)
                except PermissionError as pe_output:
                    print(f"Could not remove output PDF {pdf_output_path} after sending: {pe_output}")

    return render_template('create_pdf_from_images.html')

if __name__ == '__main__':
    # Only run in debug mode locally, not in production
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)
