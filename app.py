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
            'contenido': (
                '<p>Los exoplanetas son planetas que orbitan estrellas fuera de nuestro sistema solar. '
                'Desde el descubrimiento de 51 Pegasi b en 1995, se han confirmado miles de exoplanetas mediante diversos métodos.</p>'
                '<h3>Métodos de detección</h3>'
                '<ul>'
                '<li><strong>Tránsito:</strong> mide la disminución de brillo de una estrella cuando un planeta pasa por delante.</li>'
                '<li><strong>Velocidad radial:</strong> detecta el bamboleo de la estrella por la gravedad del planeta.</li>'
                '<li><strong>Imagen directa:</strong> captura luz del planeta separándolo del resplandor estelar.</li>'
                '<li><strong>Microlente:</strong> observa cómo la gravedad de una estrella/planeta magnifica la luz de otra estrella.</li>'
                '</ul>'
                '<p>Estos métodos nos permiten estimar el periodo orbital, el tamaño, y en algunos casos la masa y la atmósfera de los planetas.</p>'
                '<h3>Misiones y telescopios</h3>'
                '<p>Misiones como Kepler, TESS y CHEOPS han revolucionado la búsqueda de exoplanetas, mientras que el Telescopio Espacial James Webb '
                'estudia sus atmósferas para detectar compuestos como vapor de agua, CO₂ y metano.</p>'
                '<h3>Importancia científica</h3>'
                '<p>El estudio de exoplanetas ayuda a entender la formación planetaria, la arquitectura de sistemas y la posible existencia de vida fuera de la Tierra.</p>'
            )
        },
        'caracteristicas': {
            'titulo': 'Características de los exoplanetas',
            'contenido': (
                '<p>Los exoplanetas presentan una gran diversidad: desde mundos rocosos similares a la Tierra hasta gigantes gaseosos y '
                'sub-Neptunos. Sus propiedades dependen de su composición, distancia a la estrella y condiciones de formación.</p>'
                '<h3>Tipos comunes</h3>'
                '<ul>'
                '<li><strong>Rocosos:</strong> de tamaño similar a la Tierra o supertierras.</li>'
                '<li><strong>Sub-Neptunos:</strong> entre 1.5 y 4 radios terrestres, con envolturas gaseosas.</li>'
                '<li><strong>Gigantes gaseosos:</strong> tamaños similares a Júpiter o mayores.</li>'
                '</ul>'
                '<h3>Zonas habitables</h3>'
                '<p>La zona habitable es la región donde el agua líquida podría existir en superficie, pero la habitabilidad real también '
                'depende de la atmósfera, el campo magnético y la actividad estelar.</p>'
                '<h3>Parámetros clave</h3>'
                '<ul>'
                '<li><strong>Densidad y composición:</strong> distinguen mundos rocosos de gaseosos.</li>'
                '<li><strong>Excentricidad orbital:</strong> influye en variaciones climáticas.</li>'
                '<li><strong>Metallicidad estelar:</strong> correlaciona con frecuencia de gigantes gaseosos.</li>'
                '</ul>'
                '<h3>Atmósferas</h3>'
                '<p>La espectroscopía de transmisión y emisión permite estudiar nubes, brumas y moléculas clave, aportando pistas sobre procesos geológicos y climáticos.</p>'
            )
        },
        'mas-conocidos': {
            'titulo': 'Exoplanetas más conocidos',
            'contenido': (
                '<ul>'
                '<li><strong>TRAPPIST-1e:</strong> uno de los siete planetas rocosos del sistema TRAPPIST-1; posible zona habitable.</li>'
                '<li><strong>Proxima b:</strong> planeta rocoso alrededor de la estrella más cercana al Sol; sujeto a fuertes fulguraciones.</li>'
                '<li><strong>Kepler-22b:</strong> supertierra en la zona habitable de su estrella; atmósfera aún bajo estudio.</li>'
                '</ul>'
                '<p>Estos mundos son objetivos clave para misiones futuras y observatorios como el JWST, que estudian atmósferas y '
                'posibles biofirmas.</p>'
                '<h3>Otros destacados</h3>'
                '<ul>'
                '<li><strong>HD 209458 b (Osiris):</strong> «Júpiter caliente» con atmósfera evaporándose.</li>'
                '<li><strong>Kepler-452b:</strong> supertierra en la zona habitable de una estrella tipo Sol.</li>'
                '<li><strong>K2-18 b:</strong> muestra indicios de compuestos volátiles en su atmósfera.</li>'
                '</ul>'
                '<p>Estos casos ilustran la diversidad extrema de tamaños, temperaturas y composiciones presentes en nuestra galaxia.</p>'
            )
        }
    }
    data = mapping.get(slug)
    if not data:
        data = {'titulo': 'Tema no encontrado', 'contenido': '<p>El contenido solicitado no está disponible.</p>'}
    return render_template('tema.html', **data)

if __name__ == "__main__":
    app.run(debug=True)
