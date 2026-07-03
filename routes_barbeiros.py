from flask import Blueprint, request, jsonify
from database import get_connection

# Blueprint agrupa rotas relacionadas a "barbeiros"
barbeiros_bp = Blueprint("barbeiros", __name__)

@barbeiros_bp.route("/barbeiros", methods=["POST"])
def cadastrar_barbeiro():
    """
    Cadastrar um novo barbeiro
    ---
    tags:
      - Barbeiros
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            nome:
              type: string
              example: João Pedro
            telefone:
              type: string
              example: "(21) 99999-9999"
    responses:
      201:
        description: Barbeiro cadastrado com sucesso
      400:
        description: Campo 'nome' não foi enviado
    """
    dados = request.get_json()
    nome = dados.get("nome")
    telefone = dados.get("telefone")

    if not nome:
        return jsonify({"erro": "O campo 'nome' é obrigatório"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO barbeiros (nome, telefone) VALUES (?, ?)", (nome, telefone))
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()

    return jsonify({"id": novo_id, "nome": nome, "telefone": telefone}), 201

@barbeiros_bp.route("/barbeiros", methods=["GET"])
def listar_barbeiros():
    """
    Listar todos os barbeiros
    ---
    tags:
      - Barbeiros
    responses:
      200:
        description: Lista de barbeiros cadastrados
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM barbeiros")
    barbeiros = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(barbeiros), 200


@barbeiros_bp.route("/barbeiros/<int:id>", methods=["DELETE"])
def remover_barbeiro(id):
    """
    Remover um barbeiro
    ---
    tags:
      - Barbeiros
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        example: 1
    responses:
      200:
        description: Barbeiro removido com sucesso
      404:
        description: Barbeiro não encontrado
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM barbeiros WHERE id = ?", (id,))
    barbeiro = cursor.fetchone()

    if not barbeiro:
        conn.close()
        return jsonify({"erro": "Barbeiro não encontrado"}), 404

    cursor.execute("DELETE FROM barbeiros WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return jsonify({"mensagem": "Barbeiro removido com sucesso"}), 200

@barbeiros_bp.route("/barbeiros/<int:id>", methods=["PUT"])
def atualizar_barbeiro(id):
  """
  Atualizar dados de um barbeiro
  ---
  tags:
    - Barbeiros
  parameters:
    - name: id
      in: path
      type: integer
      required: true
      example: 1
    - name: body
      in: body
      required: true
      schema:
        type: object
        properties:
          nome:
            type: string
            example: João Pedro
          telefone:
            type: string
            example: "(21) 99999-9999"
  responses:
    200:
      description: Barbeiro atualizado com sucesso
    400:
      description: Campo 'nome' não foi enviado
    404:
      description: Barbeiro não encontrado
  """
  dados = request.get_json()
  nome = dados.get("nome")
  telefone = dados.get("telefone")

  if not nome:
      return jsonify({"erro": "O campo 'nome' é obrigatório"}), 400

  conn = get_connection()
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM barbeiros WHERE id = ?", (id,))
  barbeiro = cursor.fetchone()

  if not barbeiro:
      conn.close()
      return jsonify({"erro": "Barbeiro não encontrado"}), 404

  cursor.execute("UPDATE barbeiros SET nome = ?, telefone = ? WHERE id = ?", (nome, telefone, id))
  conn.commit()
  conn.close()

  return jsonify({"id": id, "nome": nome, "telefone": telefone}), 200