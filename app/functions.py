import os
import pymongo

from matplotlib import pyplot as plt

from classes import FileArray
from classes import LoggerEngine


def create_client():
    return pymongo.MongoClient(os.environ['MONGODB_CONNSTRING'])


def get_length(collection: pymongo.collection.Collection):
    return collection.count_documents({})


def import_csv(collection: pymongo.collection.Collection, file_array: FileArray,
               batch_size: int = 10000, exist_flag: bool = True):
    row_count = get_length(collection=collection) if exist_flag else 0
    data = file_array.get_data_batch(start_from=row_count, batch_size=batch_size)

    if len(data) == 0:
        return False

    collection.insert_many(data)
    return True


def log_row_count(collection: pymongo.collection.Collection, logger_engine: LoggerEngine, exist_flag: bool = True):
    row_count = get_length(collection=collection) if exist_flag else 0
    logger_engine.print_info(f'Rows already loaded: {row_count}')


def save_bar(filepath: str, labels: list, a_values: list, b_values: list, title: str = 'Title',
             a_label: str = 'A values', b_label: str = 'B values', y_label: str = 'y label',
             vertical_labels: bool = False, size_inches: tuple = None, bar_width: float = .4):
    x = [x for x in range(len(labels))]
    fig, ax = plt.subplots()
    if size_inches is not None:
        fig.set_size_inches(*size_inches)

    ax.bar([x - bar_width / 2 for x in x], a_values, bar_width, label=a_label)
    ax.bar([x + bar_width / 2 for x in x], b_values, bar_width, label=b_label)

    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.set_xticks(x)
    rotation = 'vertical' if vertical_labels else 'horizontal'
    ax.set_xticklabels(labels, rotation=rotation)
    ax.legend()

    fig.tight_layout()
    plt.savefig(filepath)


def save_load_time(filepath: str, start: float, end: float):
    template = 'Load time (s): {}'
    try:
        with open(filepath, 'r') as f:
            file_data = f.read()
            time_value = float(file_data.split(':')[-1].strip())

        with open(filepath, 'w') as f:
            f.write(template.format(time_value + (end - start)))

    except FileNotFoundError:
        with open(filepath, 'w') as f:
            f.write(template.format(end - start))
