import os
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from pymatgen.ext.matproj import MPRester
from pymatgen.analysis.phase_diagram import PhaseDiagram, PDPlotter
import logging

app = Flask(__name__)
CORS(app)
mpr = MPRester(os.environ['API_KEY'])
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)
app.logger.info(f"Running!")

@app.route('/generate_phase_diagram', methods=['POST'])
def generate_phase_diagram():
    data = request.json
    elements = data.get('elements')
    app.logger.info(f"Received /generate_phase_diagram request with elements: {elements}")

    if not elements:
        app.logger.info("Returning an error as elements in /generate_phase_diagram were empty")
        return jsonify({'error': 'API key and elements are required.'}), 400

    try:
        app.logger.info(f"Getting entries in chemsys for {elements} in /generate_phase_diagram")
        entries = mpr.get_entries_in_chemsys(elements=elements)
        if not entries:
            app.logger.info(f"Returning an error as no enteries for {elements} were found in /generate_phase_diagram")
            return jsonify({'error': 'No entries found for the given selections.'}), 404
        app.logger.info(f"Getting plot for {elements} in /generate_phase_diagram")
        pd = PhaseDiagram(entries)
        plotter = PDPlotter(pd)
        fig = plotter.get_plot()
        app.logger.info(f"Sending plot for {elements} in /generate_phase_diagram")
        fig.write_image("figure.png", engine="kaleido")
        return send_file("figure.png", mimetype='image/png')

    except Exception as e:
        app.logger.info(f"Reached error {e} in /generate_phase_diagram")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()
