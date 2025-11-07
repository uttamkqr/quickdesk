# utils/file_handler.py

import os
import uuid
from werkzeug.utils import secure_filename
from models import Attachment, db

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'images': {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'},
    'documents': {'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt'},
    'spreadsheets': {'xls', 'xlsx', 'csv', 'ods'},
    'archives': {'zip', 'rar', '7z', 'tar', 'gz'},
    'other': {'xml', 'json', 'log'}
}

# Maximum file size (in bytes) - 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024

UPLOAD_FOLDER = 'uploads'


def get_all_allowed_extensions():
    """Get all allowed file extensions"""
    extensions = set()
    for category in ALLOWED_EXTENSIONS.values():
        extensions.update(category)
    return extensions


def allowed_file(filename):
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in get_all_allowed_extensions()


def get_file_category(filename):
    """Determine file category based on extension"""
    if '.' not in filename:
        return 'other'
    ext = filename.rsplit('.', 1)[1].lower()

    for category, extensions in ALLOWED_EXTENSIONS.items():
        if ext in extensions:
            return category
    return 'other'


def generate_unique_filename(original_filename):
    """Generate unique filename to prevent conflicts"""
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    unique_name = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
    return unique_name


def validate_file_size(file):
    """Validate file size"""
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    return file_size <= MAX_FILE_SIZE, file_size


def save_file(file, ticket_id, user_id):
    """
    Save uploaded file and create attachment record
    
    Args:
        file: FileStorage object from request.files
        ticket_id: ID of the ticket
        user_id: ID of the user uploading the file
        
    Returns:
        Attachment object or None if failed
    """
    if not file or file.filename == '':
        return None, "No file provided"

    if not allowed_file(file.filename):
        return None, f"File type not allowed. Allowed: {', '.join(get_all_allowed_extensions())}"

    # Validate file size
    is_valid_size, file_size = validate_file_size(file)
    if not is_valid_size:
        return None, f"File too large. Maximum size: {MAX_FILE_SIZE / (1024 * 1024):.1f}MB"

    try:
        # Ensure upload directory exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        # Generate unique filename
        original_filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(original_filename)
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

        # Save file
        file.save(file_path)

        # Create attachment record
        attachment = Attachment(
            filename=unique_filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=file_size,
            file_type=get_file_category(original_filename),
            ticket_id=ticket_id,
            uploaded_by=user_id
        )

        db.session.add(attachment)
        db.session.commit()

        return attachment, None

    except Exception as e:
        print(f"❌ Failed to save file: {e}")
        db.session.rollback()
        return None, f"Failed to save file: {str(e)}"


def delete_file(attachment_id):
    """
    Delete file and attachment record
    
    Args:
        attachment_id: ID of the attachment to delete
        
    Returns:
        True if successful, False otherwise
    """
    try:
        attachment = Attachment.query.get(attachment_id)
        if not attachment:
            return False, "Attachment not found"

        # Delete physical file
        if os.path.exists(attachment.file_path):
            os.remove(attachment.file_path)

        # Delete database record
        db.session.delete(attachment)
        db.session.commit()

        return True, "File deleted successfully"

    except Exception as e:
        print(f"❌ Failed to delete file: {e}")
        db.session.rollback()
        return False, f"Failed to delete file: {str(e)}"


def get_ticket_attachments(ticket_id):
    """Get all attachments for a ticket"""
    return Attachment.query.filter_by(ticket_id=ticket_id).all()


def get_attachment_path(attachment_id):
    """Get file path for an attachment"""
    attachment = Attachment.query.get(attachment_id)
    if attachment and os.path.exists(attachment.file_path):
        return attachment.file_path
    return None


def format_file_size(size_bytes):
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
