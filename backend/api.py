from flask import Flask, make_response, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from video_processor import VideoProcessor
from dotenv import load_dotenv
import os
import utils
import cv2
import numpy as np
import base64
import random
import uuid
import json

# ============================= INITIALIZATION ==============================
# Load environment variables
load_dotenv()

# Import database functions
try:
    from database.database import (
        init_db, save_annotation_session, save_frame_annotation,
        update_session_progress, load_annotation_session,
        list_annotation_sessions, delete_annotation_session,
        create_user_token, validate_user_token
    )
    DB_AVAILABLE = True
except Exception as e:
    print(f"Database not available: {e}")
    DB_AVAILABLE = False

app = Flask("pose-annotator-backend")
CORS(app, origins = ['https://pose-annotator.onrender.com'])

# Initatlize database on startup
if DB_AVAILABLE:
    init_db()

# ============================== CONFIGURATION ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
VIDEOS_DIR = os.path.join(DATA_DIR, 'videos')
FRAMESETS_DIR = os.path.join(DATA_DIR, 'frame_sets')
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
os.makedirs(VIDEOS_DIR, exist_ok = True)
os.makedirs(FRAMESETS_DIR, exist_ok = True)

# Store video processors and frame sets in memory (cache)
video_processors = {}  # video_id -> VideoProcessor
FRAME_SETS = {}        # frame_set_id -> { 'video_id': str, 'frame_numbers': list[int] }


# ================================= HELPERS ==================================
def _is_valid_video_file(filename: str) -> bool:
    return ('.' in filename and filename.rsplit('.', 1)[1].lower() in
            ALLOWED_EXTENSIONS)

def _frame_to_base64(frame: np.ndarray) -> bytes:
    """Convert a frame to base64 encoded JPEG."""
    _, buffer = cv2.imencode('.jpg', frame)
    return base64.b64encode(buffer).decode('utf-8')

def _load_meta(frame_set_id: str) -> dict:
    path = os.path.join(FRAMESETS_DIR, frame_set_id, 'meta.json')
    if not os.path.exists(path):
        raise FileNotFoundError('Frame set not found')
    with open(path, 'r', encoding = 'utf-8') as f:
        return json.load(f)


