from flask import Flask, make_response, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from video_processor import VideoProcessor
import os
import utils
import cv2
import numpy as np
import base64
import random
import uuid
import json

# ============================== CONFIGURATION ===============================
DATA_DIR = 'data'
VIDEOS_DIR = os.path.join(DATA_DIR, 'videos')
FRAMESETS_DIR = os.path.join(DATA_DIR, 'frame_sets')
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}


# ================================== STARTUP =================================
# Cleanup data directory at startup
utils.cleanup_data()
os.makedirs(VIDEOS_DIR, exist_ok = True)
os.makedirs(FRAMESETS_DIR, exist_ok = True)

# Create Flask app
app = Flask('pose-annotator-backend')
CORS(app)

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
    video_id = f'{base}_{uuid.uuid4().hex[:8]}'
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
    annotations_dir = os.path.join(frame_set_dir, 'annotations')
    os.makedirs(annotations_dir, exist_ok = True)

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
            'orig_width': metadata.get('orig_width'),
            'orig_height': metadata.get('orig_height'),
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


@app.route('/health', methods = ['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(debug = True, port = 8000)