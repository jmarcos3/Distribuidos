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
        self.processed_files = self.initialize_processed_files()  # Inicializa com todos os arquivos do diretório

    def initialize_processed_files(self):
        processed_files = {}
        for root, _, files in os.walk(self.DIRECTORY_TO_WATCH):
            for file in files:
                file_path = os.path.join(root, file)
                processed_files[file_path] = os.path.getmtime(file_path)
        return processed_files

    def run(self):
        event_handler = Handler(self.processed_files)
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(1)  
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

class Handler(FileSystemEventHandler):
    def __init__(self, processed_files):
        super().__init__()
        self.clients = [ServerProxy(peer) for peer in PEERS]
        self.processed_files = processed_files

    def propagate_change(self, file_name, content, action):   # função que envia para todos os conectados na SEED
        for client in self.clients:
            try:
                client.handle_package(file_name, content, action)
            except Exception as e:
                print(f"Erro ao comunicar com peer: {e}")

    def on_created(self, event):   # Criação
        if not event.is_directory:   # se o evento não for uma pasta (só trackeia arquivos)
            file_name = event.src_path # pego o caminho do arquivo
            print(f"{os.path.basename(file_name)} foi criado.") # devolvo que o arquivo foi criado
            with open(file_name, 'rb') as file: # leio o conteudo do arquivo
                content = file.read()    # pego o que está dentro do arquivo
            self.propagate_change(file_name, content, "Created") # serializo isso em um pacote e já chamo a função de mandar para os clientes
            self.processed_files[file_name] = os.path.getmtime(file_name)  # adiciona arquivo e seu tempo de modificação que vai ser importante na hora de modificar

    def on_modified(self, event):   # Modificação
        if not event.is_directory: 
            file_name = event.src_path
            if file_name in self.processed_files: 
                current_mtime = os.path.getmtime(file_name)
                if current_mtime != self.processed_files[file_name]: # para evitar loops vamos utilizar o tempo de modificação do arquivo
                    print(f"{os.path.basename(file_name)} foi modificado.")
                    with open(file_name, 'rb') as file:
                        content = file.read()
                    self.propagate_change(file_name, content, "Modified")
                    self.processed_files[file_name] = current_mtime  # atualiza o tempo de modificação no dicionário

    def on_deleted(self, event): # Deletar
        if not event.is_directory:
            file_name = event.src_path
            if file_name in self.processed_files:
                print(f"{os.path.basename(file_name)} foi deletado.")
                self.propagate_change(file_name, b'', "Deleted")
                del self.processed_files[file_name]  # remove o arquivo do conjunto de arquivos processados

if __name__ == '__main__':
    print("Monitoramento Online em:", os.getcwd()) 
    w = Watcher()
    w.run()
