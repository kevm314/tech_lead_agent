import concurrent
import logging
import random
from pathlib import Path
from typing import Any, List, Optional, Type, Union

from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader
from langchain.document_loaders.html_bs import BSHTMLLoader
from langchain.document_loaders.text import TextLoader
from langchain.document_loaders.unstructured import UnstructuredFileLoader

FILE_LOADER_TYPE = Union[
    Type[UnstructuredFileLoader], Type[TextLoader], Type[BSHTMLLoader]
]
logger = logging.getLogger(__name__)


def _is_visible(p: Path) -> bool:
    parts = p.parts
    for _p in parts:
        if _p.startswith("."):
            return False
    return True


class FileListLoader(BaseLoader):
    """Load from a directory."""

    def __init__(
        self,
        filelist: List[Path],
        silent_errors: bool = False,
        loader_cls: FILE_LOADER_TYPE = UnstructuredFileLoader,
        loader_kwargs: Union[dict, None] = None,
        show_progress: bool = False,
        use_multithreading: bool = False,
        max_concurrency: int = 4,
        *,
        sample_size: int = 0,
        randomize_sample: bool = False,
        sample_seed: Union[int, None] = None,
    ):
        """Initialize with a path to directory and how to glob over it.

        Args:
            filelist: List of paths to files to include
            silent_errors: Whether to silently ignore errors. Defaults to False.
            loader_cls: Loader class to use for loading files.
              Defaults to UnstructuredFileLoader.
            loader_kwargs: Keyword arguments to pass to loader_cls. Defaults to None.
            show_progress: Whether to show a progress bar. Defaults to False.
            use_multithreading: Whether to use multithreading. Defaults to False.
            max_concurrency: The maximum number of threads to use. Defaults to 4.
            sample_size: The maximum number of files you would like to load from the
                directory.
            randomize_sample: Suffle the files to get a random sample.
            sample_seed: set the seed of the random shuffle for reporoducibility.
        """
        if loader_kwargs is None:
            loader_kwargs = {}
        self.filelist = filelist
        self.loader_cls = loader_cls
        self.loader_kwargs = loader_kwargs
        self.silent_errors = silent_errors
        self.show_progress = show_progress
        self.use_multithreading = use_multithreading
        self.max_concurrency = max_concurrency
        self.sample_size = sample_size
        self.randomize_sample = randomize_sample
        self.sample_seed = sample_seed

    def load_file(
        self, item: Path, docs: List[Document], pbar: Optional[Any]
    ) -> None:
        """Load a file.

        Args:
            item: File path.
            docs: List of documents to append to.
            pbar: Progress bar. Defaults to None.

        """
        if item.is_file():
            try:
                logger.debug(f"Processing file: {str(item)}")
                sub_docs = self.loader_cls(str(item), **self.loader_kwargs).load()
                docs.extend(sub_docs)
            except Exception as e:
                if self.silent_errors:
                    logger.warning(f"Error loading file {str(item)}: {e}")
                else:
                    raise e
            finally:
                if pbar:
                    pbar.update(1)

    def load(self) -> List[Document]:
        """Load documents."""
        items = self.filelist

        docs: List[Document] = []

        if self.sample_size > 0:
            if self.randomize_sample:
                randomizer = (
                    random.Random(self.sample_seed) if self.sample_seed else random
                )
                randomizer.shuffle(items)  # type: ignore
            items = items[: min(len(items), self.sample_size)]

        pbar = None
        if self.show_progress:
            try:
                from tqdm import tqdm

                pbar = tqdm(total=len(items))
            except ImportError as e:
                logger.warning(
                    "To log the progress of DirectoryLoader you need to install tqdm, "
                    "`pip install tqdm`"
                )
                if self.silent_errors:
                    logger.warning(e)
                else:
                    raise ImportError(
                        "To log the progress of DirectoryLoader "
                        "you need to install tqdm, "
                        "`pip install tqdm`"
                    )

        if self.use_multithreading:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.max_concurrency
            ) as executor:
                executor.map(lambda i: self.load_file(i, docs, pbar), items)
        else:
            for i in items:
                self.load_file(i, docs, pbar)

        if pbar:
            pbar.close()

        return docs
