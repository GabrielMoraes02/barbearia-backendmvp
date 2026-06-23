from flask import Blueprint, request, jsonify
from database import get_connection

cortes_bp = Blueprint("cortes", __name__)

FORMAS_PAGAMENTO_VALIDAS = ["Dinheiro", "Cartão de Débito", "Cartão de Crédito", "Pix"]


@cortes_bp.route("/cortes", methods=["POST"])
def registrar_corte():
    """
    Registrar um atendimento (pode ter um ou mais serviços)
    ---
    tags:
      - Cortes
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            barbeiro_id:
              type: integer
              example: 1
            tipos_corte_ids:
              type: array
              items:
                type: integer
              example: [1, 2]
            data:
              type: string
              example: "2026-06-22"
            forma_pagamento:
              type: string
              example: "Pix"
    responses:
      201:
        description: Atendimento registrado com sucesso
      400:
        description: Campos obrigatórios não enviados ou inválidos
    """
    dados = request.get_json()
    barbeiro_id = dados.get("barbeiro_id")
    tipos_corte_ids = dados.get("tipos_corte_ids")
    data = dados.get("data")
    forma_pagamento = dados.get("forma_pagamento")

    if not barbeiro_id or not tipos_corte_ids or not data or not forma_pagamento:
        return jsonify({"erro": "Os campos 'barbeiro_id', 'tipos_corte_ids' (lista), 'data' e 'forma_pagamento' são obrigatórios"}), 400

    if not isinstance(tipos_corte_ids, list) or len(tipos_corte_ids) == 0:
        return jsonify({"erro": "'tipos_corte_ids' deve ser uma lista com pelo menos um item"}), 400

    if forma_pagamento not in FORMAS_PAGAMENTO_VALIDAS:
        return jsonify({"erro": f"forma_pagamento deve ser uma de: {FORMAS_PAGAMENTO_VALIDAS}"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    # Cria o atendimento (corte "pai")
    cursor.execute(
        "INSERT INTO cortes (barbeiro_id, data, forma_pagamento) VALUES (?, ?, ?)",
        (barbeiro_id, data, forma_pagamento)
    )
    corte_id = cursor.lastrowid

    # Cria um item para cada serviço incluso nesse atendimento
    for tipo_corte_id in tipos_corte_ids:
        cursor.execute(
            "INSERT INTO corte_itens (corte_id, tipo_corte_id) VALUES (?, ?)",
            (corte_id, tipo_corte_id)
        )

    conn.commit()
    conn.close()

    return jsonify({
        "id": corte_id,
        "barbeiro_id": barbeiro_id,
        "tipos_corte_ids": tipos_corte_ids,
        "data": data,
        "forma_pagamento": forma_pagamento
    }), 201


@cortes_bp.route("/cortes", methods=["GET"])
def listar_cortes():
    """
    Listar atendimentos realizados, com seus serviços e valor total
    ---
    tags:
      - Cortes
    parameters:
      - name: barbeiro_id
        in: query
        type: integer
        required: false
      - name: data
        in: query
        type: string
        required: false
        example: "2026-06-22"
    responses:
      200:
        description: Lista de atendimentos, cada um com seus serviços e valor total
    """
    barbeiro_id = request.args.get("barbeiro_id")
    data = request.args.get("data")

    query = """
        SELECT cortes.id, cortes.data, cortes.forma_pagamento,
               barbeiros.id AS barbeiro_id, barbeiros.nome AS barbeiro_nome
        FROM cortes
        JOIN barbeiros ON cortes.barbeiro_id = barbeiros.id
        WHERE 1=1
    """
    parametros = []

    if barbeiro_id:
        query += " AND cortes.barbeiro_id = ?"
        parametros.append(barbeiro_id)

    if data:
        query += " AND cortes.data = ?"
        parametros.append(data)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, parametros)
    cortes = [dict(row) for row in cursor.fetchall()]

    # Para cada atendimento, busca os serviços inclusos e soma o valor total
    for corte in cortes:
        cursor.execute("""
            SELECT tipos_corte.id, tipos_corte.nome, tipos_corte.valor
            FROM corte_itens
            JOIN tipos_corte ON corte_itens.tipo_corte_id = tipos_corte.id
            WHERE corte_itens.corte_id = ?
        """, (corte["id"],))
        servicos = [dict(row) for row in cursor.fetchall()]

        corte["servicos"] = servicos
        corte["valor_total"] = sum(s["valor"] for s in servicos)

    conn.close()

    return jsonify(cortes), 200


@cortes_bp.route("/cortes/<int:id>", methods=["DELETE"])
def remover_corte(id):
    """
    Remover um atendimento (e seus serviços inclusos)
    ---
    tags:
      - Cortes
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        example: 1
    responses:
      200:
        description: Atendimento removido com sucesso
      404:
        description: Atendimento não encontrado
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cortes WHERE id = ?", (id,))
    corte = cursor.fetchone()

    if not corte:
        conn.close()
        return jsonify({"erro": "Atendimento não encontrado"}), 404

    # Remove primeiro os itens (serviços) ligados a esse atendimento, depois o atendimento
    cursor.execute("DELETE FROM corte_itens WHERE corte_id = ?", (id,))
    cursor.execute("DELETE FROM cortes WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return jsonify({"mensagem": "Atendimento removido com sucesso"}), 200