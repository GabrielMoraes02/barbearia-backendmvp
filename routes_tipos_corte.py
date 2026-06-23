from flask import Blueprint, request, jsonify
from database import get_connection

tipos_corte_bp = Blueprint("tipos_corte", __name__)

@tipos_corte_bp.route("/tipos_corte", methods=["POST"])
def cadastrar_tipo_corte():
    """
    Cadastrar um novo tipo de corte
    ---
    tags:
      - Tipos de Corte
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            nome:
              type: string
              example: Corte simples
            valor:
              type: number
              example: 30.00
    responses:
      201:
        description: Tipo de corte cadastrado com sucesso
      400:
        description: Campos obrigatórios não enviados
    """
    dados = request.get_json()
    nome = dados.get("nome")
    valor = dados.get("valor")

    if not nome or valor is None:
        return jsonify({"erro": "Os campos 'nome' e 'valor' são obrigatórios"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tipos_corte (nome, valor) VALUES (?, ?)", (nome, valor))
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()

    return jsonify({"id": novo_id, "nome": nome, "valor": valor}), 201


@tipos_corte_bp.route("/tipos_corte", methods=["GET"])
def listar_tipos_corte():
    """
    Listar todos os tipos de corte
    ---
    tags:
      - Tipos de Corte
    responses:
      200:
        description: Lista de tipos de corte cadastrados
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tipos_corte")
    tipos = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(tipos), 200


@tipos_corte_bp.route("/tipos_corte/<int:id>", methods=["DELETE"])
def remover_tipo_corte(id):
    """
    Remover um tipo de corte
    ---
    tags:
      - Tipos de Corte
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        example: 1
    responses:
      200:
        description: Tipo de corte removido com sucesso
      404:
        description: Tipo de corte não encontrado
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tipos_corte WHERE id = ?", (id,))
    tipo = cursor.fetchone()

    if not tipo:
        conn.close()
        return jsonify({"erro": "Tipo de corte não encontrado"}), 404

    cursor.execute("DELETE FROM tipos_corte WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return jsonify({"mensagem": "Tipo de corte removido com sucesso"}), 200