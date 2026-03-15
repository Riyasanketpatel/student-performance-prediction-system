from flask import Flask, render_template, request, redirect
from flask import send_file
from markupsafe import Markup
import pandas as pd
import plotly.express as px
import os
import joblib

# ---------------- LOAD ML MODEL ---------------- #
model = joblib.load("models/linear_regression.pkl")
scaler = joblib.load("models/scaler.pkl")
columns = joblib.load("models/columns.pkl")

app = Flask(__name__)

DATA_FILE = "data.csv"

# Dummy login users
USERS = {
    "riya": "123",
    "mentor": "project",
    "analyst": "data123"
}

# ---------------- LOGIN ---------------- #

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username in USERS and USERS[username] == password:
            return redirect("/dashboard")

        else:
            return render_template("login.html", error="Invalid Login")

    return render_template("login.html")


# ---------------- DASHBOARD ---------------- #

@app.route("/dashboard")
def dashboard():

    if not os.path.exists(DATA_FILE):
        return render_template(
            "dashboard.html",
            total_students=0,
            avg_marks=0,
            avg_study_hours=0,
            avg_attendance=0
        )

    df = pd.read_csv(DATA_FILE)

    total_students = len(df)
    avg_marks = round(df["exam_score"].mean(), 2)
    avg_study_hours = round(df["study_hours_per_day"].mean(), 2)
    avg_attendance = round(df["attendance_percentage"].mean(), 2)

    return render_template(
        "dashboard.html",
        total_students=total_students,
        avg_marks=avg_marks,
        avg_study_hours=avg_study_hours,
        avg_attendance=avg_attendance
    )


# ---------------- DATASET UPLOAD ---------------- #

@app.route("/upload")
def upload():
    return render_template("data_input.html")

#----------------csv upload-------------------#

@app.route("/upload_csv", methods=["GET", "POST"])
def upload_csv():

    if request.method == "POST":

        file = request.files["dataset"]

        if file.filename.endswith(".csv"):
            df = pd.read_csv(file)

        elif file.filename.endswith(".xlsx"):
            df = pd.read_excel(file)

        else:
            return "Unsupported file format"
        
        # Ensure required columns exist
        if "motivation_level" not in df.columns:
            df["motivation_level"] = 5   # default value
    
        df["source"] = "CSV"

        # ----------- NEW ADDITION (MERGE DATASET) -----------

        if os.path.exists(DATA_FILE):

            old_df = pd.read_csv(DATA_FILE)

            # Combine old + new dataset
            df = pd.concat([old_df, df], ignore_index=True)

        # ----------------------------------------------------

        # Save dataset
        df.drop_duplicates(inplace=True)
        df.to_csv(DATA_FILE, index=False)

        return redirect("/preprocessing")

    return render_template("upload_csv.html")

#---------------------------preprocessing-------------------------------

@app.route("/preprocessing", methods=["GET","POST"])
def preprocessing():

    if not os.path.exists(DATA_FILE):
        return redirect("/upload")

    df = pd.read_csv(DATA_FILE)

    # BEFORE PREPROCESSING
    before_rows = df.shape[0]
    before_cols = df.shape[1]
    before_missing = df.isnull().sum().sum()

    # HANDLE MISSING VALUES
    df.fillna(df.mean(numeric_only=True), inplace=True)

    # CLEAN DATASET
    df_clean = df

    # AFTER PREPROCESSING
    after_rows = df_clean.shape[0]
    after_cols = df_clean.shape[1]
    after_missing = df_clean.isnull().sum().sum()

    df_clean.to_csv(DATA_FILE, index=False)

    return render_template(
        "preprocessing.html",
        before_rows=before_rows,
        before_cols=before_cols,
        before_missing=before_missing,
        after_rows=after_rows,
        after_cols=after_cols,
        after_missing=after_missing
    )
# ---------------- STUDENT ENTRY PAGE ---------------- #

@app.route("/student_entry")
def student_entry():
    return render_template("student_entry.html")    

