from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import json
import pickle
import traceback
import logging

app = Flask(__name__)
app.secret_key = 'key'  # Replace with a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://wristwatcher:id_i78dIG!f5---@138.3.255.133:3306/WristWatch_AI'

db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    """
    A class representing a user in the application.

    Attributes:
    __tablename__ (str): The name of the table in the database.
    id (db.Column): The primary key column for the user.
    username (db.Column): The username column for the user.
    email (db.Column): The email column for the user.
    password (db.Column): The password column for the user.
    """

    __tablename__ = 'User'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# Create the database and tables
with app.app_context():
    try:
        print("Successfully connected to DB.")
    except Exception as e:
        print("Failed to connect to DB.")
        traceback.print_exc()

# Load the full model package (model + encoders)
with open("static/models/rfr_wristwatch_price_model.pkl", "rb") as f:
   prediction_model_data = pickle.load(f)

model = prediction_model_data["model"]
expected_features = prediction_model_data["features"]
numeric_features = prediction_model_data["numeric_features"]
categorical_features = prediction_model_data["categorical_features"]
mlb_functions = prediction_model_data["mlb_funkce"]
ohe = prediction_model_data["ohe"]

# Load the second model package (model + encoders)
with open("static/models/rfc_wristwatch_usage_model_v3.pkl", "rb") as f:
    usage_model_data = pickle.load(f)

usage_model = usage_model_data["model"]
usage_expected_features = usage_model_data["features"]
usage_numeric_features = usage_model_data["numeric_features"]
usage_categorical_features = usage_model_data["categorical_features"]
usage_mlb_functions = usage_model_data["mlb_funkce"]
usage_mlb_usage = usage_model_data["mlb_pouziti"]
#usage_ohe = usage_model_data["ohe"]

# Build for rendering form choices (optional, static for now)
# Load the attribute choices from the JSON file
with open("static/files/multiple_choice_features_cleaned.json", "r", encoding="utf-8") as file:
   attribute_choices = json.load(file)

