import os
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from pymatgen.ext.matproj import MPRester
from pymatgen.analysis.phase_diagram import PhaseDiagram, PDPlotter

app = Flask(__name__)
CORS(app)

@app.route('/generate_phase_diagram', methods=['POST'])
def generate_phase_diagram():
    data = request.json
    api_key = os.environ['API_KEY']
    elements = data.get('elements')

    if not elements:
        return jsonify({'error': 'API key and elements are required.'}), 400

    try:
        mpr = MPRester(api_key)
        entries = mpr.get_entries_in_chemsys(elements=elements)
        if not entries:
            return jsonify({'error': 'No entries found for the given selections.'}), 404
        pd = PhaseDiagram(entries)
        plotter = PDPlotter(pd)
        fig = plotter.get_plot()
        fig.write_image("figure.png", engine="kaleido")
        return send_file("figure.png", mimetype='image/png')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()
