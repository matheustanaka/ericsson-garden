import os
from flask import Flask, flash, request, jsonify, redirect, render_template
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
# Langchain imports
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import Docx2txtLoader
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain.agents.agent_types import AgentType
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
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'csv' }

file_uploaded = None

def allowed_file(filename): 
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploader', methods = ['POST'])
@cross_origin()
def upload_file():
    global file_uploaded

    file = request.files['file']

    if file and allowed_file(file.filename):
        print('file request', file)
        filename = secure_filename(file.filename)
        print('nome do arquivo', filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Juntando o caminho do diretório com o nome do arquivo
        file_save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file_uploaded = file_save_path

        if os.path.exists(file_uploaded):
            print('pasta do arquivo: ', app.config['UPLOAD_FOLDER'])
            return jsonify({ 'message': 'File uploaded successfully', 'filename': filename}), 200
        else: 
            return jsonify({ 'error': 'File not found'}), 404
    else:
        return jsonify({ 'error': 'File not allowed'}), 400


def process_document(data, ask, api_key):
    print('Separando o documento em pedaços...')
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=150)

    all_splits = text_splitter.split_documents(data)
    print('Documentos separados: \n', all_splits)

    print('Salvando os documentos no vetor...')
    vectorstore = Chroma.from_documents(documents=all_splits, embedding=OpenAIEmbeddings())

    print('Configurando o chatbot...')
    llm = ChatOpenAI(openai_api_key=api_key, model_name='gpt-3.5-turbo-0613', temperature=0.7)
    memory = ConversationSummaryMemory(llm=llm, memory_key='chat_history', return_messages=True)
    retriever = vectorstore.as_retriever()

    print('[PERGUNTA]: ', ask)
    qa = ConversationalRetrievalChain.from_llm(llm, retriever=retriever, memory=memory)
    response = qa(ask)

    answer = response.get('answer', 'No answer found')

    print('[RESPOSTA]: \n', answer)

    response_json = jsonify({ 'answer': answer }), 200 
 
    return response_json 


def process_csv(filename, ask, api_key): 

    print('Carregando documento csv...')

    agent = create_csv_agent(
        ChatOpenAI(temperature=0, model='gpt-3.5-turbo-0613', openai_api_key=api_key),
        filename,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
    )

    print('[PERGUNTA]: ', ask)
    response = agent.run(ask)
    answer = response
    print('[RESPOSTA]: \n', answer)

    response_json = jsonify({ 'answer': answer }), 200 
 
    return response_json 


def check_file_extension(filename, ask):
    api_key = os.getenv('OPENAI_API_KEY')
    extension = filename.rsplit('.', 1)[1].lower()

    match extension:
        case 'csv':
            print('Carregando documento CSV...')

            return process_csv(filename, ask, api_key)
        case 'docx' | 'pdf':
            if extension == 'docx':
                print('Carregando documento DOCX...')

                loader = Docx2txtLoader(filename)
                data = loader.load()

            else:
                print('Carregando documento PDF...')

                loader = PyPDFLoader(filename, extract_images=False)
                data = loader.load()

            return process_document(data, ask, api_key) 

        case _:
            raise ValueError(f'Tipo de arquivo não suportado: {extension}')



@app.route('/chatbot', methods = ['POST'])
@cross_origin()
def send_message():
    data_question = request.data
    ask = data_question.decode('utf-8')

    return check_file_extension(filename=file_uploaded, ask=ask)    

if __name__ == '__main__':
    app.run(debug=True)
