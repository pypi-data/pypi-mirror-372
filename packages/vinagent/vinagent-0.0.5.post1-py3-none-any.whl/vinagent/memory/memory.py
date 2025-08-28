from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Literal, Union
import json
import logging
from aucodb.graph import LLMGraphTransformer
from langchain_together import ChatTogether
from langchain_core.language_models.base import BaseLanguageModel
from langchain_openai.chat_models.base import BaseChatOpenAI

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryMeta(ABC):
    """
    Abstract base class defining the interface for memory operations in an AI agent.
    """

    @abstractmethod
    def update_memory(self, graph: list, user_id: str = "unknown_user"):
        """
        Update the memory with a new graph for a specific user.

        Args:
            graph (list): List of graph entries to update the memory.
            user_id (str, optional): The user identifier. Defaults to "unknown_user".
        """
        pass

    @abstractmethod
    def save_short_term_memory(
        self,
        llm: Union[ChatTogether, BaseLanguageModel, BaseChatOpenAI],
        message: str,
        user_id: str = "unknown_user",
        *args,
        **kwargs,
    ):
        """
        Convert a message to a graph and save it to memory.

        Args:
            llm (Union[ChatTogether, BaseLanguageModel, BaseChatOpenAI]): Language model for graph generation.
            message (str): The message to convert and store.
            user_id (str, optional): The user identifier. Defaults to "unknown_user".
            *args, **kwargs: Additional arguments for flexibility.
        """
        pass

    @abstractmethod
    def save_memory(
        self,
        obj: list,
        memory_path: Path,
        user_id: str = "unknown_user",
        *args,
        **kwargs,
    ):
        """
        Save a list of memory entries to the memory file for a specific user.

        Args:
            obj (list): List of memory entries to save.
            memory_path (Path): Path to the memory file.
            user_id (str, optional): The user identifier. Defaults to "unknown_user".
            *args, **kwargs: Additional arguments for flexibility.
        """
        pass


