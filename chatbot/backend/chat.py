import os
from langchain.document_loaders import Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationSummaryMemory
from langchain.chains import ConversationalRetrievalChain
from dotenv import load_dotenv

load_dotenv()

def main():
    print("Carregando o documento")
    loader = Docx2txtLoader("./Matheus Tanaka - React Native.docx")
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
    response = qa("O que você achou deste currículo")
    print("Resposta do QA:", response)


main()

