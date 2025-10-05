from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import numpy as np
import joblib

app = Flask(__name__)

# -------------------------------
# Cargar el modelo entrenado
# -------------------------------
model = joblib.load("model.pkl")
G = 2.959122082855911e-4

# -------------------------------
# Página principal
# -------------------------------
@app.route("/identificador", methods=["GET", "POST"])
def identificador():
    prediction = None
    if request.method == "POST":
        # Columnas que el usuario debe llenar
        columns = ["period", "duration", "depth", "planet_radius", 
                   "stellar_teff", "stellar_radius", "stellar_mass", "insolation"]

        # Obtener datos del formulario y convertir a float
        user_data = []
        for col in columns:
            val = float(request.form[col])
            user_data.append(val)

        # Crear DataFrame con los datos del usuario
        user_df = pd.DataFrame([user_data], columns=columns)

        # Calcular parámetros físicos
        user_df["a"] = ((G * user_df["stellar_mass"] * user_df["period"]**2) / (4 * np.pi**2))**(1/3)
        user_df["b"] = np.sqrt((1 + user_df["planet_radius"]/user_df["stellar_radius"])**2 -
                               (np.pi * user_df["a"] * user_df["duration"] / 
                                (user_df["period"] * user_df["stellar_radius"]))**2)

        # Predecir
        pred = model.predict(user_df)[0]

        # Convertir a texto
        if pred == 2:
            prediction = "Exoplaneta confirmado"
        elif pred == 1:
            prediction = "Candidato a exoplaneta"
        else:
            prediction = "No es un exoplaneta"
    return render_template("index.html", prediction=prediction)


# -------------------------------
# Rutas de navegación
# -------------------------------
@app.route("/")
def root():
    return redirect(url_for('portada'))


@app.route("/portada")
def portada():
    return render_template("portada.html")


@app.route("/menu")
def menu_principal():
    return render_template("menu.html")


@app.route("/contenidos")
def contenidos():
    return render_template("contenidos.html")


@app.route("/herramienta")
def herramienta():
    return render_template("herramienta.html")


@app.route("/buscar")
def buscar():
    q = request.args.get('q', '')
    return render_template("buscar.html", q=q)


@app.route('/tema/<slug>')
def tema(slug: str):
    mapping = {
        'que-son-los-exoplanetas': {
            'titulo': '¿Qué son los exoplanetas?',
            'contenido': '<p>Los exoplanetas son planetas que orbitan estrellas fuera de nuestro sistema solar.</p>'
        },
        'caracteristicas': {
            'titulo': 'Características de los exoplanetas',
            'contenido': '<p>Pueden ser rocosos, gaseosos o intermedios; varían en tamaño, masa y órbita.</p>'
        },
        'mas-conocidos': {
            'titulo': 'Exoplanetas más conocidos',
            'contenido': '<ul><li>TRAPPIST-1e</li><li>Proxima b</li><li>Kepler-22b</li></ul>'
        }
    }
    data = mapping.get(slug)
    if not data:
        data = {'titulo': 'Tema no encontrado', 'contenido': '<p>El contenido solicitado no está disponible.</p>'}
    return render_template('tema.html', **data)

if __name__ == "__main__":
    app.run(debug=True)
