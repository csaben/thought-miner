import tempfile
from pathlib import Path

import aeneas.globalconstants as gc
from aeneas.executetask import ExecuteTask
from aeneas.language import Language
from aeneas.syncmap import SyncMapFormat
from aeneas.task import Task, TaskConfiguration
from aeneas.textfile import TextFileFormat

# create Task object
config = TaskConfiguration()
config[gc.PPN_TASK_LANGUAGE] = Language.ENG
config[gc.PPN_TASK_IS_TEXT_FILE_FORMAT] = TextFileFormat.PLAIN
config[gc.PPN_TASK_OS_FILE_FORMAT] = SyncMapFormat.JSON
task = Task()
task.configuration = config


# TODO: on upload/transcript gen use textwrap to set width (transcribe most likely spot)
# TODO: text_path? we should also have a way to load from db and take a string directly
def process_pair(audio_path: Path, transcript: str) -> SyncMapFormat:
    # TODO: hacky af, but lets just make a tmp file for the transcript rather than
    # go back and rewrite db code, we will do that and add a path later
    task.audio_file_path_absolute = audio_path
    with tempfile.NamedTemporaryFile(mode="w+t", delete=False) as temp_file:
        temp_file.write(transcript)
        task.text_file_path_absolute = temp_file.name
        # process Task
        ExecuteTask(task).execute()
    return task.sync_map.json_string
