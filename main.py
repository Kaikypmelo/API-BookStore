from fastapi import FastAPI, HTTPException, Depends, status
from sqlmodel import SQLModel, Field, Session, create_engine, select, Relationship
from typing import List, Optional
from datetime import date
from contextlib import asynccontextmanager

# ==========================================
# 1. CONFIGURAÇÃO DO BANCO DE DADOS
# ==========================================
# Conexão com o PostgreSQL usando os dados fornecidos
DATABASE_URL = "postgresql://kaiky:123456789@127.0.0.1:5432/aula_python_db"
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

# ==========================================
# 2. MODELAGEM DE DADOS (Tabelas e Relacionamentos)
# ==========================================
class Livro(SQLModel, table=True):
    __tablename__ = "livros"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str
    ano_publicacao: int
    genero: str
    autor_id: int = Field(foreign_key="autores.id")
    
    # Relacionamento: Vários livros pertencem a um autor
    autor: Optional["Autor"] = Relationship(back_populates="livros")

class Autor(SQLModel, table=True):
    __tablename__ = "autores"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    nacionalidade: str
    data_nascimento: date
    
    # Relacionamento: Um autor pode ter vários livros
    livros: List[Livro] = Relationship(back_populates="autor")


# ==========================================
# 3. INICIALIZAÇÃO DA API E AUTO-CRIAÇÃO DAS TABELAS
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria as tabelas automaticamente ao iniciar a API, caso não existam
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(
    title="BookStore API", 
    description="Sistema de Gerenciamento de Biblioteca Digital",
    lifespan=lifespan
)

# ==========================================
# 4. ENDPOINTS - AUTORES
# ==========================================
@app.post("/autores", status_code=status.HTTP_201_CREATED, response_model=Autor)
def criar_autor(autor: Autor, session: Session = Depends(get_session)):
    session.add(autor)
    session.commit()
    session.refresh(autor)
    return autor

@app.get("/autores", response_model=List[Autor])
def listar_autores(session: Session = Depends(get_session)):
    autores = session.exec(select(Autor)).all()
    return autores

@app.get("/autores/{id}", response_model=Autor)
def buscar_autor(id: int, session: Session = Depends(get_session)):
    autor = session.get(Autor, id)
    if not autor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Autor não encontrado")
    return autor

@app.put("/autores/{id}", response_model=Autor)
def atualizar_autor(id: int, autor_atualizado: Autor, session: Session = Depends(get_session)):
    autor_db = session.get(Autor, id)
    if not autor_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Autor não encontrado")
    
    autor_data = autor_atualizado.model_dump(exclude_unset=True)
    for key, value in autor_data.items():
        setattr(autor_db, key, value)
        
    session.add(autor_db)
    session.commit()
    session.refresh(autor_db)
    return autor_db

@app.delete("/autores/{id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_autor(id: int, session: Session = Depends(get_session)):
    autor = session.get(Autor, id)
    if not autor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Autor não encontrado")
    
    session.delete(autor)
    session.commit()
    return None

# ==========================================
# 5. ENDPOINTS - LIVROS
# ==========================================
@app.post("/livros", status_code=status.HTTP_201_CREATED, response_model=Livro)
def criar_livro(livro: Livro, session: Session = Depends(get_session)):
    # Valida se o autor_id existe antes de criar o livro
    autor = session.get(Autor, livro.autor_id)
    if not autor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ID de Autor inválido. Autor não encontrado.")
    
    session.add(livro)
    session.commit()
    session.refresh(livro)
    return livro

@app.get("/livros", response_model=List[Livro])
def listar_livros(session: Session = Depends(get_session)):
    livros = session.exec(select(Livro)).all()
    return livros

@app.get("/livros/{id}", response_model=Livro)
def buscar_livro(id: int, session: Session = Depends(get_session)):
    livro = session.get(Livro, id)
    if not livro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado")
    return livro

@app.put("/livros/{id}", response_model=Livro)
def atualizar_livro(id: int, livro_atualizado: Livro, session: Session = Depends(get_session)):
    livro_db = session.get(Livro, id)
    if not livro_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado")
    
    # Se estiver tentando mudar o autor_id, verifica se o novo autor existe
    if livro_atualizado.autor_id != livro_db.autor_id:
        autor = session.get(Autor, livro_atualizado.autor_id)
        if not autor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novo ID de Autor não encontrado.")

    livro_data = livro_atualizado.model_dump(exclude_unset=True)
    for key, value in livro_data.items():
        setattr(livro_db, key, value)
        
    session.add(livro_db)
    session.commit()
    session.refresh(livro_db)
    return livro_db

@app.delete("/livros/{id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_livro(id: int, session: Session = Depends(get_session)):
    livro = session.get(Livro, id)
    if not livro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado")
    
    session.delete(livro)
    session.commit()
    return None