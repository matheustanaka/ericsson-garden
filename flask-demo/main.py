from flask import Flask, request, jsonify

app = Flask(__name__)

# Array para armazenar as palavras
palavras = []

@app.route('/adicionar_palavra', methods=['POST'])
def adicionar_palavra():
    data = request.get_json()
    palavra = data.get('palavra', '').strip()

    # Validando a entrada
    if not palavra:
        return jsonify({"erro": "Por favor, insira uma palavra válida!"}), 400

    palavras.append(palavra)

    return jsonify({"mensagem": "Palavra adicionada com sucesso!"}), 200

@app.route('/listar_palavras', methods=['GET'])
def listar_palavras():
    # Loop através do array para criar uma lista de palavras
    lista = [palavra for palavra in palavras]

    return jsonify({"palavras": lista}), 200

if __name__ == '__main__':
    app.run(debug=True)

