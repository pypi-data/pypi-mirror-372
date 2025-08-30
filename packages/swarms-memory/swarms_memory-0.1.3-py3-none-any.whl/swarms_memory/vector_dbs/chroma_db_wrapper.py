import os
import uuid
from typing import Optional

import chromadb
from dotenv import load_dotenv
from loguru import logger
from swarms_memory.vector_dbs.base_vectordb import BaseVectorDatabase
from swarms.utils.data_to_text import data_to_text

# Load environment variables
load_dotenv()


# Results storage using local ChromaDB
class ChromaDB(BaseVectorDatabase):
    """

    ChromaDB database

    Args:
        metric (str): The similarity metric to use.
        output (str): The name of the collection to store the results in.
        limit_tokens (int, optional): The maximum number of tokens to use for the query. Defaults to 1000.
        n_results (int, optional): The number of results to retrieve. Defaults to 2.

    Methods:
        add: _description_
        query: _description_

    Examples:
        >>> chromadb = ChromaDB(
        >>>     metric="cosine",
        >>>     output="results",
        >>>     llm="gpt3",
        >>>     openai_api_key=OPENAI_API_KEY,
        >>> )
        >>> chromadb.add(task, result, result_id)
    """

    def __init__(
        self,
        metric: str = "cosine",
        output_dir: str = "swarms",
        limit_tokens: Optional[int] = 1000,
        n_results: int = 1,
        docs_folder: str = None,
        verbose: bool = False,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.metric = metric
        self.output_dir = output_dir
        self.limit_tokens = limit_tokens
        self.n_results = n_results
        self.docs_folder = docs_folder
        self.verbose = verbose

        # Create Chroma collection
        chroma_persist_dir = "chroma"
        chroma_client = chromadb.PersistentClient(
            settings=chromadb.config.Settings(
                persist_directory=chroma_persist_dir,
            ),
            *args,
            **kwargs,
        )

        # Create ChromaDB client
        self.client = chromadb.Client()

        # Create Chroma collection
        self.collection = chroma_client.get_or_create_collection(
            name=output_dir,
            metadata={"hnsw:space": metric},
            *args,
            **kwargs,
        )
        logger.info(
            "ChromaDB collection created:"
            f" {self.collection.name} with metric: {self.metric} and"
            f" output directory: {self.output_dir}"
        )

        # If docs
        if docs_folder:
            logger.info(f"Traversing directory: {docs_folder}")
            self.traverse_directory()

    def add(
        self,
        document: str,
        *args,
        **kwargs,
    ):
        """
        Add a document to the ChromaDB collection.

        Args:
            document (str): The document to be added.
            condition (bool, optional): The condition to check before adding the document. Defaults to True.

        Returns:
            str: The ID of the added document.
        """
        try:
            doc_id = str(uuid.uuid4())
            self.collection.add(
                ids=[doc_id],
                documents=[document],
                *args,
                **kwargs,
            )
            print("-----------------")
            print("Document added successfully")
            print("-----------------")
            return doc_id
        except Exception as e:
            raise Exception(f"Failed to add document: {str(e)}")

    def query(
        self,
        query_text: str,
        *args,
        **kwargs,
    ) -> str:
        """
        Query documents from the ChromaDB collection.

        Args:
            query (str): The query string.
            n_docs (int, optional): The number of documents to retrieve. Defaults to 1.

        Returns:
            dict: The retrieved documents.
        """
        try:
            logger.info(f"Querying documents for: {query_text}")
            docs = self.collection.query(
                query_texts=[query_text],
                n_results=self.n_results,
                *args,
                **kwargs,
            )["documents"]

            # Convert into a string
            out = ""
            for doc in docs:
                out += f"{doc}\n"

            # Display the retrieved document
            logger.info(f"Query: {query_text}")
            logger.info(f"Retrieved Document: {out}")
            return out

        except Exception as e:
            raise Exception(f"Failed to query documents: {str(e)}")

    def traverse_directory(
        self, docs_folder: str = None, *args, **kwargs
    ):
        """
        Traverse through every file in the given directory and its subdirectories,
        and return the paths of all files.
        Parameters:
        - directory_name (str): The name of the directory to traverse.
        Returns:
        - list: A list of paths to each file in the directory and its subdirectories.
        """
        try:
            logger.info(f"Traversing directory: {self.docs_folder}")
            added_to_db = False
            allowed_extensions = [
                "txt",
                "pdf",
                "docx",
                "doc",
                "md",
                "yaml",
                "json",
                "csv",
                "tsv",
                "xls",
                "xlsx",
                "xml",
                "yml",
            ]

            for root, dirs, files in os.walk(self.docs_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    _, ext = os.path.splitext(file_path)
                    if ext.lower() in allowed_extensions:
                        data = data_to_text(file_path)
                        added_to_db = self.add(str(data))
                        print(f"{file_path} added to Database")
                    else:
                        print(
                            f"Skipped {file_path} due to unsupported file extension"
                        )

            return added_to_db

        except Exception as error:
            logger.error(
                f"Failed to traverse directory: {str(error)}"
            )
            raise error