# ================================= ROUTES ===================================
@app.route('/frame-set', methods = ['POST'])
def upload_and_create_frame_set():
    """Upload a video file and create a randomly selected set of frames given a
    user-specified number of frames."""
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not _is_valid_video_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    # Read options from multipart form
    num_frames = request.form.get('num_frames', type = int)
    if num_frames <= 0:
        return jsonify({'error': 'num_frames must be greater than 0'}), 400

    get_first_frame = request.form.get(
        'get_first_frame', 'true').lower() in ('1', 'true', 'yes')

    # Save video
    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[1].lower()
    base = os.path.splitext(filename)[0]
    video_id = base
    video_path = os.path.join(VIDEOS_DIR, f'{video_id}{ext}')
    file.save(video_path)

    # Create processor
    processor = VideoProcessor(video_path)
    video_processors[video_id] = processor

    # Get frame count
    total_frames = int(processor.cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        return jsonify(
            {'error': 'Could not read frames from uploaded video'}), 400

    num_frames = min(num_frames, total_frames)

    # Generate random frame numbers
    frame_numbers = sorted(random.sample(range(total_frames), num_frames))

    # Create frame_set_id
    frame_set_id = uuid.uuid4().hex

    # Persist frame set on disk
    frame_set_dir = os.path.join(FRAMESETS_DIR, frame_set_id)

    meta = {
        'frame_set_id': frame_set_id,
        'video_id': video_id,
        'video_path': video_path,
        'fps': processor.fps,
        'width': processor.width,
        'height': processor.height,
        'total_frames': total_frames,
        'num_frames': num_frames,
        'frame_numbers': frame_numbers
    }

    with open(os.path.join(frame_set_dir, 'meta.json'), 'w',
              encoding = 'utf-8') as f:
        json.dump(meta, f, indent = 2)

    # Cache in memory
    FRAME_SETS[frame_set_id] = {
        'video_id': video_id,
        'frame_numbers': frame_numbers
    }

    resp = {
        'video_id': video_id,
        'frame_set_id': frame_set_id,
        'fps': processor.fps,
        'orig_width': processor.width,
        'orig_height': processor.height,
        'total_frames': total_frames,
        'count': len(frame_numbers),
        'frame_numbers': frame_numbers
    }

    if get_first_frame and len(frame_numbers) > 0:
        first_index = 0
        first_frame_num = frame_numbers[first_index]

        frame = processor.get_frame(number = first_frame_num)

        # Resize to max height = 720 px
        frame = processor.resize(frame, height = 720)

        # Add render dimensions to response
        resp['render_width'] = frame.shape[1]
        resp['render_height'] = frame.shape[0]

        resp['first_frame'] = {
            'frame_idx': first_index,
            'frame_num': first_frame_num,
            'frame_img': _frame_to_base64(frame),
            'render_width': frame.shape[1],
            'render_height': frame.shape[0]
        }

    return jsonify(resp)

@app.route('/frame-set/<frame_set_id>/info', methods = ['GET'])
def get_frame_set_info(frame_set_id: str):
    """Load persisted frame set metadata."""
    try:
        metadata = _load_meta(frame_set_id)
        frame_numbers = metadata.get('frame_numbers', [])
        return jsonify({
            'frame_set_id': metadata.get('frame_set_id'),
            'video_id': metadata.get('video_id'),
            'fps': metadata.get('fps'),
            'orig_width': metadata.get('width'),
            'orig_height': metadata.get('height'),
            'total_frames': metadata.get('total_frames'),
            'count': len(frame_numbers),
            'frame_numbers': frame_numbers
        })
    except FileNotFoundError:
        return jsonify({'error': 'Frame set not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/frame-set/<frame_set_id>/frame', methods = ['GET'])
def get_frame_from_set(frame_set_id: str):
    """
    Step through a frame set by index.

    Examples
    --------
    GET /frame-set/<id>/frame?index=0
    """
    frame_set = FRAME_SETS.get(frame_set_id)

    if not frame_set:
        try:
            meta = _load_meta(frame_set_id)
        except FileNotFoundError:
            return jsonify({'error': 'Frame set not found'}), 404

        frame_numbers = meta.get('frame_numbers', [])
        if not frame_numbers:
            return jsonify({'error': 'No frames available in this frame set'}), 400

        frame_set = {
            'video_id': meta['video_id'],
            'frame_numbers': frame_numbers
        }
        FRAME_SETS[frame_set_id] = frame_set

        # Ensure processor exists
        if meta['video_id'] not in video_processors:
            if not os.path.exists(meta['video_path']):
                return jsonify({'error': 'Video file not found on server'}), 404
            video_processors[meta['video_id']] = VideoProcessor(meta['video_path'])

    video_id = frame_set['video_id']
    processor = video_processors.get(video_id)
    if not processor:
        return jsonify({'error': 'Video not found'}), 404

    frame_idx = request.args.get('index', type = int)
    if frame_idx is None:
        return jsonify({'error': 'Missing index parameter'}), 400

    frame_numbers = frame_set['frame_numbers']
    if frame_idx < 0 or frame_idx >= len(frame_numbers):
        return jsonify({'error': 'index out of range'}), 400

    frame_num = frame_numbers[frame_idx]
    frame = processor.get_frame(number = frame_num)

    # Resize to max height = 720 px
    frame = processor.resize(frame, height = 720)

    return jsonify({
        'frame_set_id': frame_set_id,
        'frame_count': len(frame_numbers),
        'frame_idx': frame_idx,
        'frame_num': frame_num,
        'frame_img': _frame_to_base64(frame),
        'render_width': frame.shape[1],
        'render_height': frame.shape[0]
    })


@app.route('/annotations/export-csv', methods = ['POST'])
def export_annotations_csv():
    """
    Export annotations as a CSV file.

    Examples
    --------
    POST /annotations/export-csv
    """
    try:
        # Get JSON data from request body
        all_annotations = request.json

        if not all_annotations:
            return jsonify({'error': 'No annotations data provided'}), 400

        # Format data for CSV
        annotations_df = utils.process_annotations(all_annotations)
        csv_content = annotations_df.to_csv(index = False)

        # Send as downloadable file
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = 'attachment; filename=annotations.csv'
        return response

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# ================================ANNOTATION ENDPOINTS===============================

@app.route('/annotations/save', methods = ['POST'])
def save_annotations():
    """
    Saves all annotations for a frame set.

    Expected JSON body:
    {
        "frame_set_id": str,
        "video_id": str,
        "orig_width": int,
        "orig_height": int,
        "rendered_width": int,
        "rendered_height": int,
        "total_frames": int,
            "annotations": {
                "123": { "nose": { "x": 100, "y": 200, "not_visible": false }, ... },
                "456": { ... }
        }
    }
    """
    if not DB_AVAILABLE:
        return jsonify({'error': 'Database not available'}), 503
    
    try:
        data = request.json
        frame_set_id = data.get('frame_set_id')
        video_id = data.get('video_id')
        annotations = data.get('annotations', {})

        if not frame_set_id or not video_id:
            return jsonify({'error': 'frame_set_id and video_id are required'}), 400
        
        # Extract dimension metadata
        orig_width = data.get('orig_width') or annotations.get('orig_width')
        orig_height = data.get('orig_height') or annotations.get('orig_height')
        rendered_width = data.get('rendered_width') or annotations.get('rendered_width')
        rendered_height = data.get('rendered_height') or annotations.get('rendered_height')

        # Count total frames (exluding the metadata fields)
        metadata_keys = {'orig_width', 'orig_height', 'rendered_width', 'rendered_height'}
        frame_annotations = {k: v for k, v in annotations.items() if k not in metadata_keys and isinstance(v, dict)}
        last_frame_annotated = data.get('last_frame_annotated', 0)
        total_frames = _load_meta(frame_set_id).get('num_frames', len(frame_annotations))

        if total_frames == 0:
            return jsonify({'error': 'No frame annotations provided'}), 400
        
        # Add token param
        token = data.get('token') or request.args.get('token')

        # Validate token
        if token and not validate_user_token(token):
            return jsonify({'error': 'Invalid user token'}), 401
        
        # Save or update annotation session
        save_annotation_session(
            frame_set_id, video_id, orig_width, orig_height,
            rendered_width, rendered_height, total_frames, last_frame_annotated, user_token=token
        )

        # Save each frame's annotations
        saved_count = 0
        for frame_num_str, frame_data in frame_annotations.items():
            try:
                frame_num = int(frame_num_str)
            except ValueError:
                continue # Skip invalid frame numbers

            # Check if frame is complete
            is_complete = all(
                (ann.get('x') is not None and ann.get('y') is not None and
                 not ann.get('not_visible')) or ann.get('not_visible')
                 for ann in frame_data.values()
            )

            save_frame_annotation(frame_set_id, frame_num, frame_data, is_complete)
            saved_count += 1
        
        # Update session progress
        update_session_progress(frame_set_id)

        return jsonify({
            'success': True,
            'message': f'Saved {saved_count} frames',
            'frame_set_id': frame_set_id
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/annotations/load/<frame_set_id>', methods = ['GET'])
def load_annotations(frame_set_id: str):
    """
    Load annotations for a given frame set.
    """
    if not DB_AVAILABLE:
        return jsonify({'error': 'Database not available'}), 503
    
    try:
        token = request.args.get('token')

        # Validate token
        if token and not validate_user_token(token):
            return jsonify({'error': 'Invalid user token'}), 401

        data = load_annotation_session(frame_set_id)

        if not data:
            return jsonify({'error': 'Session not found'}), 404
        
        session = data['session']

        # Check if session belongs to this user
        if token and session.get('user_token') != token:
            return jsonify({'error': 'Unauthorized to access this session'}), 403

        frames = data['frames']

        # Reconstruct annotations object
        annotations = {
            'orig_width': session.get('orig_width'),
            'orig_height': session.get('orig_height'),
            'rendered_width': session.get('rendered_width'),
            'rendered_height': session.get('rendered_height')
        }

        for frame in frames:
            annotations[str(frame['frame_num'])] = frame['annotations']
        
        return jsonify({
            'success': True,
            'frame_set_id': frame_set_id,
            'video_id': session['video_id'],
            'annotations': annotations,
            'session_info': {
                'created_at': session['created_at'].isoformat() if session.get('created_at') else None,
                'updated_at': session['updated_at'].isoformat() if session.get('updated_at') else None,
                'total_frames': session['total_frames'],
                'annotated_frames': session['annotated_frames'],
                'last_frame_annotated': session['last_frame_annotated'],
                'status': session['status']
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/annotations/sessions', methods=['GET'])
def get_annotation_sessions():
    """ List all annotation sessions. """
    if not DB_AVAILABLE:
        return jsonify({'error': 'Database not available'}), 503
    
    try:
        token = request.args.get('token')

        # Validate token
        if token and not validate_user_token(token):
            return jsonify({'error': 'Invalid user token'}), 401

        limit = request.args.get('limit', default=50, type=int)
        sessions = list_annotation_sessions(limit, user_token=token)

        # Convert datetime objects to ISO format strings
        for session in sessions:
            if session.get('created_at'):
                session['created_at'] = session['created_at'].isoformat()
            if session.get('updated_at'):
                session['updated_at'] = session['updated_at'].isoformat()
        
        return jsonify({
            'success': True,
            'sessions': sessions
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/annotations/session/<frame_set_id>', methods=['DELETE'])
def delete_session(frame_set_id: str):
    """ Delete an annotation session. """
    if not DB_AVAILABLE:
        return jsonify({'error': 'Database not available'}), 503
    
    try:
        token = request.args.get('token') or request.json.get('token') if request.json else None

        # Validate token
        if token and not validate_user_token(token):
            return jsonify({'error': 'Invalid user token'}), 401

        # Optional: Verify the session belongs to this user before deleting
        if token:
            session_data = load_annotation_session(frame_set_id)
            if session_data and session_data['session'].get('user_token') != token:
                return jsonify({'error': 'Unauthorized to delete this session'}), 403

        deleted = delete_annotation_session(frame_set_id)

        if not deleted:
            return jsonify({'error': 'Session not found'}), 404
        
        return jsonify({
            'success': True,
            'message': f"Annotation session {frame_set_id} deleted"
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/annotations/auto-save', methods=['POST'])
def auto_save_frame():
    """
    Auto-save a single frame's annotations.
    
    Expected JSON body:
    {
        "frame_set_id": "...",
        "video_id": "...",
        "frame_num": 123,
        "annotations": { "nose": {...}, "left_eye": {...}, ... },
        "orig_width": 1920,
        "orig_height": 1080,
        "render_width": 1280,
        "render_height": 720,
        "total_frames": 10
    }
    """
    if not DB_AVAILABLE:
        return jsonify({'error': 'Database not available'}), 503
    
    try:
        data = request.json
        frame_set_id = data.get('frame_set_id')
        video_id = data.get('video_id')
        frame_num = data.get('frame_num')
        annotations = data.get('annotations', {})

        if not all([frame_set_id, video_id, frame_num is not None]):
            return jsonify({'error': f"Missing required fields"}), 400
        
        # Get and validate token
        token = data.get('token') or request.args.get('token')
        if token and not validate_user_token(token):
            return jsonify({'error': 'Invalid user token'}), 401
        
        # Check if session exists
        save_annotation_session(
            frame_set_id, video_id,
            data.get('orig_width'), data.get('orig_height'),
            data.get('render_width'), data.get('render_height'),
            data.get('total_frames', 0),
            data.get('last_frame_annotated', 0),
            user_token=token  # Add this
        )

        # Check if frame is complete
        is_complete = all(
            (ann.get('x') is not None and ann.get('y') is not None and
             not ann.get('not_visible')) or ann.get('not_visible')
             for ann in annotations.values()
        )

        save_frame_annotation(frame_set_id, frame_num, annotations, is_complete)

        return jsonify({
            'success': True,
            'message': f'Auto-saved frame {frame_num} for frame set {frame_set_id}'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# ============================= USER MANAGEMENT =============================

@app.route('/admin/generate-token', methods = ['POST'])
def generate_user_token():
    """ Generate a unique token for a user. """
    
    try:
        token = create_user_token()
        # Use frontend URL instead of backend URL
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
        return jsonify({
            'success': True,
            'token': token,
            'link': f"{frontend_url}/annotate/{token}"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/validate-token/<token>', methods = ['GET'])
def check_token(token: str):
    """ Validate a user token. """
    try:
        is_valid = validate_user_token(token)
        if is_valid:
            return jsonify({
                'success': True,
            })
        
        return jsonify({'valid': False}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# ========================== HEALTH CHECK & DEBUGGING ========================

@app.route('/health', methods = ['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})

@app.route('/debug/meta/<frame_set_id>')
def debug_meta(frame_set_id):
    path = os.path.join(FRAMESETS_DIR, frame_set_id, 'meta.json')
    exists = os.path.exists(path)
    return jsonify({'exists': exists, 'path': path})


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
