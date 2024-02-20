
import os
import loguru
from pathlib import Path
import shutil
import datetime
import json
import zlib
import re
import time
loguru.logger.add("file.log", rotation="500 MB")

def calculate_hash(file_path):

    with open(file_path, 'rb') as file:
        file_hash = zlib.adler32(file.read())
    
    return file_hash


def get_date_from_file_name(file_path):
    
    # try to find YYYYMMDD in the file name

    file_name = os.path.basename(file_path)

    pattern = r"(\d{4})(\d{2})(\d{2})"

    match = re.search(pattern, file_name)

    if match:
        year = int(match.group(1))
        if year < 2000 or year > 2024: # if year is not between 2000 and 2024, it is probably not a date
            return None

        month = match.group(2)

        if int(month) > 12 or int(month) < 1:
            return None

        day = match.group(3)

        if int(day) > 31 or int(day) < 1:
            return None

        return datetime.datetime(int(year), int(month), int(day))

    else:
        return None

def get_created_date(file_path):

    created_time = get_date_from_file_name(file_path)

    if created_time is not None:
            
        return created_time

    try:


        created_time = os.path.getctime(file_path)


    except OSError:
        # if modified time cannot be read, use creation time
        try:
            created_time = os.path.getmtime(file_path)
        
        except OSError:
            # if creation time cannot be read raise exception
            raise Exception("Cannot read modified time or creation time", file_path)
    created_time = datetime.datetime.fromtimestamp(created_time)
        
    return created_time




def copy_files(source_path:str, target_path:str, progress_callback=None, exception_queue=None):
    
    source_path = Path(source_path)
    target_path = Path(target_path)

    files_index_path = target_path / "files_index.jsonl"
    processed_files = 0
    all_files = list(source_path.rglob('*'))
    total_files = len(all_files)  
    for file_path in all_files:
        processed_files += 1
        time.sleep(2)
        progress_value = int(processed_files / total_files * 100)
        if file_path.is_file():
            # Do something with the file
            loguru.logger.info(file_path)
            # omit files that are not images or videos
            if file_path.suffix.lower() not in ['.jpg', '.jpeg', '.png', '.mp4', '.mov', '.avi', '.mpg', '.mpeg', '.wmv', '.3gp', '.3g2', '.m4v', '.mkv', '.webm','.webp', ".txt", ".pdf"]:
                print(file_path.suffix)
                progress_callback(progress_value)
                loguru.logger.info("File is not an image or video: " + file_path.as_posix() + " skipping")
                continue

            original_path = file_path.as_posix()
            file_hash = calculate_hash(original_path)
            created_time = get_created_date(original_path)

            # target directory is YYYY/MM

            target_directory = target_path / str(created_time.year) / str(created_time.month)

            target_directory.mkdir(parents=True, exist_ok=True)

            target_file_path = target_directory / file_path.name

            
            if target_file_path.exists():
        
                    # check if the file is the same as the original file    
                    target_file_hash = calculate_hash(target_file_path.as_posix())

                    if file_hash == target_file_hash:
        
                        # file is the same as the original file
                        # write log message
                        loguru.logger.info("File already exists: " + target_file_path.as_posix() + "skipping")
                        progress_callback(progress_value)
                        continue
        
                    else:
        
                        # file is different from the original file
        
                        # rename the file
                        date_str = created_time.strftime("%Y_%m_%d_%H_%M_%S")
                        new_file_name = file_path.stem + "_" + date_str + file_path.suffix
                        target_file_path = target_directory / new_file_name

            # copy the file to the target directory

            shutil.copy(original_path, target_file_path)

            # check if the file exists in the target directory


            if not target_file_path.exists():
                if exception_queue is not None:
                    exception_queue.put("File not copied to target directory")
                raise Exception("File not copied to target directory")
            
            # check if the file is the same as the original file
            target_file_hash = calculate_hash(target_file_path.as_posix())

            if file_hash != target_file_hash:

                if exception_queue is not None:
                    exception_queue.put("File hashes do not match")
                raise Exception("File hashes do not match")
            
            # write the file index
            files_index_path.open('a').write(json.dumps(
                {
                    "original_path": original_path,
                    "target_path": target_file_path.as_posix(),
                    "modified_time": created_time.isoformat(),
                    "file_hash": file_hash
                }
            ) + "\n")
            progress_callback(progress_value)
            loguru.logger.info("File copied: " + target_file_path.as_posix())
            



        

        



