import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend for server environments
import matplotlib.pyplot as plt
import librosa
from werkzeug.utils import secure_filename
from tcai_sandesh.utils.analyze_audio import analyze_audio_file

# Get absolute path to the package directory
BASE_DIR = Path(__file__).resolve().parent

# Configure Flask app
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static")
)

# Set up dynamic uploads folder (NOT shipped in pip package)
UPLOAD_FOLDER = BASE_DIR / "uploads"
STATIC_FOLDER = BASE_DIR / "static"

app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB limit

# Create folders at runtime if missing
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
STATIC_FOLDER.mkdir(parents=True, exist_ok=True)


@app.route("/")
def index():
    """Render the home page"""
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    """Handle audio file upload and analysis"""
    if "audiofile" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["audiofile"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Save uploaded file securely
    filename = secure_filename(file.filename)
    file_path = UPLOAD_FOLDER / filename

    try:
        file.save(file_path)
        analysis_result = analyze_audio_file(str(file_path))

        if not analysis_result.get("success", False):
            return jsonify({"error": analysis_result.get("error", "Analysis failed")}), 500

        # Generate pitch plot
        plot_path = generate_pitch_plot(file_path)
        analysis_result["plot_path"] = str(plot_path.relative_to(BASE_DIR))

        return jsonify(analysis_result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Remove uploaded file after processing to save space
        if file_path.exists():
            file_path.unlink()


def generate_pitch_plot(audio_path: Path):
    """Generate a pitch contour plot for the given audio file"""
    try:
        y, sr = librosa.load(audio_path)
        pitches = librosa.yin(y, fmin=80, fmax=400)
        times = librosa.times_like(pitches, sr=sr)

        plt.figure(figsize=(10, 4))
        plt.plot(times, pitches, color="blue")
        plt.title("Pitch Contour")
        plt.xlabel("Time (s)")
        plt.ylabel("Frequency (Hz)")
        plt.grid(True)

        plot_filename = STATIC_FOLDER / "pitch_plot.png"
        plt.savefig(plot_filename)
        plt.close()

        return plot_filename
    except Exception as e:
        print(f"[ERROR] Failed to generate pitch plot: {e}")
        return None


def main():
    """Entry point for console_scripts"""
    app.run(host="0.0.0.0", port=5000, debug=False)


if __name__ == "__main__":
    main()
