from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import urllib.parse
from datetime import datetime

app = Flask(__name__)
app.secret_key = "eight_sistemas_2026"

usuario = 'root'
senha = 'fucapfaculdade.2026'
host = 'localhost'
banco = 'projeto'
senha_segura = urllib.parse.quote_plus(senha)

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{usuario}:{senha_segura}@{host}/{banco}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#   ----------
#   CLASSES
#   ----------

class Fornecedor(db.Model):
    __tablename__ = 'fornecedores'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    contato = db.Column(db.String(50))
    email = db.Column(db.String(100))
    cnpj = db.Column(db.String(18))
    localizacao = db.Column(db.String(200))
    produtos = db.relationship('Produto', backref='fornecedor', lazy=True)


class Produto(db.Model):
    __tablename__ = 'produtos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50))
    categoria = db.Column(db.String(50))
    quantidade = db.Column(db.Integer, default=0)
    estoque_minimo = db.Column(db.Integer, default=5)
    preco_custo = db.Column(db.Numeric(10, 2))
    preco_venda = db.Column(db.Numeric(10, 2))
    fornecedor_id = db.Column(db.Integer, db.ForeignKey('fornecedores.id'))
    descricao = db.Column(db.Text)


class Movimentacao(db.Model):
    __tablename__ = 'movimentacoes_estoque'
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id', ondelete='CASCADE'))
    tipo = db.Column(db.Enum('entrada', 'saida'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    origem = db.Column(db.Enum('compra', 'venda', 'ajuste'), nullable=False)
    valor_unitario = db.Column(db.Numeric(10, 2))
    custo_unitario = db.Column(db.Numeric(10, 2))
    data_movimentacao = db.Column(db.DateTime, default=db.func.current_timestamp())


#   ------------
#   ROTAS
#   ------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/estoque')
def estoque():
    produtos_db = Produto.query.all()
    fornecedores_db = Fornecedor.query.all()

    lista_para_exibir = []
    for p in produtos_db:
        forn = Fornecedor.query.get(p.fornecedor_id)
        lista_para_exibir.append({
            "id": p.id,
            "nome": p.nome,
            "quantidade": p.quantidade,
            "preco_venda": p.preco_venda,
            "preco_custo": p.preco_custo,
            "fornecedor_nome": forn.nome if forn else "Sem Fornecedor",
            "fornecedor_id": p.fornecedor_id,
            "categoria": p.categoria,
            "estoque_minimo": p.estoque_minimo,
        })

    return render_template('estoque.html', produtos=lista_para_exibir, fornecedores=fornecedores_db)


#   -----------
#   FORNECEDORES
#   -----------

@app.route('/fornecedores')
def fornecedores():
    lista = Fornecedor.query.all()
    return render_template('fornecedores.html', fornecedores=lista)


@app.route('/cadastrar_fornecedor', methods=['POST'])
def cadastrar_fornecedor():
    nome_forn      = request.form.get('nome_fornecedor')
    contato_forn   = request.form.get('contato_fornecedor')
    email_forn     = request.form.get('email_fornecedor')
    cnpj_forn      = request.form.get('cnpj_fornecedor')
    local_forn     = request.form.get('localizacao_fornecedor')

    if nome_forn:
        novo_forn = Fornecedor(
            nome=nome_forn,
            contato=contato_forn,
            email=email_forn,
            cnpj=cnpj_forn,
            localizacao=local_forn
        )
        db.session.add(novo_forn)
        db.session.commit()
    return redirect(url_for('fornecedores'))


@app.route('/editar_fornecedor/<int:id>', methods=['POST'])
def editar_fornecedor(id):
    fornecedor = Fornecedor.query.get(id)
    if fornecedor:
        fornecedor.nome        = request.form.get('nome_fornecedor')
        fornecedor.contato     = request.form.get('contato_fornecedor')
        fornecedor.email       = request.form.get('email_fornecedor')
        fornecedor.cnpj        = request.form.get('cnpj_fornecedor')
        fornecedor.localizacao = request.form.get('localizacao_fornecedor')
        db.session.commit()
    return redirect(url_for('fornecedores'))


@app.route('/excluir_fornecedor/<int:id>')
def excluir_fornecedor(id):
    fornecedor = Fornecedor.query.get(id)
    if fornecedor:
        produtos_vinculados = Produto.query.filter_by(fornecedor_id=id).all()
        for p in produtos_vinculados:
            p.fornecedor_id = None
        db.session.commit()
        db.session.delete(fornecedor)
        db.session.commit()
    return redirect(url_for('fornecedores'))


#   ----------------------
#   ADICIONAR PRODUTOS AO ESTOQUE (COMPRA)
#   ----------------------

@app.route('/adicionar_produto', methods=['POST'])
def adicionar_produto():
    nome       = request.form.get('nome', '').strip()
    categoria  = request.form.get('categoria', '').strip()
    qtd_raw    = request.form.get('quantidade', '').strip()
    forn_id    = request.form.get('fornecedor_id')

    # Valida campos obrigatórios
    if not nome or qtd_raw == '':
        flash('Campos obrigatórios não preenchidos.', 'erro')
        return redirect(url_for('estoque'))

    try:
        quantidade  = int(qtd_raw)
        preco_venda = float(request.form.get('preco_venda', 0) or 0)
        preco_custo = float(request.form.get('preco_custo', 0) or 0)
    except ValueError:
        flash('Campos obrigatórios não preenchidos.', 'erro')
        return redirect(url_for('estoque'))

    produto_existente = Produto.query.filter_by(nome=nome).first()

    if produto_existente:
        produto_existente.quantidade += quantidade
        produto_existente.preco_venda = preco_venda
        produto_existente.preco_custo = preco_custo
        db.session.commit()
        flash(f'Estoque de "{nome}" atualizado com sucesso!', 'sucesso')
    else:
        novo_produto = Produto(
            nome=nome,
            categoria=categoria,
            quantidade=quantidade,
            preco_venda=preco_venda,
            preco_custo=preco_custo,
            fornecedor_id=int(forn_id) if forn_id else None
        )
        db.session.add(novo_produto)
        db.session.commit()
        flash(f'Produto "{nome}" cadastrado com sucesso!', 'sucesso')

    return redirect(url_for('estoque'))


#   -------
#   COMPRAR PRODUTOS (REPOSIÇÃO)
#   -------

@app.route('/comprar_produto/<int:id>', methods=['POST'])
def comprar_produto(id):
    p = Produto.query.get(id)
    if p:
        try:
            quantidade = int(request.form.get('quantidade', 0))
            if quantidade > 0:
                nova_mov = Movimentacao(
                    produto_id=p.id,
                    tipo='entrada',
                    quantidade=quantidade,
                    origem='compra',
                    valor_unitario=p.preco_custo,
                    custo_unitario=p.preco_custo
                )
                p.quantidade += quantidade
                db.session.add(nova_mov)
                db.session.commit()
        except Exception as e:
            print(f"Erro ao processar compra: {e}")
            db.session.rollback()

    return redirect(url_for('estoque'))


#   --------
#   EDITAR PRODUTO
#   --------

@app.route('/editar_produto/<int:id>', methods=['POST'])
def editar_produto(id):
    produto = Produto.query.get(id)
    if not produto:
        flash('Produto não encontrado.', 'erro')
        return redirect(url_for('estoque'))

    nome    = request.form.get('nome', '').strip()
    qtd_raw = request.form.get('quantidade', '').strip()
    forn_id = request.form.get('fornecedor_id')

    if not nome or qtd_raw == '':
        flash('Campos obrigatórios não preenchidos.', 'erro')
        return redirect(url_for('estoque'))

    try:
        quantidade  = int(qtd_raw)
        preco_venda = float(request.form.get('preco_venda', 0) or 0)
        preco_custo = float(request.form.get('preco_custo', 0) or 0)
    except ValueError:
        flash('Campos obrigatórios não preenchidos.', 'erro')
        return redirect(url_for('estoque'))

    if quantidade < 0:
        flash('O estoque não permite quantidade negativa.', 'erro')
        return redirect(url_for('estoque'))

    produto.nome      = nome
    produto.categoria = request.form.get('categoria', '').strip()
    produto.quantidade  = quantidade
    produto.preco_venda = preco_venda
    produto.preco_custo = preco_custo
    produto.fornecedor_id = None if (forn_id in ('', 'None')) else int(forn_id)

    db.session.commit()
    flash(f'Produto "{nome}" atualizado com sucesso!', 'sucesso')

    return redirect(url_for('estoque'))


#   --------
#   EXCLUIR PRODUTO
#   --------

@app.route('/excluir_produto/<int:id>')
def excluir_produto(id):
    produto = Produto.query.get(id)
    if produto:
        db.session.delete(produto)
        db.session.commit()
        print(f"Produto {id} removido com sucesso!")
    return redirect(url_for('estoque'))


#   ------------
#   CADASTRAR VENDA
#   ------------

@app.route('/vender_produto/<int:id>', methods=['POST'])
def vender_produto(id):
    p = Produto.query.get(id)
    if not p:
        flash('Produto não encontrado.', 'erro')
        return redirect(url_for('estoque'))

    try:
        quantidade = int(request.form.get('quantidade', 0))

        if quantidade <= 0:
            flash('A quantidade deve ser maior que zero.', 'erro')
        elif p.quantidade < quantidade:
            flash(
                f'Estoque insuficiente! Você tentou vender {quantidade} unidade(s) '
                f'de "{p.nome}", mas só há {p.quantidade} em estoque.',
                'erro'
            )
        else:
            nova_mov = Movimentacao(
                produto_id=p.id,
                tipo='saida',
                quantidade=quantidade,
                origem='venda',
                valor_unitario=p.preco_venda,
                custo_unitario=p.preco_custo
            )
            p.quantidade -= quantidade
            db.session.add(nova_mov)
            db.session.commit()
            flash(f'Venda de {quantidade}x "{p.nome}" realizada com sucesso!', 'sucesso')

    except Exception as e:
        print(f"Erro ao processar venda: {e}")
        db.session.rollback()
        flash('Erro interno ao processar a venda. Tente novamente.', 'erro')

    return redirect(url_for('estoque'))


#   ---------------
#   DASHBOARD / MOVIMENTO
#   ---------------

@app.route('/movimento')
def movimento():
    from datetime import timedelta

    # Lê o filtro escolhido pelo usuário (padrão: mensal)
    filtro = request.args.get('filtro', 'mensal')

    agora = datetime.now()
    filtros_map = {
        'diario':      agora - timedelta(days=1),
        'semanal':     agora - timedelta(weeks=1),
        'mensal':      agora - timedelta(days=30),
        'trimestral':  agora - timedelta(days=90),
        'semestral':   agora - timedelta(days=180),
        'anual':       agora - timedelta(days=365),
    }
    data_inicio = filtros_map.get(filtro, filtros_map['mensal'])

    # Busca movimentações filtradas por data
    movimentacoes = db.session.query(Movimentacao, Produto).join(
        Produto, Movimentacao.produto_id == Produto.id
    ).filter(
        Movimentacao.data_movimentacao >= data_inicio
    ).order_by(Movimentacao.data_movimentacao.desc()).all()

    # Calcula totais para o dashboard
    total_vendas = 0
    total_lucro  = 0
    total_compras = 0

    for mov, prod in movimentacoes:
        if mov.tipo == 'saida' and mov.origem == 'venda':
            receita = float(mov.valor_unitario or 0) * mov.quantidade
            custo   = float(mov.custo_unitario or 0) * mov.quantidade
            total_vendas  += receita
            total_lucro   += (receita - custo)
        elif mov.tipo == 'entrada' and mov.origem == 'compra':
            total_compras += float(mov.valor_unitario or 0) * mov.quantidade

    # Produtos com estoque baixo
    alertas = Produto.query.filter(Produto.quantidade <= Produto.estoque_minimo).all()

    lista_mov = []
    for mov, prod in movimentacoes:
        lista_mov.append({
            "id": mov.id,
            "produto_nome": prod.nome,
            "tipo": mov.tipo,
            "origem": mov.origem,
            "quantidade": mov.quantidade,
            "valor_unitario": mov.valor_unitario,
            "data": mov.data_movimentacao.strftime('%d/%m/%Y %H:%M') if mov.data_movimentacao else "-"
        })

    return render_template('movimento.html',
                           movimentacoes=lista_mov,
                           total_vendas=total_vendas,
                           total_lucro=total_lucro,
                           total_compras=total_compras,
                           alertas=alertas,
                           filtro_ativo=filtro)


if __name__ == '__main__':
    print("Sistema Eight Sistemas Iniciado!")
    app.run(debug=True)
