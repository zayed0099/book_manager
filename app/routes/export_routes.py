from flask import Blueprint
from flask_restful import Api

export_bp = Blueprint('export', __name__, url_prefix='/api/v1/export')
export_api = Api(export_bp)

from app.resources.export_data import (PDFExport, 
	JSONExport)

# Generating PDF
# export_api.add_resource(PDFExport, '/pdf', endpoint='export_pdf')

# generating JSON data
export_api.add_resource(JSONExport, '/json', endpoint='export_json')