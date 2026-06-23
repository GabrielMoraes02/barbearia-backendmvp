from flask import Blueprint, request, jsonify
from database import get_connection

agendamentos_bp = Blueprint("agendamentos", __name__)

@agendamentos_bp.route("/agendamentos", methods=["POST"])
def criar_agendamento():
    """
    Criar um agendamento
    ---
    tags:
      - Agendamentos
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
            nome_cliente:
              type: string
              example: Marcos Silva
            data_hora:
              type: string
              example: "2026-06-25 14:30"
            tipo_corte_id:
              type: integer
              example: 1
    responses:
      201:
        description: Agendamento criado com sucesso
      400:
        description: Campos obrigatórios não enviados
      409:
        description: Horário já ocupado para esse barbeiro
    """
    dados = request.get_json()
    barbeiro_id = dados.get("barbeiro_id")
    nome_cliente = dados.get("nome_cliente")
    data_hora = dados.get("data_hora")
    tipo_corte_id = dados.get("tipo_corte_id")  # opcional

    if not barbeiro_id or not nome_cliente or not data_hora:
        return jsonify({"erro": "Os campos 'barbeiro_id', 'nome_cliente' e 'data_hora' são obrigatórios"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    # Verifica se já existe agendamento ativo nesse horário para esse barbeiro
    cursor.execute("""
        SELECT * FROM agendamentos
        WHERE barbeiro_id = ? AND data_hora = ? AND status = 'agendado'
    """, (barbeiro_id, data_hora))
    conflito = cursor.fetchone()

    if conflito:
        conn.close()
        return jsonify({"erro": "Esse barbeiro já tem um agendamento nesse horário"}), 409

    cursor.execute("""
        INSERT INTO agendamentos (barbeiro_id, tipo_corte_id, nome_cliente, data_hora, status)
        VALUES (?, ?, ?, ?, 'agendado')
    """, (barbeiro_id, tipo_corte_id, nome_cliente, data_hora))
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "id": novo_id,
        "barbeiro_id": barbeiro_id,
        "nome_cliente": nome_cliente,
        "data_hora": data_hora,
        "status": "agendado"
    }), 201


@agendamentos_bp.route("/agendamentos", methods=["GET"])
def listar_agendamentos():
    """
    Listar agendamentos (nome do cliente, horário e barbeiro)
    ---
    tags:
      - Agendamentos
    parameters:
      - name: barbeiro_id
        in: query
        type: integer
        required: false
      - name: data
        in: query
        type: string
        required: false
        example: "2026-06-25"
    responses:
      200:
        description: Lista de agendamentos
    """
    barbeiro_id = request.args.get("barbeiro_id")
    data = request.args.get("data")

    query = """
        SELECT agendamentos.id, agendamentos.nome_cliente, agendamentos.data_hora, agendamentos.status,
               barbeiros.id AS barbeiro_id, barbeiros.nome AS barbeiro_nome
        FROM agendamentos
        JOIN barbeiros ON agendamentos.barbeiro_id = barbeiros.id
        WHERE 1=1
    """
    parametros = []

    if barbeiro_id:
        query += " AND agendamentos.barbeiro_id = ?"
        parametros.append(barbeiro_id)

    if data:
        query += " AND agendamentos.data_hora LIKE ?"
        parametros.append(f"{data}%")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, parametros)
    agendamentos = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(agendamentos), 200


@agendamentos_bp.route("/agendamentos/<int:id>", methods=["DELETE"])
def cancelar_agendamento(id):
    """
    Cancelar um agendamento
    ---
    tags:
      - Agendamentos
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        example: 1
    responses:
      200:
        description: Agendamento cancelado com sucesso
      404:
        description: Agendamento não encontrado
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agendamentos WHERE id = ?", (id,))
    agendamento = cursor.fetchone()

    if not agendamento:
        conn.close()
        return jsonify({"erro": "Agendamento não encontrado"}), 404

    cursor.execute("DELETE FROM agendamentos WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return jsonify({"mensagem": "Agendamento cancelado com sucesso"}), 200


# Horário de funcionamento da barbearia: 08h às 20h, de hora em hora
HORARIOS_DISPONIVEIS = [f"{h:02d}:00" for h in range(8, 21)]

@agendamentos_bp.route("/agendamentos/disponibilidade", methods=["GET"])
def consultar_disponibilidade():
    """
    Consultar disponibilidade de horários de um barbeiro em um dia
    ---
    tags:
      - Agendamentos
    parameters:
      - name: barbeiro_id
        in: query
        type: integer
        required: true
        example: 1
      - name: data
        in: query
        type: string
        required: true
        example: "2026-06-25"
    responses:
      200:
        description: Lista de horários com status (disponivel ou ocupado)
      400:
        description: Parâmetros obrigatórios não enviados
    """
    barbeiro_id = request.args.get("barbeiro_id")
    data = request.args.get("data")

    if not barbeiro_id or not data:
        return jsonify({"erro": "Os parâmetros 'barbeiro_id' e 'data' são obrigatórios"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT data_hora FROM agendamentos
        WHERE barbeiro_id = ? AND data_hora LIKE ? AND status = 'agendado'
    """, (barbeiro_id, f"{data}%"))
    ocupados = [row["data_hora"] for row in cursor.fetchall()]
    conn.close()

    # Monta a lista de horários, marcando cada um como disponivel ou ocupado
    resultado = []
    for horario in HORARIOS_DISPONIVEIS:
        data_hora_completa = f"{data} {horario}"
        status = "ocupado" if data_hora_completa in ocupados else "disponivel"
        resultado.append({"horario": horario, "status": status})

    return jsonify(resultado), 200