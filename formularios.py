from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, validators

class FormularioProduto(FlaskForm):
    nome_produto = StringField('Nome do Produto', [validators.DataRequired(), validators.Length(min=1, max=100)])
    codigo = StringField('Código', [validators.DataRequired(), validators.Length(min=1, max=50)])
    preco = StringField('Preço', [validators.DataRequired(), validators.Length(min=1, max=20)])
    quantidade = StringField('Quantidade', [validators.DataRequired(), validators.Length(min=1, max=50)])
    data_validade = StringField('Data de Validade', [validators.DataRequired(), validators.Length(min=1, max=20)])
    fornecedor = StringField('Fornecedor', [validators.DataRequired(), validators.Length(min=1, max=100)])
    salvar = SubmitField('Salvar')

class FormularioUsuario(FlaskForm):
    nickname = StringField('Usuário',[validators.DataRequired(), validators.Length(min=1, max=50)] )
    senha = PasswordField ('Senha', [validators.DataRequired(), validators.Length(min=1, max=50)])
    login = SubmitField('Login')