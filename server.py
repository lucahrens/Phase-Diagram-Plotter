from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from pymatgen.ext.matproj import MPRester
from pymatgen.analysis.phase_diagram import PhaseDiagram, PDPlotter
import logging
from io import BytesIO
import os

app = Flask(__name__)
CORS(app)

# Configure logging to integrate with Gunicorn
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)
app.logger.info("Running!")

@app.route('/generate_phase_diagram', methods=['POST'])
def generate_phase_diagram():
    data = request.json
    elements = data.get('elements')
    app.logger.info(f"Received /generate_phase_diagram request with elements: {elements}")

    if not elements or len(elements)!=3:
        app.logger.warning("Elements not provided in the request.")
        return jsonify({'error': 'Please select exactly 3 elements, comma separated.'}), 400

    try:
        app.logger.info(f"Fetching entries for elements: {elements}")
        with MPRester(os.environ['API_KEY']) as mpr:
            entries = mpr.get_entries_in_chemsys(elements=elements)

        if not entries or len(elements)!=3:
            app.logger.warning(f"No entries found for elements: {elements}")
            return jsonify({'error': 'No entries found for the given elements.'}), 404

        app.logger.info(f"Generating phase diagram for elements: {elements}")
        pd = PhaseDiagram(entries)
        plotter = PDPlotter(pd)
        fig = plotter.get_plot()

        # Use BytesIO to handle image in memory
        img_io = BytesIO()
        fig.write_image(img_io, format='png', engine='kaleido')
        img_io.seek(0)

        app.logger.info(f"Sending phase diagram for elements: {elements}")
        return send_file(img_io, mimetype='image/png')

    except Exception as e:
        app.logger.error(f"Error generating phase diagram: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()
