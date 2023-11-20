import os
from flask import Flask, flash, request, jsonify, redirect, render_template
from werkzeug.utils import secure_filename
# Langchain imports
from langchain.document_loaders import Docx2txtLoader
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

app = Flask(__name__, template_folder='template')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

file_uploaded = None

@app.route('/upload')
def upload():
   return render_template('upload.html')

@app.route("/uploader", methods = ['POST'])
def upload_file():
    global file_uploaded
    file = request.files['file']
    print("file request", file)
    filename = secure_filename(file.filename)
    print("nome do arquivo", filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # Juntando o caminho do diretório com o nome do arquivo
    file_save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file_uploaded = file_save_path

    if os.path.exists(file_save_path):
        print("pasta do arquivo", app.config['UPLOAD_FOLDER'])
        return jsonify({ "message": "File uploaded successfully", "filename": filename})
    else: 
        return jsonify({ "error": "File not found"})


@app.route("/chatbot", methods = ['GET', 'POST'])
def send_message():
    if request.method == 'POST':
        data = request.data # Ignora o tipo do conteudo
        ask = data.decode('utf-8')

        print("Carregando o documento")
        loader = Docx2txtLoader(file_uploaded)
        data = loader.load()

        api_key = os.getenv('OPENAI_API_KEY')

        print("Separando o documento em pedaços")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)

        all_splits = text_splitter.split_documents(data)

        print("Salvando os documentos no vetor")
        vectorstore = Chroma.from_documents(documents=all_splits, embedding=OpenAIEmbeddings())

        print("Configurando o chatbot")
        llm = ChatOpenAI(openai_api_key=api_key, model_name='gpt-4', temperature=1.0)
        memory = ConversationSummaryMemory(llm=llm, memory_key="chat_history", return_messages=True)
        retriever = vectorstore.as_retriever()

        print("Realizando a pergunta")
        qa = ConversationalRetrievalChain.from_llm(llm, retriever=retriever, memory=memory)
        response = qa(ask)

        # Converte o objeto SystemMessage para string
        response['chat_history'] = [str(msg) for msg in response['chat_history']]
        print("Resposta do QA:", response) 

        # Converte toda a resposta em objeto para JSON
        return json.dumps(response)

if __name__ == "__main__":
    app.run(debug=True)
