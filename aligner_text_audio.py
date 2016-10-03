# -*- coding: utf-8 -*-

import sys
sys.path.append('/home/anya/aeneas')

from aeneas.executetask import ExecuteTask
from aeneas.task import Task


def print_text_by_one_word_in_string(input_path, output_path):

    with open(input_path) as f:
        text = f.read().split()

    with open(output_path, 'wb') as f_out:
        for line in text:
            f_out.write(line + '\n')


if __name__ == '__main__':

    audio_path = 'forrest_audio_3-15_min.mp3'
    input_file = 'subtitles_by_word_first_15_min.txt'
    output_file = 'forrest_align_by_word_first_15_min.txt'

    #audiodata = AudioSegment.from_file(audio_path, format='wav')
    #print_text_by_one_word_in_string(input_file, output_file)

    config_string = u"task_language=deu|is_text_type=plain|os_task_file_format=txt"
    task = Task(config_string=config_string)
    task.audio_file_path_absolute = audio_path
    task.text_file_path_absolute = input_file
    task.sync_map_file_path_absolute = output_file

    # process Task
    ExecuteTask(task).execute()

    # output sync map to file
    task.output_sync_map_file()