class Memory(MemoryMeta):
    """
    Concrete implementation of MemoryMeta for storing and managing conversational memory.
    Memory is persisted in a JSON Lines file, with support for user-specific data and graph-based representations.
    """

    def __init__(
        self,
        memory_path: Optional[Union[Path, str]] = Path("templates/memory.jsonl"),
        is_reset_memory: bool = False,
        is_logging: bool = False,
        *args,
        **kwargs,
    ):
        """
        Initialize the Memory instance.

        Args:
            memory_path (Optional[Union[Path, str]], optional): Path to the JSON Lines file for memory storage.
                Defaults to Path("templates/memory.jsonl").
            is_reset_memory (bool, optional): If True, resets the memory file to an empty JSON object. Defaults to False.
            is_logging (bool, optional): If True, enables logging of memory operations. Defaults to False.
            *args, **kwargs: Additional arguments for future extensions.

        Behavior:
            - Converts memory_path to a Path object if provided as a string.
            - Creates the parent directory for memory_path if it does not exist.
            - Initializes an empty JSON file if it does not exist.
            - Resets the memory file if is_reset_memory is True.
        """
        if isinstance(memory_path, str) and memory_path:
            self.memory_path = Path(memory_path)
        else:
            self.memory_path = memory_path
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        self.is_reset_memory = is_reset_memory
        self.is_logging = is_logging
        if not self.memory_path.exists():
            self.memory_path.write_text(json.dumps({}, indent=4), encoding="utf-8")
        if self.is_reset_memory:
            self.memory_path.write_text(json.dumps({}, indent=4), encoding="utf-8")

    def load_memory_by_user(
        self,
        load_type: Literal["list", "string"] = "list",
        user_id: str = "unknown_user",
    ):
        """
        Load memory data for a specific user from the memory file.

        Args:
            load_type (Literal["list", "string"], optional): Format of the returned data ("list" or "string").
                Defaults to "list".
            user_id (str, optional): The user identifier. Defaults to "unknown_user".

        Returns:
            Union[List[dict], str]: List of memory entries if load_type is "list", or a string representation if "string".
        """
        data = self.load_all_memory()
        data_user = []
        if user_id in data:
            data_user = data[user_id]

        if load_type == "list":
            return data_user
        elif load_type == "string":
            message = self.revert_object_mess(data_user)
            return message

    def load_all_memory(self):
        """
        Load all memory data from the memory file.

        Returns:
            dict: The entire memory data as a dictionary, with user IDs as keys and lists of memory entries as values.
        """
        with open(self.memory_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    def save_memory(self, obj: list, memory_path: Path, user_id: str = "unknown_user"):
        """
        Save a list of memory entries for a specific user to the memory file.

        Args:
            obj (list): List of memory entries to save.
            memory_path (Path): Path to the memory file.
            user_id (str, optional): The user identifier. Defaults to "unknown_user".
        """
        memory = self.load_all_memory()
        memory[user_id] = obj
        with open(memory_path, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=4, ensure_ascii=False)

        if self.is_logging:
            logger.info(f"Saved memory!")

    def save_short_term_memory(
        self,
        llm: Union[ChatTogether, BaseLanguageModel, BaseChatOpenAI],
        message: str,
        user_id: str = "unknown_user",
        *args,
        **kwargs,
    ):
        """
        Convert a message to a graph using a language model and update the user's memory.

        Args:
            llm (Union[ChatTogether, BaseLanguageModel, BaseChatOpenAI]): Language model for graph generation.
            message (str): The message to convert and store.
            user_id (str, optional): The user identifier. Defaults to "unknown_user".
            *args, **kwargs: Additional arguments for flexibility.

        Returns:
            list: The generated graph representation of the message.
        """
        graph_transformer = LLMGraphTransformer(llm=llm)
        graph = graph_transformer.generate_graph(message)
        self.update_memory(user_id=user_id, graph=graph)
        return graph

    def revert_object_mess(self, object: list[dict]):
        """
        Convert a list of memory entries into a human-readable string format.

        Args:
            object (list[dict]): List of memory entries, each containing head, relation, relation_properties, and tail.

        Returns:
            str: String representation of memory entries in the format "head -> relation[relation_properties] -> tail".
        """
        mess = []
        for line in object:
            head, _, relation, relation_properties, tail, _ = list(line.values())
            relation_additional = (
                f"[{relation_properties}]" if relation_properties else ""
            )
            mess.append(f"{head} -> {relation}{relation_additional} -> {tail}")
        mess = "\n".join(mess)
        return mess

    def update_memory(self, graph: list, user_id: str = "unknown_user"):
        """
        Update the user's memory by adding or updating graph entries, avoiding duplicates.

        Args:
            graph (list): List of graph entries, each with head, head_type, relation, relation_properties, tail, and tail_type.
            user_id (str, optional): The user identifier. Defaults to "unknown_user".

        Returns:
            list: The updated list of memory entries for the user.
        """
        memory_about_user = self.load_memory_by_user(load_type="list", user_id=user_id)
        if memory_about_user:
            index_memory = [
                (item["head"], item["relation"], item["tail"])
                for item in memory_about_user
            ]
            index_memory_head_relation_tail_type = [
                (item["head"], item["relation"], item["tail_type"])
                for item in memory_about_user
            ]
        else:
            index_memory = []
            index_memory_head_relation_tail_type = []

        if graph:
            for line in graph:
                head, head_type, relation, relation_properties, tail, tail_type = list(
                    line.values()
                )
                lookup_hrt = (head, relation, tail)
                lookup_hrttp = (head, relation, tail_type)
                if lookup_hrt in index_memory:
                    if self.is_logging:
                        logger.info(f"Bypass {line}")
                    pass
                elif lookup_hrttp in index_memory_head_relation_tail_type:
                    index_match = index_memory_head_relation_tail_type.index(
                        lookup_hrttp
                    )
                    if self.is_logging:
                        logger.info(
                            f"Update new line: {line}\nfrom old line {memory_about_user[index_match]}"
                        )
                    memory_about_user[index_match] = line
                else:
                    if self.is_logging:
                        logger.info(f"Insert new line: {line}")
                    memory_about_user.append(line)
        else:
            if self.is_logging:
                logger.info(f"No thing updated")

        self.save_memory(
            obj=memory_about_user, memory_path=self.memory_path, user_id=user_id
        )
        return memory_about_user
