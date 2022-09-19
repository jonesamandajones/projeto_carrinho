from functools import reduce
from fastapi import FastAPI
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI()

OK = "OK"
FALHA = "FALHA"

class Endereco(BaseModel):
    id_end: int
    rua: str
    cep: str
    cidade: str
    estado: str

class Usuario(BaseModel):
    id: int
    nome: str
    email: str
    senha: str

class EnderecosUsuario(BaseModel):
    usuario: Usuario
    lista_enderecos: List[Endereco] = []

class Produto(BaseModel): 
    id_produto: int
    nome: str
    descricao: str
    preco: float

class CarrinhoDeCompras(BaseModel): 
    id_usuario: int
    id_produtos: List[Produto] = []
    preco_total: Optional[float] = None
    quantidade_de_produtos: Optional[int] = None

db_usuarios = {}
db_produtos = {}
db_end = {}
db_carrinhos = {}


####################### POST ######################

@app.post("/usuario/")
async def criar_usuário(usuario: Usuario):
    if usuario.id in db_usuarios:
        return FALHA
    db_usuarios[usuario.id] = usuario
    return usuario

@app.post("/endereco/{id_usuario}/")
async def criar_endereco(id_usuario: int, endereco: Endereco):
    if id_usuario in db_end: 
        db_end[id_usuario].lista_enderecos.append(endereco)
        return db_end[id_usuario]
    
    if id_usuario in db_usuarios:
        db_end[id_usuario] = EnderecosUsuario(
            usuario = db_usuarios[id_usuario],
            lista_enderecos = [endereco]
        )
        return db_end[id_usuario]
    
    return FALHA

@app.post("/catalogo/{id_produto}/")
async def cadastrar_produto(produto: Produto):
    if produto.id_produto in db_produtos:
        return FALHA  
    db_produtos[produto.id_produto] = produto
    return db_produtos        

@app.post("/carrinho/{id_usuario}/{id_produto}/")
async def criar_carrinho(carrinho: CarrinhoDeCompras, id_usuario: int, id_produto: int):
    if carrinho.id_usuario in db_carrinhos:
        db_carrinhos[carrinho.id_usuario].id_produtos.append(db_produtos[id_produto])
        db_carrinhos[carrinho.id_usuario].preco_total += db_produtos[id_produto].preco 
        db_carrinhos[carrinho.id_usuario].quantidade_de_produtos += 1
        return db_carrinhos
    if carrinho.id_usuario not in db_carrinhos:
        db_carrinhos[id_usuario] = CarrinhoDeCompras(
            id_usuario = id_usuario,
            id_produtos = [db_produtos[id_produto]], 
            preco_total = db_produtos[id_produto].preco,
            quantidade_de_produtos = 1
        )
        return db_carrinhos
    
    return FALHA
       
####################### GET ######################

@app.get("/usuario/")
async def retornar_usuario(id: int):
    if id in db_usuarios:
        return db_usuarios[id]
    return FALHA

@app.get("/usuario/{nome}")
async def retornar_usuario_com_nome(nome: str):
    for _, v in db_usuarios.items():
        if nome in v.nome:
            return v
    
    return FALHA
   
@app.get("/usuario/{id_usuario}/enderecos/")
async def retornar_enderecos_do_usuario(id_usuario: int):
    if id_usuario in db_end:
        return db_end[id_usuario]
    return FALHA

@app.get("/usuarios/{dominio}")
async def retornar_emails(dominio: str):
    for _, v in db_usuarios.items():
        if dominio in v.email:
            return v    
    return FALHA

@app.get("/carrinho/{id_usuario}/")
async def retornar_carrinho(id_usuario: int):
    if id_usuario in db_carrinhos:
        return db_carrinhos[id_usuario]
    return FALHA

@app.get("/carrinho/total/{id_usuario}/")
async def retornar_total_carrinho(id_usuario: int):
    if id_usuario in db_carrinhos:
        return {
            "Quantidade": db_carrinhos[id_usuario].quantidade_de_produtos,
            "Valor total": db_carrinhos[id_usuario].preco_total
        }      
    return FALHA


@app.get("/catalogo/")
async def retornar_catalogo():
    return db_produtos

@app.get("/usuarios/")
async def retornar_usuarios():
    return db_usuarios

@app.get("/carrinhos/")
async def retornar_carrinhos():
    return db_carrinhos
  
@app.get("/")
async def bem_vinda():
    site = "Seja muito bem-vinda!"
    return site.replace('\n', '')


####################### DELETE ######################

@app.delete("/usuario/{id}")
async def deletar_usuario(id: int):
    if id in db_usuarios:
        del db_usuarios[id]
        return db_usuarios
    return FALHA

@app.delete("/endereco/{id_usuario}/{id_endereco}/")
async def deletar_endereco(id_usuario: int, id_endereco: int):
    
    if id_usuario in db_usuarios:
        for endereco in db_end[id_usuario].lista_enderecos:
            if id_endereco == endereco.id_end:
                db_end[id_usuario].lista_enderecos.remove(endereco)
                return db_end[id_usuario]
        
    return FALHA

@app.delete("/catalogo/{id_produto}/")
async def deletar_produto(id_produto: int):
    if id_produto in db_produtos:
        del db_produtos[id_produto]
        return db_produtos
    
    return FALHA

@app.delete("/carrinho/{id_usuario}/")
async def deletar_carrinho(id_usuario: int):
        if id_usuario in db_carrinhos:
            del db_carrinhos[id_usuario]
            return db_carrinhos
        return FALHA