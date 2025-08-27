import os
import logging
import pandas as pd
import tempfile as tmp
from typing import Optional
from fastapi.responses import HTMLResponse
from wattleflow.core import IProcessor, IRepository, ITarget, T
from wattleflow.concrete import (
    AuditLogger,
    DocumentFacade,
    GenericBlackboard,
    GenericRepository,
    GenericPipeline,
    StrategyCreate,
    StrategyRead,
    StrategyWrite,
)
from wattleflow.constants import Event
from wattleflow.documents import DataFrameDocument
from wattleflow.helpers import TextFileStream
from wattleflow.helpers.casetext import CaseText
from wattleflow.processors import YoutubeTranscriptProcessor


class RepositoryReadDocument(StrategyRead):
    def get_filepath(self, storage_path: str, name: str, ext: str) -> str:
        name_pattern = "{path}{sep}{name:lower}.{ext:lower}"
        return name_pattern.format(
            path=CaseText(storage_path),
            sep=os.path.sep,
            name=CaseText(name),
            ext=CaseText(ext),
        )

    def execute(
        self, caller: IRepository, item: ITarget, **kwargs
    ) -> Optional[ITarget]:
        self.debug(
            msg=Event.ProcessingTask.value,
            id=item.identifier,
            caller=caller.name,
            kwargs=kwargs,
        )

        return item

        repository_path = getattr(caller, "repository_path", "")
        filename = getattr(item, "filename", "")
        file_path = self.get_filepath(repository_path, filename, "csv")
        self.debug(f"repository_path: {repository_path}, file_path: {file_path}")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        content: pd.DataFrame = pd.read_csv(file_path)
        self.debug(msg=f"columns: {content.columns}")
        # content["text"] = content["text"].apply(lambda s: s.replace("\n", " "))

        document = DocumentFacade(DataFrameDocument(item))
        document.update_content(content)

        self.info(
            msg=Event.Created.value,
            id=document.identifier,
            size=len(content),
        )

        return document


class RepositoryStoreDataframeDocument(StrategyWrite):
    def get_filepath(self, storage_path: str, name: str, ext: str) -> str:
        name_pattern = "{path}{sep}{name:lower}.{ext:lower}"
        return name_pattern.format(
            path=CaseText(storage_path),
            sep=os.path.sep,
            name=CaseText(name),
            ext=CaseText(ext),
        )

    def execute(self, pipeline, repository, item, **kwargs) -> bool:
        self.mandatory(name="processor", cls=IProcessor, **kwargs)
        pipe_name = pipeline.name.lower()
        filename = getattr(item, "filename", item.identifier)

        dataframe: pd.DataFrame = item.request()
        self.evaluate(dataframe, pd.DataFrame)

        self.debug(
            msg=Event.ProcessingTask.value,
            pipe_name=pipe_name,
            filename=filename,
            repository=repository.name,
        )

        if dataframe.empty:
            self.warning(
                msg=Event.ProcessingTask.value,
                id=item.identifier,
                size=len(dataframe),
            )
            return False

        file_path = self.get_filepath(
            repository.repository_path, item.identifier, "csv"
        )
        if not os.path.exists(repository.repository_path):
            self.debug(msg="creating storage_path", path=repository.repository_path)
            os.makedirs(repository.repository_path, exist_ok=True)

        write_kwargs = {}
        dataframe.to_csv(file_path, index=False, **write_kwargs)

        self.info(
            msg=Event.TaskCompleted.value,
            id=item.identifier,
            info="dataframe is saved",
            filepath=file_path,
            size=len(dataframe),
        )

        return True


class DataFrameCleanupPipeline(GenericPipeline):
    def process(self, processor, item) -> None:
        super().process(processor=processor, item=item)

        dataframe: pd.DataFrame = item.request()
        self.evaluate(dataframe, pd.DataFrame)

        if dataframe.empty:
            self.warning(
                msg="Dataframe is empty.",
                id=item.identifier,
            )
            return

        self.debug(
            msg=Event.Processing.value,
            id=item.identifier,
            size=len(dataframe),
        )

        data = dataframe.fillna("")
        item.update_content(data)
        uid = processor.blackboard.write(pipeline=self, item=item, processor=processor)

        self.info(
            msg=Event.TaskCompleted.value,
            id=item.identifier,
            uid=uid,
            size=len(data),
        )


class DataFrameSummarisePipeline(GenericPipeline):
    def process(self, processor, item) -> None:
        super().process(processor=processor, item=item)

        dataframe: pd.DataFrame = item.request()
        self.evaluate(dataframe, pd.DataFrame)

        if dataframe.empty:
            self.warning(
                msg="Dataframe is empty.",
                id=item.identifier,
            )
            return

        self.debug(
            msg=Event.Processing.value,
            id=item.identifier,
            size=len(dataframe),
        )

        data = dataframe.fillna("")
        item.update_content(data)
        uid = processor.blackboard.write(pipeline=self, item=item, processor=processor)

        self.info(
            msg=Event.TaskCompleted.value,
            id=item.identifier,
            uid=uid,
            size=len(data),
        )


class CreateDataframeDocument(StrategyCreate):
    def execute(self, processor, *args, **kwargs) -> T:
        self.evaluate(processor, IProcessor)
        self.mandatory(name="item", cls=str, **kwargs)
        self.mandatory(name="content", cls=list, **kwargs)

        self.debug(msg=Event.Creating.value, id=self.item, size=len(self.content))

        content: pd.DataFrame = pd.DataFrame(self.content)
        document = DocumentFacade(DataFrameDocument(self.item))
        document.update_content(content)

        self.info(
            msg=Event.Created.value,
            id=document.identifier,
            size=len(content),
        )

        return document


class YoutubeTranscriptModel(AuditLogger):
    def __init__(
        self,
        url: str,
        level: int = logging.NOTSET,
        handler: Optional[logging.Handler] = None,
    ):
        AuditLogger.__init__(self, level=level, handler=handler)

        self.url = url
        self.storage_path = tmp.gettempdir()

        self.info(f"url: {url}")
        self.debug(f"storage path: {self.storage_path}")

        self.blackboard = GenericBlackboard(DocumentFacade, CreateDataframeDocument())
        self.blackboard.register(
            GenericRepository(
                strategy_read=RepositoryReadDocument(),
                strategy_write=RepositoryStoreDataframeDocument(),
                repository_path=self.storage_path,
                level=logging.INFO,
            )
        )

        processor = YoutubeTranscriptProcessor(
            blackboard=self.blackboard,
            pipelines=[
                DataFrameCleanupPipeline(),
                DataFrameSummarisePipeline(),
            ],
            storage_path=self.storage_path,
            videos=[url],
            level=logging.DEBUG,
        )
        processor.process_tasks()

    def view(self) -> HTMLResponse:
        endpoints_path = str(os.path.sep).join(__file__.rsplit(os.path.sep)[:-2])
        self.debug(f"endpoints_path: {endpoints_path}")
        for identifier in self.blackboard._storage:
            document = self.blackboard.read(identifier=identifier)
            df = (
                document.request()
            )  # df.drop(columns=['start', 'duration'], inplace=True)
            self.debug(df.columns)
            html = TextFileStream(
                f"{endpoints_path}/view/youtube.html",
                list_of_macros=[
                    ("@TITLE", "Transcript[YouTube]"),
                    ("@H1", ""),
                    ("@URL", self.url),
                    ("@CONTENT", df.to_html(index=False)),
                    ("@FOOTER", __file__),
                ],
            )
            return HTMLResponse(content=html.content)

        return HTMLResponse(content={"error": "transcript not found."})