#------------------add student----------------------#
@app.route("/save_student", methods=["POST"])
def save_student():

    new_data = {
        "name": request.form["name"],
        "gender": request.form["gender"],
        "study_hours_per_day": float(request.form["study_hours_per_day"]),
        "attendance_percentage": float(request.form["attendance_percentage"]),
        "screen_time_hours": float(request.form["screen_time_hours"]),
        "entertainment_hours": float(request.form["entertainment_hours"]),
        "stress_level": float(request.form["stress_level"]),
        "motivation_level": float(request.form["motivation_level"]),
        "exam_anxiety": float(request.form["exam_anxiety"]),
        "major": request.form["major"],
        "exam_score": float(request.form["exam_score"]),
        "source": "Manual"
    }

    new_df = pd.DataFrame([new_data])

    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df = pd.concat([df, new_df], ignore_index=True)
    else:
        df = new_df

    df.to_csv(DATA_FILE, index=False)

    return redirect("/dashboard")    

# ---------------- VIEW STUDENTS ---------------- #

@app.route("/view_students")
def view_students():

    if not os.path.exists(DATA_FILE):
        return render_template("view_students.html", students=[])

    df = pd.read_csv(DATA_FILE)

    students = df.to_dict(orient="records")

    return render_template("view_students.html", students=students)
#-----------------EDIT STUDENT-----------------------#
@app.route("/edit_student/<int:index>")
def edit_student(index):

    df = pd.read_csv(DATA_FILE)

    student = df.iloc[index].to_dict()

    return render_template("edit_student.html", student=student, index=index)
# ---------------- DELETE STUDENTS PAGE ---------------- #

@app.route("/delete_students")
def delete_students():

    if not os.path.exists(DATA_FILE):
        return render_template("delete_students.html", students=[])

    df = pd.read_csv(DATA_FILE)

    students = df.to_dict(orient="records")

    return render_template("delete_students.html", students=students)

# ---------------- DELETE STUDENT ---------------- #

@app.route("/delete_student/<int:index>")
def delete_student(index):

    df = pd.read_csv(DATA_FILE)

    df = df.drop(index).reset_index(drop=True)

    df.to_csv(DATA_FILE, index=False)

    return redirect("/view_students?msg=deleted")

#------------------DELETE ENTIRE DATASET--------------#
@app.route("/delete_dataset")
def delete_dataset():

    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)

    return redirect("/upload")
#----------------UPDATE STUDNET--------------------#
@app.route("/update_student/<int:index>", methods=["POST"])
def update_student(index):

    df = pd.read_csv(DATA_FILE)

    df.loc[index, "name"] = request.form["name"]
    df.loc[index, "gender"] = request.form["gender"]
    df.loc[index, "study_hours_per_day"] = float(request.form["study_hours_per_day"])
    df.loc[index, "attendance_percentage"] = float(request.form["attendance_percentage"])
    df.loc[index, "screen_time_hours"] = float(request.form["screen_time_hours"])
    df.loc[index, "entertainment_hours"] = float(request.form["entertainment_hours"])
    df.loc[index, "stress_level"] = float(request.form["stress_level"])
    df.loc[index, "motivation_level"] = float(request.form["motivation_level"])
    df.loc[index, "exam_anxiety"] = float(request.form["exam_anxiety"])
    df.loc[index, "major"] = request.form["major"]
    df.loc[index, "exam_score"] = float(request.form["exam_score"])

    df.to_csv(DATA_FILE, index=False)

    return redirect("/view_students?msg=updated")
