import os
from typing import Dict, List, Optional

from .igt import IGT


def load_igt_file(path: str) -> List[IGT]:
    """
    Loads a file containing IGT data into a list of entries.

    Args:
        path (str): Either a single IGT file (`.txt` or `.igt`) or a directory. If a directory, will concat all the IGT from files recursively.

    Returns:
        List[IGT]

    ## Notes
    Files should be formatted as follows:

    ```text
    \\t Transcription
    \\m Segmentation (optional)
    \\p Part of speech tags (optional)
    \\g Glosses
    \\l Translation

    \\t Transcription
    \\m Segmentation (optional)
    \\p Part of speech tags (optional)
    \\g Glosses
    \\l Translation
    ...
    ```
    """
    all_data = []

    # If we have a directory, recursively load all files and concat together
    if os.path.isdir(path):
        for file in os.listdir(path):
            if file.endswith(".txt") or file.endswith(".igt"):
                all_data.extend(load_igt_file(os.path.join(path, file)))
        return all_data

    # If we have one file, read in line by line
    with open(path, "r") as file:
        empty_entry: Dict[str, Optional[str]] = {
            "transcription": None,
            "segmentation": None,
            "glosses": None,
            "pos_glosses": None,
            "translation": None,
        }
        current_entry = empty_entry.copy()

        for line in file:
            # Determine the type of line
            # If we see a type that has already been filled for the current entry, something is wrong
            line_prefix = line.strip()[:2]
            if line_prefix == "\\t" and current_entry["transcription"] is None:
                current_entry["transcription"] = line[3:].strip()
            elif line_prefix == "\\m" and current_entry["segmentation"] is None:
                current_entry["segmentation"] = line[3:].strip()
            elif line_prefix == "\\g" and current_entry["glosses"] is None:
                if len(line[3:].strip()) > 0:
                    current_entry["glosses"] = line[3:].strip()
            elif line_prefix == "\\p" and current_entry["pos_glosses"] is None:
                if len(line[3:].strip()) > 0:
                    current_entry["pos_glosses"] = line[3:].strip()
            elif line_prefix == "\\l" and current_entry["translation"] is None:
                current_entry["translation"] = line[3:].strip()
                # Once we have the translation, we've reached the end and can save this entry
                all_data.append(IGT.from_dict(current_entry))
                current_entry = empty_entry.copy()
            elif line.strip() != "":
                # Something went wrong
                raise ValueError("Found unexpected line: ", line)
            else:
                # We've reached a blank line
                if not current_entry == empty_entry:
                    all_data.append(IGT.from_dict(current_entry))
                    current_entry = empty_entry.copy()
        # Might have one extra line at the end
        if not current_entry == empty_entry:
            all_data.append(IGT.from_dict(current_entry))
    return all_data
