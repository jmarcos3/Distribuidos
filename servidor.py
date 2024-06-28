from xmlrpc.server import SimpleXMLRPCServer
import os
from xmlrpc.client import Binary

class FileSyncServer:
    def handle_package(self, file_name, content, action):
        try:
            if action == "Created":
                self.create_file(file_name, content)
            elif action == "Modified":
                self.modify_file(file_name, content)
            elif action == "Deleted":
                self.delete_file(file_name)
            return True
        except Exception as e:
            print(f"Erro ao processar pacote: {e}")
            return False

    def create_file(self, file_name, content):
        with open(file_name, 'wb') as f:
            f.write(content.data if isinstance(content, Binary) else content)
        print(f"{file_name} foi criado com sucesso.")

    def modify_file(self, file_name, content):
        if os.path.exists(file_name):
            with open(file_name, 'wb') as f:
                f.write(content.data if isinstance(content, Binary) else content)
            print(f"{file_name} foi modificado com sucesso.")
        else:
            print(f"Erro ao modificar {file_name}: Arquivo não encontrado.")

    def delete_file(self, file_name):
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"{file_name} foi deletado com sucesso.")
        else:
            print(f"Erro ao deletar {file_name}: Arquivo não encontrado.")

def run_server(port):
    server = SimpleXMLRPCServer(('localhost', port))
    server.register_instance(FileSyncServer())
    print(f"Servidor RPC está rodando na porta {port}...")
    server.serve_forever()

if __name__ == "__main__":
    run_server(8085)  # Modifique a porta conforme necessário
