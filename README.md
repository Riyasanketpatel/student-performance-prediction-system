# Student Performance Prediction System

The Student Performance Prediction System is a machine learning based web application designed to predict student academic performance based on various lifestyle and study-related factors.

This project analyzes how factors such as study hours, attendance, screen time, stress levels, and exam anxiety influence student exam scores. Using machine learning models, the system predicts student performance and provides insights into the most influential factors affecting academic outcomes.

---

## Project Objective

The objective of this project is to build a predictive system that can estimate student exam performance using behavioral and academic features. This can help educators and students better understand how study habits and lifestyle choices impact academic success.

---

## Key Features

• Student performance prediction using machine learning  
• Web interface for entering student data  
• Dataset upload functionality for bulk predictions  
• Model training and evaluation  
• Interactive result display  
• Integration of multiple features affecting performance  

---

## Machine Learning Models Used

The system uses machine learning algorithms to train and evaluate predictive models.

Models implemented include:

• Linear Regression  
• Random Forest Regressor  
• Decision Tree Regressor  

These models are trained on a dataset containing student lifestyle and academic attributes, and the best performing model is used for prediction.

---

## Technologies Used

Backend:
- Python
- Flask

Machine Learning & Data Analysis:
- Pandas
- NumPy
- Scikit-learn

Frontend:
- HTML
- CSS
- JavaScript

Visualization:
- Matplotlib / Seaborn

---

## Dataset Features

The dataset includes several factors related to student lifestyle and academic behavior such as:

• Gender  
• Study Hours Per Day  
• Attendance Percentage  
• Screen Time Hours  
• Entertainment Hours  
• Stress Level  
• Exam Anxiety  
• Academic Major  
• Exam Score  

These features are used to train machine learning models for predicting exam scores.

---

## Project Structure

student-performance-prediction-system

dataset/  
templates/  
static/  
model/  
app.py  
train_model.py  
requirements.txt  
README.md  

---

## How to Run the Project

1. Clone the repository

git clone https://github.com/Riyasanketpatel/student-performance-prediction-system.git

2. Navigate to the project directory

cd student-performance-prediction-system

3. Install required libraries

pip install -r requirements.txt

4. Run the application

python app.py

5. Open the application in your browser

http://127.0.0.1:5000/

---

## Conclusion

This project demonstrates how machine learning can be used to analyze and predict academic performance based on student lifestyle factors. It highlights the importance of data-driven insights in understanding the relationship between habits and educational outcomes.

http://127.0.0.1:5000/
