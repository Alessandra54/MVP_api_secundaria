from flask import Flask, jsonify, request
from flask_restx import Api, Resource, fields
from config import Config
from database import db, init_db

app = Flask(__name__)
app.config.from_object(Config)
init_db(app)

# Criação do Swagger
api = Api(app, doc="/swagger")

# Definindo o Namespace
favoritas_ns = api.namespace('favoritas', description='Operações relacionadas às receitas favoritas')

# Definindo os Modelos para o Swagger
receita_model = api.model('Receita', {
    'titulo': fields.String(required=True, description='Título da receita'),
    'ingredientes': fields.String(required=True, description='Ingredientes da receita')
})

# Modelo de receitas favoritas
class ReceitaFavorita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    ingredientes = db.Column(db.String(500), nullable=False)

# Endpoint para adicionar e listar receitas favoritas
@favoritas_ns.route('/')
class ReceitaFavoritaLista(Resource):
    @api.doc('Listar todas as receitas favoritas')
    def get(self):
        receitas = ReceitaFavorita.query.all()
        resultado = [{"id": r.id, "titulo": r.titulo, "ingredientes": r.ingredientes} for r in receitas]
        return jsonify(resultado)

    @api.doc('Adicionar uma nova receita favorita')
    @api.expect(receita_model)
    def post(self):
        dados = request.json
        if not dados or 'titulo' not in dados or 'ingredientes' not in dados:
            return jsonify({"error": "Campos 'titulo' e 'ingredientes' são obrigatórios"}), 400
        
        nova_receita = ReceitaFavorita(titulo=dados['titulo'], ingredientes=dados['ingredientes'])
        db.session.add(nova_receita)
        db.session.commit()
        
        return jsonify({"message": "Receita adicionada com sucesso!"}), 201

# Endpoint para buscar, atualizar e deletar uma receita favorita por ID
@favoritas_ns.route('/<int:id>')
class ReceitaFavoritaDetalhe(Resource):
    @api.doc('Buscar uma receita favorita pelo ID')
    def get(self, id):
        receita = ReceitaFavorita.query.get(id)
        if not receita:
            return jsonify({"error": "Receita não encontrada"}), 404
        return jsonify({"id": receita.id, "titulo": receita.titulo, "ingredientes": receita.ingredientes})

    @api.doc('Atualizar uma receita favorita pelo ID')
    @api.expect(receita_model)
    def put(self, id):
        receita = ReceitaFavorita.query.get(id)
        if not receita:
            return jsonify({"error": "Receita não encontrada"}), 404
        
        dados = request.json
        receita.titulo = dados.get('titulo', receita.titulo)
        receita.ingredientes = dados.get('ingredientes', receita.ingredientes)
        
        db.session.commit()
        return jsonify({"message": "Receita atualizada com sucesso!"})

    @api.doc('Remover uma receita favorita pelo ID')
    def delete(self, id):
        receita = ReceitaFavorita.query.get(id)
        if not receita:
            return jsonify({"error": "Receita não encontrada"}), 404
        
        db.session.delete(receita)
        db.session.commit()
        return jsonify({"message": "Receita removida com sucesso!"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
