import os
from typing import List

from git import Repo
from langchain.agents import load_tools, initialize_agent, AgentType
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain.llms.openai import OpenAI
from langchain.text_splitter import CharacterTextSplitter, Language, RecursiveCharacterTextSplitter
from langchain.tools import Tool, StructuredTool
from langchain.vectorstores.chroma import Chroma

import RepoLoader
from document_loaders.FileListLoader import FileListLoader
from prompts import request_prompt_template
from tools import create_ticket
from utils import list_files


class AgentSmith:
    def __init__(self):
        print("Launching Agent!")

        self.react = None
        self.doc_searches = []

        model_name = "BAAI/bge-small-en"
        model_kwargs = {'device': 'cpu'}
        encode_kwargs = {'normalize_embeddings': True}
        self.embeddings = HuggingFaceBgeEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )

        self.text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

        self.llm = OpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")  # # gpt-3.5-turbo

        self.tools = load_tools(["llm-math"], llm=self.llm)

        ticket_tool = StructuredTool.from_function(create_ticket)

        self.tools.append(
            ticket_tool
        )

    def add_git_repo_as_vector_store(self, repo_name, local_dir=None):
        # repo_name = extract_repo_name(git_url)
        if local_dir is None:
            local_dir = f'temp/{repo_name}'
        git_url = f'https://github.com/{repo_name}.git'

        os.makedirs(local_dir, exist_ok=True)

        print(f"Cloning {git_url} into {local_dir}")
        repo = Repo.clone_from(git_url, local_dir)

        self.add_vector_store(local_dir, repo_name)

        return repo

    def add_vector_store(self, repo_dir, repo_name):
        print(f"Adding Vector Directory: {repo_dir}")

        split_text: List[Document] = []
        excluded_file_extensions = []

        for language in Language:
            accepted_file_extensions = RepoLoader.code_map[language.value]
            excluded_file_extensions += accepted_file_extensions

            files = list_files(repo_dir, include_extensions=accepted_file_extensions)

            d_loader = FileListLoader(
                files,
                show_progress=True,
                use_multithreading=False,
                loader_cls=TextLoader,
                silent_errors=True
            )

            docs = d_loader.load()

            text_splitter = RecursiveCharacterTextSplitter.from_language(
                chunk_size=1000,
                chunk_overlap=100,
                language=language
            )

            texts = text_splitter.split_documents(docs)
            split_text += texts

        # Add non-code files

        if False:
            files = list_files(repo_dir, ignore_extensions=excluded_file_extensions)
            d_loader = FileListLoader(files,
                                       show_progress=True, use_multithreading=False, loader_cls=TextLoader,
                                       silent_errors=True)

            docs = d_loader.load()

            frontend_texts = self.text_splitter.split_documents(docs)
            split_text += frontend_texts

        doc_search = Chroma.from_documents(split_text, self.embeddings, collection_name=repo_name.split('/')[0])

        self.doc_searches.append(doc_search)

        repo = RetrievalQAWithSourcesChain.from_chain_type(
            llm=self.llm, chain_type="stuff", retriever=doc_search.as_retriever(search_kwargs={'k': 26})
        )

        vector_store_tool = Tool(
            name=f"{repo_name} repository",
            func=repo.__call__,
            description=f"Useful for when you need to answer questions about code files within the {repo_name} repo. Input should be a fully formed question about what code files to search. repo_name={repo_name}",
        )

        self.tools.append(vector_store_tool)

    def init_agent(self):
        self.react = initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )

    def run(self, feature_request):
        prompt: str = request_prompt_template.format(feature_request)

        if self.react is None:
            raise Exception("Cannot run on prompt. Make sure you've setup the agent first!")
        self.react.run(
            prompt
        )


