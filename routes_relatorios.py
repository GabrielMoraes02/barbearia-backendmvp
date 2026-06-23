from flask import Blueprint, request, jsonify
from database import get_connection

relatorios_bp = Blueprint("relatorios", __name__)


@relatorios_bp.route("/relatorio", methods=["GET"])
def relatorio_semanal():
    """
    Relatório de faturamento por barbeiro em um intervalo de datas
    ---
    tags:
      - Relatórios
    parameters:
      - name: data_inicio
        in: query
        type: string
        required: true
        example: "2026-06-22"
      - name: data_fim
        in: query
        type: string
        required: true
        example: "2026-06-28"
    responses:
      200:
        description: Faturamento por barbeiro no período
      400:
        description: Parâmetros obrigatórios não enviados
    """
    data_inicio_str = request.args.get("data_inicio")
    data_fim_str = request.args.get("data_fim")

    if not data_inicio_str or not data_fim_str:
        return jsonify({"erro": "Os parâmetros 'data_inicio' e 'data_fim' são obrigatórios"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT barbeiros.id AS barbeiro_id, barbeiros.nome AS barbeiro_nome,
               COUNT(DISTINCT cortes.id) AS quantidade_atendimentos,
               COALESCE(SUM(tipos_corte.valor), 0) AS faturamento_total
        FROM cortes
        JOIN barbeiros ON cortes.barbeiro_id = barbeiros.id
        JOIN corte_itens ON corte_itens.corte_id = cortes.id
        JOIN tipos_corte ON corte_itens.tipo_corte_id = tipos_corte.id
        WHERE cortes.data BETWEEN ? AND ?
        GROUP BY barbeiros.id
    """, (data_inicio_str, data_fim_str))

    resultado = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({
        "periodo": {"inicio": data_inicio_str, "fim": data_fim_str},
        "barbeiros": resultado
    }), 200


@relatorios_bp.route("/ranking", methods=["GET"])
def ranking_barbeiros():
    """
    Ranking de barbeiros por faturamento total
    ---
    tags:
      - Relatórios
    responses:
      200:
        description: Lista de barbeiros ordenada por faturamento, do maior para o menor
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT barbeiros.id AS barbeiro_id, barbeiros.nome AS barbeiro_nome,
               COUNT(DISTINCT cortes.id) AS quantidade_atendimentos,
               COALESCE(SUM(tipos_corte.valor), 0) AS faturamento_total
        FROM cortes
        JOIN barbeiros ON cortes.barbeiro_id = barbeiros.id
        JOIN corte_itens ON corte_itens.corte_id = cortes.id
        JOIN tipos_corte ON corte_itens.tipo_corte_id = tipos_corte.id
        GROUP BY barbeiros.id
        ORDER BY faturamento_total DESC
    """)

    ranking = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(ranking), 200