import gzip
import json

from fastavro import reader
from tqdm import tqdm
from pathlib import Path


def validate_file(file_path):
    try:
        with gzip.open(file_path) as f:
            docs = []
            for line in f:
                docs.append(json.loads(line))
            return True
    except json.decoder.JSONDecodeError:
        print(f"json.decoder.JSONDecodeError for file {file_path}")
        return False


def avro_to_jsonl(file, overwrite=False):
    with open(file, "rb") as in_file:
        avro_reader = reader(in_file)
        out_file_path = f"{file.split('.')[0]}.jsonl.gz"
        if Path(out_file_path).exists() and not overwrite:
            print(f"File {out_file_path} already exists. Skipping.")
        else:
            with gzip.open(out_file_path, "wt") as out_file:
                for record in tqdm(avro_reader, desc=f"Processing {file}"):
                    out_file.write(json.dumps(record) + "\n")
        assert validate_file(out_file_path), f"Validation failed for file {out_file_path}"
        print(f"Validation passed for file {out_file_path}")


def main():
    for file in [
        "v1_20210811/train.avro",
        "v1_20210811/dev.avro",
        "v1_20210811/test.avro"
    ]:
        avro_to_jsonl(file, overwrite=True)


if __name__ == "__main__":
    main()
