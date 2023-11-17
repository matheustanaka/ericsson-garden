# from langchain.document_loaders import TextLoader
from langchain.document_loaders import Docx2txtLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.callbacks import get_openai_callback
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
import os
from dotenv import load_dotenv

load_dotenv()


def main():
    loader = Docx2txtLoader("./Matheus Tanaka - React Native.docx")
    data = loader.load()

    print(data)

    text_splitter_summary = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=100, chunk_overlap=0)

    docs_summary = text_splitter_summary.split_documents(data)

    print(docs_summary)

    summary_template = "Você é um analista de Recursos Humanos de uma startup de tecnologia, seu trabalho é analisar currículos de candidatos a vaga de progamador mobile. Abaixo você encontra os dados de um currículo {text}. Analise o currículo enviado e dê sugestões sobre o que pode ser melhorado no currículo"

    PROMPT_SUMMARY = PromptTemplate(template=summary_template, input_variables=["text"])

    summary_refine_template = """
    Você é um analista de Recursos Humanos de uma startup de tecnologia, cuja tarefa é avaliar currículos de candidatos à vaga de programador mobile. Abaixo, você encontra os dados de um currículo: {text}. 

    Por favor, faça uma análise detalhada do currículo com base nos seguintes critérios:
    1. Experiência Profissional: Avalie a relevância e a profundidade das experiências profissionais listadas. 
    2. Habilidades Técnicas: Analise as habilidades técnicas apresentadas e como elas se alinham com os requisitos para um programador mobile.
    3. Educação e Qualificações: Considere a adequação da formação educacional e quaisquer outras qualificações.
    4. Apresentação e Clareza: Avalie a clareza, organização e profissionalismo da apresentação do currículo.

    Com base em sua análise, ofereça sugestões construtivas sobre o que pode ser melhorado no currículo para torná-lo mais atraente para a posição de programador mobile.
    """
    PROMPT_SUMMARY_REFINE = PromptTemplate(input_variables=["existing_answer", "text"], template=summary_refine_template,)

    open_api_key = os.getenv('OPENAI_API_KEY')

    llm_summary = ChatOpenAI(open_api_key=open_api_key, model_name='gpt-4', temperature=1.0)

    summarize_chain = load_summarize_chain(llm=llm_summary, chain_type="refine", verbose=True, question_prompt=PROMPT_SUMMARY, refine_prompt=PROMPT_SUMMARY_REFINE)

    summaries = []
    for doc in docs_summary:
        summary = summarize_chain.run(summaries[doc])  # Process each doc individually
        print(summary)
        summaries.append(summary)
    
    # Join all summaries into a single string
    full_summary = "\n".join(summaries)


    # Write summary to file
    with open("summary.txt", "w") as f:
        f.write(full_summary)

    # Create the LLM model for the question answering
    llm_question_answer = ChatOpenAI(openai_api_key=openai_api_key, temperature=0.2, model="gpt-4")

    # Create the vector database and RetrievalQA Chain
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    db = FAISS.from_documents(docs_qa, embeddings)
    qa = RetrievalQA.from_chain_type(llm=llm_question_answer, chain_type="stuff", retriever=db.as_retriever())


    question = ""
    # Run the QA chain continuously
    while question != "exit":
        # Get the user question
        question = input("Ask a question or enter exit to close the app: ")
        # Run the QA chain
        answer = qa.run(question)
        print("---------------------------------")
        print("\n")

main()
