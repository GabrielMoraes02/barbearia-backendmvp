from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from database import init_db
from routes_barbeiros import barbeiros_bp
from routes_tipos_corte import tipos_corte_bp
from routes_cortes import cortes_bp
from routes_agendamentos import agendamentos_bp
from routes_relatorios import relatorios_bp

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)
app.config["SWAGGER"] = {
    "title": "API Barbearia",
    "uiversion": 3
}
swagger = Swagger(app)

app.register_blueprint(barbeiros_bp)
app.register_blueprint(tipos_corte_bp)
app.register_blueprint(cortes_bp)
app.register_blueprint(agendamentos_bp)
app.register_blueprint(relatorios_bp)

@app.route("/")
def home():
    return "API da Barbearia rodando!"

if __name__ == "__main__":
    init_db()
    app.run(debug=True)