# Import modul
import os
import json
import pickle
from datetime import datetime


def save_service(format, source_data, destination_path):
    # Check if the destination path exists
    if os.path.exists(destination_path):
        # Save the data to the destination path using the chosen format
        now = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")  # Get the current date and time
        if format == "json":
            json_data = json.dumps(source_data)
            file_name = f"data_{now}.json"
            with open(os.path.join(destination_path, file_name), "w") as f:
                f.write(json_data)
        elif format == "pickle":
            file_name = f"data_{now}.pkl"
            with open(os.path.join(destination_path, file_name), "wb") as f:
                pickle.dump(source_data, f)
        elif format == "txt":
            json_data = json.dumps(source_data)
            file_name = f"data_{now}.txt"
            with open(os.path.join(destination_path, file_name), "w") as f:
                f.write(json_data)
        else:
            print("Format tidak valid. Pilih antara json atau pickle")
        print(f"Data berhasil disimpan ke flashdisk dengan nama {file_name}")
    else:
        print("Path tidak ada. Pastikan Path tujuan dengan benar")
