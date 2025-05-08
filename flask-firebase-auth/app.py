import io
import pandas as pd
from database_config import SessionLocal, ExcelData, init_db, ChartData
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from firebase_config import users_ref, db

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize database tables
init_db()

@app.route("/")
def home():
    return "Flask + Firebase is working!"

@app.route("/signup", methods=["POST", "OPTIONS"])
@cross_origin()
def signup():
    if request.method == "OPTIONS":
        return '', 204  # Handle CORS preflight

    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    clearance = data.get("clearance")

    try:
        # Check if user already exists
        existing_user = users_ref.where("email", "==", email).get()
        if existing_user:
            return jsonify({"error": "Email already registered"}), 400

        # Try adding user to Firestore
        doc_ref = users_ref.add({
            "name": name,
            "email": email,
            "password": password,  # In production, store hashed passwords!
            "clearance": int(clearance)
        })
        print("User added with doc ID:", doc_ref)

        return jsonify({
            "message": "Signup successful!",
            "name": name,
            "email": email,
            "clearance": int(clearance)
        }), 200

    except Exception as e:
        print("Error during signup:", e)
        return jsonify({"error": "Failed to sign up", "details": str(e)}), 500


@app.route("/login", methods=["POST", "OPTIONS"])
@cross_origin()
def login():
    if request.method == "OPTIONS":
        return '', 204  # Handle CORS preflight

    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    try:
        user_query = users_ref.where("email", "==", email).get()
        if not user_query:
            return jsonify({"error": "User not found"}), 404

        user_data = user_query[0].to_dict()
        print("Login user data fetched from Firestore:", user_data)

        if user_data["password"] != password:
            return jsonify({"error": "Incorrect password"}), 401

        clearance = user_data.get("clearance", 1)

        return jsonify({
            "message": "Login successful!",
            "user": {
                "name": user_data["name"],
                "email": user_data["email"],
                "clearance": clearance
            }
        }), 200

    except Exception as e:
        print("Error during login:", e)
        return jsonify({"error": "Login failed", "details": str(e)}), 500


@app.route("/upload-excel", methods=["POST"])
@cross_origin()
def upload_excel():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        # Read Excel file into pandas DataFrame
        in_memory_file = io.BytesIO()
        file.save(in_memory_file)
        in_memory_file.seek(0)
        df = pd.read_excel(in_memory_file)

        # Store data into database
        session = SessionLocal()
        for _, row in df.iterrows():
            excel_data = ExcelData(
                state_name=str(row[0]) if len(row) > 0 else None,
                district_name=str(row[1]) if len(row) > 1 else None,
                factory_name=str(row[2]) if len(row) > 2 else None,
                bod=str(row[3]) if len(row) > 3 else None,
                cod=str(row[4]) if len(row) > 4 else None,
                ph=str(row[5]) if len(row) > 5 else None,
                nitrate=str(row[6]) if len(row) > 6 else None,
                do=str(row[7]) if len(row) > 7 else None,
                tds=str(row[8]) if len(row) > 8 else None,
                zone=str(row[9]) if len(row) > 9 else None,
            )
            session.add(excel_data)
        session.commit()
        session.close()

        return jsonify({"message": "Excel file uploaded and data stored successfully."}), 200
    except Exception as e:
        print("Error processing Excel file:", e)
        return jsonify({"error": "Failed to process Excel file", "details": str(e)}), 500

@app.route("/fetch-excel-data", methods=["GET"])
@cross_origin()
def fetch_excel_data():
    try:
        session = SessionLocal()
        data = session.query(ExcelData).all()
        result = []
        for item in data:
            result.append({
                "id": item.id,
                "state_name": item.state_name,
                "district_name": item.district_name,
                "factory_name": item.factory_name,
                "bod": item.bod,
                "cod": item.cod,
                "ph": item.ph,
                "nitrate": item.nitrate,
                "do": item.do,
                "tds": item.tds,
                "zone": item.zone,
            })
        session.close()
        return jsonify({"data": result}), 200
    except Exception as e:
        print("Error fetching Excel data:", e)
        return jsonify({"error": "Failed to fetch Excel data", "details": str(e)}), 500

@app.route("/update-excel-data/<int:data_id>", methods=["PUT"])
@cross_origin()
def update_excel_data(data_id):
    try:
        data = request.get_json()
        session = SessionLocal()
        record = session.query(ExcelData).filter(ExcelData.id == data_id).first()
        if not record:
            session.close()
            return jsonify({"error": "Record not found"}), 404

        # Update fields if present in request
        for field in ["state_name", "district_name", "factory_name", "bod", "cod", "ph", "nitrate", "do", "tds", "zone"]:
            if field in data:
                setattr(record, field, data[field])

        session.commit()
        session.close()
        return jsonify({"message": "Record updated successfully"}), 200
    except Exception as e:
        print("Error updating Excel data:", e)
        return jsonify({"error": "Failed to update Excel data", "details": str(e)}), 500

@app.route("/chart-data", methods=["GET", "POST"])
@cross_origin()
def chart_data():
    if request.method == "GET":
        try:
            session = SessionLocal()
            data = session.query(ChartData).all()
            result = []
            for item in data:
                result.append({
                    "id": item.id,
                    "label": item.label,
                    "bad": item.bad,
                    "moderate": item.moderate,
                    "good": item.good,
                })
            session.close()
            return jsonify({"data": result}), 200
        except Exception as e:
            print("Error fetching chart data:", e)
            return jsonify({"error": "Failed to fetch chart data", "details": str(e)}), 500
    elif request.method == "POST":
        try:
            data = request.get_json()
            session = SessionLocal()
            new_record = ChartData(
                label=data.get("label", ""),
                bad=float(data.get("bad", 0)),
                moderate=float(data.get("moderate", 0)),
                good=float(data.get("good", 0))
            )
            session.add(new_record)
            session.commit()
            session.close()
            return jsonify({"message": "Chart data added successfully"}), 201
        except Exception as e:
            print("Error adding chart data:", e)
            return jsonify({"error": "Failed to add chart data", "details": str(e)}), 500

@app.route("/chart-data/<int:data_id>", methods=["PUT", "DELETE"])
@cross_origin()
def chart_data_detail(data_id):
    if request.method == "PUT":
        try:
            data = request.get_json()
            session = SessionLocal()
            record = session.query(ChartData).filter(ChartData.id == data_id).first()
            if not record:
                session.close()
                return jsonify({"error": "Record not found"}), 404

            for field in ["label", "bad", "moderate", "good"]:
                if field in data:
                    setattr(record, field, data[field])

            session.commit()
            session.close()
            return jsonify({"message": "Chart data updated successfully"}), 200
        except Exception as e:
            print("Error updating chart data:", e)
            return jsonify({"error": "Failed to update chart data", "details": str(e)}), 500
    elif request.method == "DELETE":
        try:
            session = SessionLocal()
            record = session.query(ChartData).filter(ChartData.id == data_id).first()
            if not record:
                session.close()
                return jsonify({"error": "Record not found"}), 404
            session.delete(record)
            session.commit()
            session.close()
            return jsonify({"message": "Chart data deleted successfully"}), 200
        except Exception as e:
            print("Error deleting chart data:", e)
            return jsonify({"error": "Failed to delete chart data", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
