import tqdm
import os


def upload_path(self):
    SEPARATOR = "<SEPARATOR>"
    BUFFER_SIZE = 1048576  # 1MB
    filename = "paths.json"
    filesize = os.path.getsize(filename)
    for i in self.all_connections:
        i.send(f"{filename}{SEPARATOR}{filesize}".encode())
        progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "rb") as f:
            while True:
                # read the bytes from the file
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    # file transmitting is done
                    break
                # we use sendall to assure transmission in
                # busy networks
                i.sendall(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))
