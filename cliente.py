import time
import os
from xmlrpc.client import ServerProxy
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Lista de IPs/portas dos outros nós na rede
PEERS = [
    'http://192.168.0.177:8084', # IP 1
]

class Watcher:
    def __init__(self):
        self.DIRECTORY_TO_WATCH = os.getcwd()  # Diretório atual
        self.observer = Observer()
        self.processed_files = set()  # Conjunto de arquivos processados

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

    def propagate_change(self, file_name, content, action):  # Função que envia o pacote aos endereços conectados
        for client in self.clients:
            try:
                client.handle_package(file_name, content, action)
            except Exception as e:
                print(f"Erro ao comunicar com peer: {e}")

    def on_created(self, event):  # Função de criação
        if not event.is_directory:
            file_name = event.src_path
            base_name = os.path.basename(file_name)
            
            if not base_name.startswith("1"): 
                print(f"{base_name} foi criado localmente.")
                with open(file_name, 'rb') as file: # Abro o arquivo que foi criado
                    content = file.read() # leio o conteudo dentro do arquvo e guardo em uma variavel
                self.propagate_change(base_name, content, "Created") # e mando todo o conteudo para o servidor
                self.processed_files.add(base_name) # adiciono o nome de arquivos na lista de arquivos a serem trackeados

    def on_modified(self, event):
        if not event.is_directory:
            file_name = event.src_path
            base_name = os.path.basename(file_name)
            
            ''' Esse If de checagem que occore em todos os métodos é para garantir que só o autor que possui o nome do arquivo original consiga modificar e deletar para todos
            já que quando o servidor cria um arquivo enviado por outra maquina ele adiciona esse "1" na frente, existem outras soluções mas foi a que a gnt pensou de forma mais rápida
            para uma solução inicial.'''
            if not base_name.startswith("1"):  
                print(f"{base_name} foi modificado localmente.")
                with open(file_name, 'rb') as file:
                    content = file.read()
                self.propagate_change(base_name, content, "Modified") # manda as modificações para o servidor através desas função

    def on_deleted(self, event):
        if not event.is_directory:
            file_name = event.src_path
            base_name = os.path.basename(file_name)
            
            if not base_name.startswith("1"):  
                print(f"{base_name} foi deletado localmente.")
                self.propagate_change(base_name, b'', "Deleted") # manda pro servidor
                self.processed_files.discard(base_name) # remove da lista de arquivos a serem "trackeados"

if __name__ == '__main__':
    print("Monitoramento Online em:", os.getcwd()) 
    w = Watcher()
    w.run()
