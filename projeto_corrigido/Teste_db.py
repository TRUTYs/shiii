import sys
import os

sys.path.append(os.getcwd())

try:
    from app import app, db, Produto
    print("✅ Ficheiro app.py encontrado!")
except ImportError as e:
    print(f"❌ Erro: Não encontrei o ficheiro 'app.py' na mesma pasta. Erro: {e}")
    exit()

def testar_conexao():
    with app.app_context():
        try:
            # Tenta contar quantos produtos existem
            total = Produto.query.count()
            print("-----------------------------------------")
            print("✅ SUCESSO TOTAL: O Python ligou-se ao Banco!")
            print(f"Total de produtos no banco: {total}")
            print("-----------------------------------------")
        except Exception as e:
            print("-----------------------------------------")
            print("❌ ERRO NO BANCO: O ficheiro existe, mas a senha ou o nome do banco está errado.")
            print(f"Detalhe do erro: {e}")
            print("-----------------------------------------")

if __name__ == "__main__":
    testar_conexao()