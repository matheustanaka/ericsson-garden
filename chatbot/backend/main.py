import os
from flask import Flask, flash, request, jsonify, redirect, render_template
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
# Langchain imports
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import Docx2txtLoader
from langchain.document_loaders import UnstructuredExcelLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationSummaryMemory
from langchain.chains import ConversationalRetrievalChain
from dotenv import load_dotenv
import json

load_dotenv()


UPLOAD_FOLDER = './upload/'

os.makedirs(os.path.dirname(UPLOAD_FOLDER), exist_ok=True)

app = Flask(__name__)
cors = CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'xlsx' }

file_uploaded = None

def allowed_file(filename): 
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/uploader", methods = ['POST'])
@cross_origin()
def upload_file():
    global file_uploaded

    file = request.files['file']

    if file and allowed_file(file.filename):
        print("file request", file)
        filename = secure_filename(file.filename)
        print("nome do arquivo", filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Juntando o caminho do diretório com o nome do arquivo
        file_save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file_uploaded = file_save_path
        print("Vendo o tipo do arquivo", file.filename)

        if os.path.exists(file_uploaded):
            print("pasta do arquivo", app.config['UPLOAD_FOLDER'])
            return jsonify({ "message": "File uploaded successfully", "filename": filename}), 200
        else: 
            return jsonify({ "error": "File not found"}), 404
    else:
        return jsonify({ "error": "File not allowed"}), 400


def load_document(filename):
    extension = filename.rsplit('.', 1)[1].lower()

    match extension:
        case 'docx':
            loader = Docx2txtLoader(filename)
            print("Carregando documento docx...")
        case 'pdf':
            loader = PyPDFLoader(filename, extract_images=True)
            print("Carregando documento PDF...")
        case _:
            raise ValueError(f"Tipo de arquivo não suportado: {extension}")

    return loader.load()


@app.route("/chatbot", methods = ['POST'])
@cross_origin()
def send_message():
    data_question = request.data # Ignora o tipo do conteudo
    ask = data_question.decode('utf-8')

    print("Carregando o documento")
    document_data = load_document(file_uploaded)

    api_key = os.getenv('OPENAI_API_KEY')

    print("Separando o documento em pedaços")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=150)

    all_splits = text_splitter.split_documents(document_data)
    print("Documentos quebrados", all_splits)

    print("Salvando os documentos no vetor")
    vectorstore = Chroma.from_documents(documents=all_splits, embedding=OpenAIEmbeddings())

    print("Configurando o chatbot")
    llm = ChatOpenAI(openai_api_key=api_key, model_name='gpt-4', temperature=0.7)
    memory = ConversationSummaryMemory(llm=llm, memory_key="chat_history", return_messages=True)
    retriever = vectorstore.as_retriever()

    print("Realizando a pergunta")
    qa = ConversationalRetrievalChain.from_llm(llm, retriever=retriever, memory=memory)
    response = qa(ask)

    answer = response.get('answer', 'No answer found')

    print("Resposta do chatgpt:", answer)

    return jsonify({ "answer": answer }), 200 

if __name__ == "__main__":
    app.run(debug=True)
