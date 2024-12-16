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


def process_pair(audio_path: Path, text_path: Path) -> SyncMapFormat:
    task.audio_file_path_absolute = audio_path
    task.text_file_path_absolute = text_path
    # process Task
    ExecuteTask(task).execute()
    return task.sync_map.json_string
