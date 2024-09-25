import psycopg2
from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_wtf.csrf import CSRFProtect
from markupsafe import Markup

from formularios import FormularioProduto, FormularioUsuario

app = Flask(__name__)
app.secret_key = 'ewerton'

csrf = CSRFProtect(app)

class Produto:
    def __init__(self, id, nome_produto, codigo, preco, quantidade, data_validade, fornecedor):
        self.id = id
        self.nome_produto = nome_produto
        self.codigo = codigo
        self.preco = preco
        self.quantidade = quantidade
        self.data_validade = data_validade
        self.fornecedor = fornecedor

class Usuario:
    def __init__(self, nome, nickname, senha):
        self.nome = nome
        self.nickname = nickname
        self.senha = senha

def conecta_bd():
    return psycopg2.connect(
        host="localhost",
        database="loja",
        user="postgres",
        password="admin"
    )

def buscar_produtos():
    conn = conecta_bd()
    cur = conn.cursor()
    cur.execute('SELECT id, nome_produto, codigo, preco, quantidade, data_validade, fornecedor FROM produtos')
    produtos = cur.fetchall()
    conn.close()
    return [Produto(*produto) for produto in produtos]

def adicionar_produto(produto):
    conn = conecta_bd()
    cur = conn.cursor()
    cur.execute('INSERT INTO produtos (nome_produto, codigo, preco, quantidade, data_validade, fornecedor) VALUES (%s, %s, %s, %s, %s, %s)',
                (produto.nome_produto, produto.codigo, produto.preco, produto.quantidade, produto.data_validade, produto.fornecedor))
    conn.commit()
    conn.close()

def buscar_usuarios():
    conn = conecta_bd()
    cur = conn.cursor()
    cur.execute('SELECT nome, nickname, senha FROM usuarios')
    usuarios = cur.fetchall()
    conn.close()
    return {usuario[1]: Usuario(*usuario) for usuario in usuarios}

@app.route('/')
def index():
    produtos = buscar_produtos()
    return render_template('lista.html', titulo='CadastraFácil', produtos=produtos)

@app.route('/novo')
def novo():
    if 'usuario_logado' not in session or session['usuario_logado'] is None:
        return redirect(url_for('login', proxima=url_for('novo')))
    form = FormularioProduto()
    return render_template('novo.html', titulo='Cadastro de Produtos', form=form)

@app.route('/criar', methods=['POST'])
def criar():
    form = FormularioProduto(request.form)

    if not form.validate_on_submit():
        return redirect(url_for('novo'))

    nome_produto = form.nome_produto.data
    codigo = form.codigo.data
    preco = form.preco.data
    quantidade = form.quantidade.data
    data_validade = form.data_validade.data
    fornecedor = form.fornecedor.data

    conn = conecta_bd()
    cur = conn.cursor()

    cur.execute('SELECT COUNT(*) FROM produtos WHERE nome_produto = %s', (nome_produto,))
    existe_produto = cur.fetchone()[0] > 0

    if existe_produto:
        flash(f'Produto com o nome "{nome_produto}" já existe!')
        conn.close()
        return redirect(url_for('novo'))

    novo_produto = Produto(None, nome_produto, codigo, preco, quantidade, data_validade, fornecedor)
    adicionar_produto(novo_produto)
    conn.close()

    flash('Produto adicionado com sucesso!')
    return redirect(url_for('index'))

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if 'usuario_logado' not in session or session['usuario_logado'] is None:
        return redirect(url_for('login', proxima=url_for('editar', id=id)))

    form = FormularioProduto()

    if request.method == 'POST':
        if form.validate_on_submit():
            nome_produto = form.nome_produto.data
            codigo = form.codigo.data
            preco = form.preco.data
            quantidade = form.quantidade.data
            data_validade = form.data_validade.data
            fornecedor = form.fornecedor.data

            conn = conecta_bd()
            cur = conn.cursor()
            cur.execute(
                'UPDATE produtos SET nome_produto = %s, codigo = %s, preco = %s, quantidade = %s, data_validade = %s, fornecedor = %s WHERE id = %s',
                (nome_produto, codigo, preco, quantidade, data_validade, fornecedor, id)
            )
            conn.commit()
            conn.close()

            flash('Produto atualizado com sucesso!')
            return redirect(url_for('index'))
    else:
        conn = conecta_bd()
        cur = conn.cursor()
        cur.execute('SELECT id, nome_produto, codigo, preco, quantidade, data_validade, fornecedor FROM produtos WHERE id = %s',
                    (id,))
        produto = cur.fetchone()
        conn.close()

        if produto:
            form.nome_produto.data = produto[1]
            form.codigo.data = produto[2]
            form.preco.data = produto[3]
            form.quantidade.data = produto[4]
            form.data_validade.data = produto[5]
            form.fornecedor.data = produto[6]
        else:
            flash('Produto não encontrado.')
            return redirect(url_for('index'))
    return render_template('editar.html', titulo='Edição de Produto', id=id, form=form)

@app.route('/deletar/<int:id>', methods=['POST'])
def deletar(id):
    if 'usuario_logado' not in session or session['usuario_logado'] is None:
        return redirect(url_for('login'))

    conn = conecta_bd()
    cur = conn.cursor()
    cur.execute('DELETE FROM produtos WHERE id = %s', (id,))
    conn.commit()
    conn.close()

    flash('Produto removido com sucesso!')
    return redirect(url_for('index'))

@app.route('/login')
def login():
    proxima = request.args.get('proxima', url_for('index'))
    form = FormularioUsuario()
    return render_template('login.html', proxima=proxima, form=form)

@app.route('/autenticar', methods=['POST'])
def autenticar():
    form = FormularioUsuario(request.form)

    if form.validate_on_submit():
        usuarios = buscar_usuarios()
        username = form.nickname.data

        if username in usuarios:
            usuario = usuarios[username]
            if form.senha.data == usuario.senha:
                session['usuario_logado'] = usuario.nickname
                flash(f'{usuario.nickname} logado com sucesso!')

                proxima_pagina = request.form.get('proxima', url_for('index'))
                return redirect(proxima_pagina)
        else:
            flash('Usuário não encontrado.')
    else:
        flash('Formulário inválido.')

    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session['usuario_logado'] = None
    flash('Logout efetuado com sucesso!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)