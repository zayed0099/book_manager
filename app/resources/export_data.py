# book manage.py
import os
import json
import csv
import io
from flask import jsonify, send_file, make_response
from flask_restful import Resource, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
from datetime import datetime
from pathlib import Path

# Local Import
from app.errors.handlers import CustomBadRequest
from app.extensions import db
from app.jwt_extensions import limiter

# this code is crashing on my pc. will look into it later. 

# class PDFExport(Resource):
# 	@jwt_required()
# 	def post(self):
# 		from app.models import User, book_manager
# 		from fpdf import FPDF

# 		user_id = get_jwt_identity()
# 		user = User.query.get(user_id)

# 		# Pdf setup

# 		pdf = FPDF()
# 		pdf.add_page()

# 		# Pdf file part
# 		pdf.set_font("Times", "B", size=16)
# 		pdf.cell(200, 10, txt="Book Manager", ln=True, align='C')

# 		pdf.set_font("Times", "B", size=12)
# 		pdf.cell(200, 10, txt=f"Booklist generated for user {user.username}.", ln=True, align='C')

# 		pdf.set_font("Times", "B", size=12)
# 		pdf.cell(200, 10, txt=f"List was generated automatically at {datetime.utcnow()}, on users request.", ln=True, align='C')

# 		header = ["Title", "Author", "Genre", "Status"]

# 		table_data = book_manager.query.filter_by(user_id=user_id).limit(10).all()

# 		column_widths = [50, 60, 40, 30]

# 		# drawing table header
# 		for i, heading in enumerate(header):
# 			pdf.set_fill_color(200, 220, 255) # light-blue
# 			pdf.cell(column_widths[i], 10, heading, border=1, align="C", fill=True)
# 			print('Header added')
# 		pdf.ln() # to go to next line

# 		# adding data in table 
# 		for row in table_data:
# 			print('table data adding')
# 			try:
# 				row_items = [row.title, row.author, row.genre, row.status]
# 				for i, item in enumerate(row_items):
# 					pdf.cell(column_widths[i], 10, str(item), border=1)
# 					print('table data adding 2')
# 				pdf.ln()
# 			except Exception as e:
# 				print("Error writing row to PDF:", e)


# 		os.makedirs('exports', exist_ok=True)
# 		file_path = f"exports/{user_id}_user_report.pdf"
# 		try:
# 			pdf.output(file_path)
# 		except Exception as e:
# 			print("PDF output error:", e)
# 			return {"message": "PDF generation failed"}, 500
			
# 		return {"message": "PDF exported successfully"}, 200

class JSONExport(Resource):
	@jwt_required()
	def post(self):
		user_id = get_jwt_identity()
		from app.models import book_manager
		from app.extensions import exportschema

		books = book_manager.query.filter_by(user_id=user_id).limit(50).all()
		output = exportschema.dump(books)

		dir_path = Path("app/exports/json")
		dir_path.mkdir(parents=True, exist_ok=True)

		check_file = dir_path/f"{user_id}_books.json"

		if check_file.exists():
			return {'message' : 'The user already has a json file generated.'}, 400

		with open(f"app/exports/json/{user_id}_books.json", "w") as file:
			json.dump(output, file, indent=4)

		return {'message' : 'JSON file has been successfully created.'}, 200

	@jwt_required()
	def get(self):
		user_id = get_jwt_identity()

		base_dir = Path(__file__).resolve().parents[2]
		dir_path = base_dir/"exports"/"json"

		filename = f"{user_id}_books.json"
		
		target_path = dir_path/filename
		
		if target_path.exists():
			return send_file(
				target_path,
				mimetype='application/json',
				as_attachment=True
				)
		else:
			return {"message": "File not found"}, 404

class CSVExport(Resource):
	@jwt_required()
	def get(self):
		user_id = get_jwt_identity()

		from app.models import book_manager

		books = book_manager.query.filter_by(
			user_id=user_id).limit(50).all()

		temp_file = io.StringIO()
		cw = csv.writer(temp_file)

		cw.writerow([
			'ID', 
			'Title', 
			'Author',
			'Genre', 
			'Status', 
			'Is_deleted',
			'Favourite'
			])

		for book in books:
			cw.writerow([
				book.id,
				book.title,
				book.author,
				book.genre,
				book.status,
				book.is_deleted,
				book.favourite
				])

		output = temp_file.getvalue()

		response = make_response(output)
		response.headers["Content-Disposition"] = (
			f"attachment; filename=books_user_{user_id}.csv")
		response.headers["Content-type"] = "text/csv"
		return response

