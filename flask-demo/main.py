from flask import Flask, request, jsonify

app = Flask(__name__)

# Array para armazenar os usuários. OBS: Isso não é um banco de dados de verdade.
banco_de_dados = []

@app.route('/adicionar_usuario', methods=['POST'])
def adicionar_usuario():
    data = request.get_json()
    usuario = data.get('usuario', '')

    # Validando a entrada que será enviada pelo Postman
    if not usuario:
        return jsonify({"erro": "Por favor, insira um usuário válido!"}), 400
    # Adicionando o usuário no banco de dados (array)
    banco_de_dados.append(usuario)
    
    return jsonify({"mensagem": "Usuário adicionado com sucesso!"}), 200


@app.route('/listar_usuarios', methods=['GET'])
def listar_usuarios():
    # Loop através do array para criar uma lista de usuários
    lista = [usuario for usuario in banco_de_dados]

    return jsonify({"usuario": lista}), 200


@app.route('/buscar_usuario/<usuario>', methods=['GET'])
def buscar_usuario(usuario):

    if usuario in banco_de_dados:
        return jsonify({"usuario": usuario}), 200
    else:
        return jsonify({"erro": "Usuário não encontrado!"}), 404


@app.route('/deletar_usuario/<usuario>', methods=['DELETE'])
def deletar_usuario(usuario):
    if usuario in banco_de_dados:
        # Removendo o usuário do banco de dados
        banco_de_dados.remove(usuario)

        return jsonify({"mensagem": "Usuário deletado com sucesso!"}), 200

    else:
        return jsonify({"erro": "Usuário não encontrado!"}), 404

if __name__ == '__main__':
    app.run(debug=True)