# ---------------- EDA VISUALIZATION ---------------- #
@app.route("/eda")
def eda():

    if not os.path.exists(DATA_FILE):
        return redirect("/upload")

    df = pd.read_csv(DATA_FILE)
        # correlation with exam score
    corr = df.corr(numeric_only=True)["exam_score"].sort_values(ascending=False)
    
    df.fillna(0, inplace=True)

    insights = []

    for feature, value in corr.items():

        if feature == "exam_score":
            continue

        if value > 0.5:
            insights.append(f"{feature.replace('_',' ').title()} strongly increases Exam Score ({value:.2f})")

        elif value > 0.2:
            insights.append(f"{feature.replace('_',' ').title()} moderately increases Exam Score ({value:.2f})")

        elif value < -0.5:
            insights.append(f"{feature.replace('_',' ').title()} strongly decreases Exam Score ({value:.2f})")

        elif value < -0.2:
            insights.append(f"{feature.replace('_',' ').title()} moderately decreases Exam Score ({value:.2f})")

    # Graph 1 - Study Hours vs Score (Regression)
    fig1 = px.scatter(
        df,
        x="study_hours_per_day",
        y="exam_score",
        trendline="ols",
        opacity=0.5,
        trendline_color_override="red",
        title="Study Hours vs Exam Score"
    )

    fig1.update_layout(width=900, height=500)

    # Graph 2 - Attendance vs Score
    fig2 = px.scatter(
        df,
        x="attendance_percentage",
        y="exam_score",
        trendline="ols",
        opacity=0.5,
        trendline_color_override="red",
        title="Attendance vs Exam Score"
    )

    fig2.update_layout(width=900, height=500)

    # Graph 3 - Stress vs Score
    fig3 = px.scatter(
        df,
        x="stress_level",
        y="exam_score",
        trendline="ols",
        opacity=0.5,
        trendline_color_override="red",
        title="Stress Level vs Exam Score"
    )

    fig3.update_layout(width=900, height=500)

    # Graph 4 - Screen Time vs Score
    fig4 = px.scatter(
        df,
        x="screen_time_hours",
        y="exam_score",
        trendline="ols",
        opacity=0.5,
        trendline_color_override="red",
        title="Screen Time vs Exam Score"
    )

    fig4.update_layout(width=900, height=500)
    
    # Graph 5 - Motivation level vs Score
    fig5 = px.scatter(
        df,
        x="motivation_level",
        y="exam_score",
        trendline="ols",
        opacity=0.5,
        trendline_color_override="red",
        title="motivation level vs Exam Score"
    )

    fig5.update_layout(width=900, height=500)

    # Graph 6 - Score Distribution
    fig6 = px.histogram(
        df,
        x="exam_score",
        nbins=50,
        title="Exam Score Distribution"
    )

    fig6.update_layout(width=900, height=500)
    
    #
    fig7 = px.box(
    df,
    x="stress_level",
    y="exam_score",
    title="Stress Level vs Exam Score Distribution"
    )
    
    fig7.update_layout(width=900, height=500)
    
    #
    fig8 = px.histogram(
    df,
    x="study_hours_per_day",
    nbins=30,
    title="Study Hours Distribution"
    )
    
    fig8.update_layout(width=900, height=500)
    
    #
    fig9 = px.box(
    df,
    x="major",
    y="exam_score",
    title="Exam Score Distribution by Major"
    )
    
    fig9.update_layout(width=900, height=500)

    chart1 = Markup(fig1.to_html(full_html=False))
    chart2 = Markup(fig2.to_html(full_html=False))
    chart3 = Markup(fig3.to_html(full_html=False))
    chart4 = Markup(fig4.to_html(full_html=False))
    chart5 = Markup(fig5.to_html(full_html=False))
    chart6 = Markup(fig6.to_html(full_html=False))
    chart7 = Markup(fig7.to_html(full_html=False))
    chart8 = Markup(fig8.to_html(full_html=False))
    chart9 = Markup(fig9.to_html(full_html=False))

    return render_template(
        "eda.html",
        chart1=chart1,
        chart2=chart2,
        chart3=chart3,
        chart4=chart4,
        chart5=chart5,
        chart6=chart6,
        chart7=chart7,
        chart8=chart8,
        chart9=chart9,
        insights=insights
    )

# ---------------- PREDICTION HOME ---------------- #

@app.route("/prediction")
def prediction():
    return render_template("prediction_home.html")


# ---------------- SINGLE PREDICTION FORM ---------------- #

@app.route("/single_prediction")
def single_prediction():
    return render_template("single_prediction.html")


# ---------------- BULK PREDICTION PAGE ---------------- #

@app.route("/bulk_prediction")
def bulk_prediction():
    return render_template("bulk_prediction.html")


