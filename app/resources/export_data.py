# book manage.py
import os
from flask_restful import Resource, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
from datetime import datetime

# Local Import
from app.errors.handlers import CustomBadRequest
from app.extensions import db
from app.jwt_extensions import limiter

class PDFExport(Resource):
	@jwt_required()
	def post(self):
		from app.models import User, book_manager
		from fpdf import FPDF

		user_id = get_jwt_identity()
		user = User.query.get(user_id)

		# Pdf setup

		pdf = FPDF()
		pdf.add_page()

		# Pdf file part
		pdf.set_font("Times", "B", size=16)
		pdf.cell(200, 10, txt="Book Manager", ln=True, align='C')

		pdf.set_font("Times", "B", size=12)
		pdf.cell(200, 10, txt=f"Booklist generated for user {user.username}.", ln=True, align='C')

		pdf.set_font("Times", "B", size=12)
		pdf.cell(200, 10, txt=f"List was generated automatically at {datetime.utcnow()}, on users request.", ln=True, align='C')

		header = ["Title", "Author", "Genre", "Status"]

		table_data = book_manager.query.filter_by(user_id=user_id).all()

		column_widths = [50, 60, 40, 30]

		# drawing table header
		for i, heading in enumerate(header):
			pdf.set_fill_color(200, 220, 255) # light-blue
			pdf.cell(column_widths[i], 10, heading, border=1, align="C", fill=True)
		pdf.ln() # to go to next line

		# adding data in table 
		for row in table_data:
			row_items = [row.title, row.author, row.genre, row.status]
			for i, item in enumerate(row_items):
				pdf.cell(column_widths[i], 10, str(item), border=1)
			pdf.ln()

		os.makedirs('exports', exist_ok=True)
		file_path = f"exports/{user_id}_user_report.pdf"
		pdf.output(file_path)
		return {"message": "PDF exported successfully"}, 200
		

