from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from video_analyzer import VideoAnalyzer

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize video analyzer
analyzer = VideoAnalyzer()

def analyze_video(filename):
    """Analyze video for distracted driving behaviors using computer vision"""
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        # Perform real video analysis
        analysis_result = analyzer.analyze_video(video_path)
        analysis_result['analyzed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return analysis_result
    except Exception as e:
        # Fallback in case of analysis error
        return {
            'behaviors': ['Analysis Error'],
            'warnings': [{
                'type': 'error',
                'message': f' Error analyzing video: {str(e)}. Please try again.',
                'severity': 'Medium'
            }],
            'risk_level': 'Medium',
            'confidence': 0.0,
            'analyzed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

@app.route('/')
def dashboard():
    # Don't list or analyze previous videos to avoid shuffling
    return render_template('dashboard.html', videos=[])

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return redirect(url_for('dashboard'))

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return redirect(url_for('dashboard'))

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Analyze immediately and show result
    try:
        analysis_result = analyzer.analyze_video(filepath)
        analysis_result['analyzed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        analysis_result['filename'] = filename
        # Delete the video after analysis to avoid saving previous videos
        os.remove(filepath)
        return render_template('dashboard.html', result=analysis_result, videos=[])
    except Exception as e:
        # Also delete on error
        if os.path.exists(filepath):
            os.remove(filepath)
        return redirect(url_for('dashboard'))

@app.route('/video/<filename>')
def serve_video(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/temp/<filename>')
def serve_temp(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)