# =========================================================
# SINGLE STUDENT PREDICTION
# =========================================================

@app.route("/predict_single", methods=["POST"])
def predict_single_student():

    study = float(request.form["study_hours_per_day"])
    attendance = float(request.form["attendance_percentage"])
    screen = float(request.form["screen_time_hours"])
    entertainment = float(request.form["entertainment_hours"])
    stress = float(request.form["stress_level"])
    anxiety = float(request.form["exam_anxiety"])
    gpa = float(request.form["previous_gpa"])
    motivation = float(request.form["motivation_level"])
    major = request.form["major"]

    # Convert GPA scale
    if gpa > 4:
        gpa = (gpa / 10) * 4

    input_dict = {
        "study_hours_per_day": study,
        "attendance_percentage": attendance,
        "screen_time": screen,
        "entertainment_hours": entertainment,
        "stress_level": stress,
        "exam_anxiety": anxiety,
        "previous_gpa": gpa,
        "motivation_level": motivation,
        "major": major
    }

    input_df = pd.DataFrame([input_dict])

    # Encode
    input_df = pd.get_dummies(input_df)

    # Match training columns
    input_df = input_df.reindex(columns=columns, fill_value=0)

    # Scale
    scaled_data = scaler.transform(input_df)

    # Predict
    prediction = model.predict(scaled_data)

    predicted_score = round(prediction[0], 2)
    predicted_score = max(0, min(100, predicted_score))

    # Performance level
    if predicted_score >= 80:
        performance = "Excellent"
    elif predicted_score >= 60:
        performance = "Good"
    elif predicted_score >= 40:
        performance = "Average"
    else:
        performance = "Needs Improvement"

    # Suggestions
    suggestions = []

    if study < 3:
        suggestions.append("Increase study hours to at least 4–5 hours daily.")

    if attendance < 75:
        suggestions.append("Maintain attendance above 80%.")

    if screen > 6:
        suggestions.append("Reduce screen time to improve concentration.")

    if stress > 7:
        suggestions.append("High stress detected. Practice relaxation techniques.")

    if motivation < 5:
        suggestions.append("Improve motivation using goal-based study planning.")

    if gpa < 2.5:
        suggestions.append("Focus on revision and concept clarity to improve GPA.")

    return render_template(
        "single_predict.html",
        score=predicted_score,
        performance=performance,
        suggestions=suggestions
    )


# =========================================================
# BULK DATASET PREDICTION
# =========================================================

@app.route("/bulk_predict", methods=["POST"])
def bulk_predict():

    file = request.files["dataset"]

    if file.filename.endswith(".csv"):
        df = pd.read_csv(file)

    elif file.filename.endswith(".xlsx"):
        df = pd.read_excel(file)

    else:
        return "Unsupported file format"

    # Merge entertainment columns if needed
    if "entertainment_hours" not in df.columns:

        if "social_media_hours" in df.columns and "netflix_hours" in df.columns:
            df["entertainment_hours"] = df["social_media_hours"] + df["netflix_hours"]

    # GPA conversion
    if "previous_gpa" in df.columns:

        df["previous_gpa"] = df["previous_gpa"].apply(
            lambda x: (x/10)*4 if x > 4 else x
        )

    # Encoding
    df_encoded = pd.get_dummies(df)

    # Align columns
    model_input = df_encoded.reindex(columns=columns, fill_value=0)

    # Scale
    scaled_data = scaler.transform(model_input)

    # Predict
    predictions = model.predict(scaled_data)

    df["predicted_exam_score"] = predictions
    df["predicted_exam_score"] = df["predicted_exam_score"].clip(0, 100)

    # Save output
    output_file = "predicted_results.csv"
    df.to_csv(output_file, index=False)

    return render_template(
        "bulk_predict.html",
        download_ready=True
    )


# =========================================================
# DOWNLOAD RESULT
# =========================================================

@app.route("/download_result")
def download_result():

    return send_file(
        "predicted_results.csv",
        as_attachment=True
    )
    
# ---------------- RUN APP ---------------- #

if __name__ == "__main__":
    app.run(debug=True)