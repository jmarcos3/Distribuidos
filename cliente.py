import time
import os
from xmlrpc.client import ServerProxy
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Lista de IPs/portas dos outros nós na rede
PEERS = [
    'http://127.0.0.1:8085',  # URL do servidor XML-RPC
    # Adicione mais nós conforme necessário
]

class Watcher:
    def __init__(self):
        self.DIRECTORY_TO_WATCH = os.getcwd()  # Diretório atual
        self.observer = Observer()
        self.processed_files = set()  # Conjunto para armazenar arquivos processados

    def run(self):
        event_handler = Handler(self.processed_files)
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(1)  # Reduzido o tempo de espera para 1 segundo para melhor responsividade
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

class Handler(FileSystemEventHandler):
    def __init__(self, processed_files):
        super().__init__()
        self.clients = [ServerProxy(peer) for peer in PEERS]
        self.processed_files = processed_files

    def propagate_change(self, file_name, content, action):
        for client in self.clients:
            try:
                client.handle_package(file_name, content, action)
            except Exception as e:
                print(f"Erro ao comunicar com peer: {e}")

    def on_created(self, event):
        if not event.is_directory:
            file_name = event.src_path
            if file_name not in self.processed_files:
                print(f"{file_name} foi criado.")
                with open(file_name, 'rb') as file:
                    content = file.read()
                self.propagate_change(file_name, content, "Created")
                self.processed_files.add(file_name)  # Adiciona o arquivo ao conjunto de arquivos processados

    def on_modified(self, event):
        if not event.is_directory:
            file_name = event.src_path
            if file_name not in self.processed_files:
                print(f"{file_name} foi modificado.")
                with open(file_name, 'rb') as file:
                    content = file.read()
                self.propagate_change(file_name, content, "Modified")
                self.processed_files.add(file_name)  # Adiciona o arquivo ao conjunto de arquivos processados

    def on_deleted(self, event):
        if not event.is_directory:
            file_name = event.src_path
            if file_name not in self.processed_files:
                print(f"{file_name} foi deletado.")
                self.propagate_change(file_name, b'', "Deleted")
                self.processed_files.add(file_name)  # Adiciona o arquivo ao conjunto de arquivos processados

if __name__ == '__main__':
    print("Monitoramento Online em:", os.getcwd()) 
    w = Watcher()
    w.run()