@app.route("/", methods=["GET"])
def index():
    """
    This function handles the rendering of the home page for authenticated users.
    If the user is not authenticated, they are redirected to the login page.

    Parameters:
    None

    Returns:
    render_template: A rendered HTML template for the home page if the user is authenticated.
        - numeric_features: A list of numeric features required for the prediction form.
        - attribute_choices: A dictionary containing attribute choices for the prediction form.
        - form_data: An empty dictionary representing the initial form data.
        - predicted_price: A placeholder value for the predicted price, initially set to None.

    redirect: A redirection to the login page if the user is not authenticated.
    """
    if 'username' in session:
        return render_template(
            "index.html",
            numeric_features=numeric_features,
            attribute_choices=attribute_choices,
            form_data={},
            predicted_price=None
        )
    return redirect(url_for('login'))

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Handles the user login process. It checks if the user is making a POST request,
    retrieves the username and password from the form data, and attempts to authenticate the user.
    If the user is authenticated, it sets the 'username' in the session and redirects the user to the index page.
    If the user is not authenticated, it returns an error message.

    Parameters:
    None

    Returns:
    render_template: A rendered HTML template with an error message if the user's credentials are invalid.
    redirect: A redirection to the index page if the user is successfully authenticated.
    """
    error = None
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            error = "Invalid credentials. Please try again."
    return render_template("login.html", error=error)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route("/register", methods=["GET", "POST"])
def register():
    """
    This function handles the user registration process. It checks if the user is making a POST request,
    retrieves the username, email, and password from the form data, and attempts to register the user.
    If the user already exists, it returns an error message. If the registration is successful, it logs the
    event and redirects the user to the login page.

    Parameters:
    None

    Returns:
    render_template: A rendered HTML template with an error message if the user already exists or if an error occurs during registration.
    redirect: A redirection to the login page if the registration is successful.
    """
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        try:
            # Re-query from DB directly, not polluted session
            db.session.expire_all()

            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                error = "Username already exists. Please choose a different username."
                return render_template("register.html", error=error)

            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            logger.info(f"New user registered: {username}, {email}")
            return redirect(url_for('login'))

        except Exception as e:
            db.session.rollback()
            logger.error("Error registering user", exc_info=True)
            return render_template("register.html", error="Failed to register user.")
    return render_template("register.html")

@app.route("/logout", methods=["POST"])
def logout():
    """
    This function handles the user logout process. It removes the 'username' from the session
    and redirects the user to the login page.

    Parameters:
    None

    Returns:
    redirect: A redirection to the login page after the user has been successfully logged out.
    """
    session.pop('username', None)
    return redirect(url_for('login'))


def prepare_input_data(input_df, functions_vector, encoded_single_labels):
    """
    Prepares input data for the usage prediction model by concatenating the input DataFrame,
    functions vector, and encoded single labels. It also handles missing columns by adding them
    with default values (0).

    Parameters:
    input_df (pandas.DataFrame): The input DataFrame containing numeric and categorical features.
    functions_vector (pandas.DataFrame): The DataFrame representing the multi-label functions vector.
    encoded_single_labels (pandas.DataFrame): The DataFrame representing the encoded single labels.

    Returns:
    pandas.DataFrame: The prepared input DataFrame with the same columns as the usage prediction model's expected features.
    """
    data_input_df = pd.concat([input_df, functions_vector, encoded_single_labels], axis=1)
    missing_cols = [col for col in usage_expected_features if col not in data_input_df.columns]
    if missing_cols:
        missing_df = pd.DataFrame([[0] * len(missing_cols)], columns=missing_cols)
        data_input_df = pd.concat([data_input_df, missing_df], axis=1)

    return data_input_df[usage_expected_features]

@app.route("/aboutus", methods=["GET"])
def about_us():
    """
    This function handles the rendering of the about us page for authenticated users.
    If the user is not authenticated, they are redirected to the login page.

    Parameters:
    None

    Returns:
    render_template: A rendered HTML template for the about us page if the user is authenticated.
    redirect: A redirection to the login page if the user is not authenticated.
    """
    if 'username' in session:
        return render_template("about-us.html")
    return redirect(url_for('login'))

@app.route("/contact", methods=["GET"])
def contact():
    """
    This function handles the contact page rendering for authenticated users.
    If the user is not authenticated, they are redirected to the login page.

    Parameters:
    None

    Returns:
    render_template: A rendered HTML template for the contact page if the user is authenticated.
    redirect: A redirection to the login page if the user is not authenticated.
    """
    if 'username' in session:
        return render_template("contact.html")
    return redirect(url_for('login'))

@app.route("/", methods=["POST"])
def predict():
    """
    This function handles the prediction process for wristwatch prices and usage based on user input.
    It retrieves form data, processes numeric and categorical features, prepares input for the models,
    makes predictions, and returns the results to the user interface.

    Parameters:
    None

    Returns:
    render_template: A rendered HTML template with the predicted price and usage, or an error message.
    """
    if 'username' not in session:
        return redirect(url_for('login'))
    try:
        form_data = request.form.to_dict(flat=False)
        input_data = {}

        # Process numeric features
        for feature in numeric_features:
            value = form_data.get(feature, [''])[0]
            input_data[feature] = float(value) if value else 0.0

        # Multi-label features
        functions = form_data.get("Funkce", [])
        functions_vector = pd.DataFrame(
            mlb_functions.transform([functions]),
            columns=mlb_functions.classes_
        )
        # Encode other categorical fields
        single_label_data = {}
        for feature in categorical_features:
            value = form_data.get(feature, [''])[0]
            single_label_data[feature] = value if value else "Neznámé"

        encoded_single_labels = pd.DataFrame(
            ohe.transform(pd.DataFrame([single_label_data])).toarray(),
            columns=ohe.get_feature_names_out(categorical_features)
        )

        # Final combined input for price prediction
        input_df = pd.DataFrame([input_data])

        # Reorder columns to match the model input
        full_input = prepare_input_data(input_df, functions_vector, encoded_single_labels)
        # Predict price
        price_prediction = model.predict(full_input)[0]
        predicted_price = f"{int(price_prediction):,}".replace(",", " ")

        # Prepare input for usage prediction
        usage_input_df = prepare_input_data(input_df, functions_vector, encoded_single_labels)

        # Predict usage
        usage_prediction = usage_model.predict(usage_input_df)
        predicted_usage = usage_mlb_usage.inverse_transform(usage_prediction)[0]

    except Exception as e:
        predicted_price = f"Error: {str(e)}"
        predicted_usage = []
        traceback.print_exc()
    return render_template(
            "index.html",
            numeric_features=numeric_features,
            attribute_choices=attribute_choices,
            form_data=request.form,
            predicted_price=predicted_price,
            predicted_usage=predicted_usage
        )

if __name__ == "__main__":
   app.run(debug=True)

