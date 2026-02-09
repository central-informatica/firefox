from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import date
from backend.app.db.models import Feriados
from backend.app.schemas.feriados import FeriadoCreate, FeriadoUpdate, FeriadosReplicar, FeriadosImportarPadroes


# Feriados nacionais brasileiros (recorrentes)
FERIADOS_NACIONAIS = [
    {"dia": 1, "mes": 1, "nome": "Confraternização Universal"},
    {"dia": 21, "mes": 4, "nome": "Tiradentes"},
    {"dia": 1, "mes": 5, "nome": "Dia do Trabalho"},
    {"dia": 7, "mes": 9, "nome": "Independência do Brasil"},
    {"dia": 12, "mes": 10, "nome": "Nossa Senhora Aparecida"},
    {"dia": 2, "mes": 11, "nome": "Finados"},
    {"dia": 15, "mes": 11, "nome": "Proclamação da República"},
    {"dia": 25, "mes": 12, "nome": "Natal"},
]


class CRUDFeriados:

    def listar(self, db: Session):
        return db.query(Feriados).all()

    def get(self, db: Session, feriado_id: str):
        feriado = db.query(Feriados).filter(Feriados.feriado_id == feriado_id).first()
        if not feriado:
            raise HTTPException(404, "Feriado não encontrado")
        return feriado

    def criar(self, db: Session, data: FeriadoCreate):

        # Evitar duplicidade caso não seja recorrente
        existente = db.query(Feriados).filter(
            Feriados.data == data.data
        ).first()

        if existente:
            raise HTTPException(400, "Já existe um feriado cadastrado nesta data.")

        novo = Feriados(
            data=data.data,
            nome=data.nome,
            recorrente=data.recorrente,
            empresa_id=data.empresa_id,
        )

        db.add(novo)
        db.commit()
        db.refresh(novo)
        return novo

    def atualizar(self, db: Session, feriado_id: str, data: FeriadoUpdate):
        feriado = self.get(db, feriado_id)

        updates = data.dict(exclude_unset=True)

        # Se a data está sendo alterada, verificar duplicidade
        if "data" in updates:
            existe = db.query(Feriados).filter(
                Feriados.data == updates["data"],
                Feriados.feriado_id != feriado_id
            ).first()

            if existe:
                raise HTTPException(400, "Já existe um feriado nesta nova data.")

        for campo, valor in updates.items():
            setattr(feriado, campo, valor)

        db.commit()
        db.refresh(feriado)
        return feriado

    def deletar(self, db: Session, feriado_id: str):
        feriado = self.get(db, feriado_id)
        db.delete(feriado)
        db.commit()
        return {"status": "deleted"}

    def replicar(self, db: Session, data: FeriadosReplicar):
        """Replica feriados selecionados para outras empresas."""
        criados = []
        erros = []

        # Buscar feriados de origem
        feriados_origem = db.query(Feriados).filter(
            Feriados.feriado_id.in_([str(fid) for fid in data.feriado_ids])
        ).all()

        if not feriados_origem:
            raise HTTPException(404, "Nenhum feriado encontrado para replicar")

        for empresa_id in data.empresa_ids_destino:
            for feriado in feriados_origem:
                # Verificar se já existe feriado com mesma data na empresa destino
                existente = db.query(Feriados).filter(
                    Feriados.empresa_id == str(empresa_id),
                    Feriados.data == feriado.data
                ).first()

                if existente:
                    erros.append(f"Feriado '{feriado.nome}' já existe na empresa {empresa_id}")
                    continue

                novo = Feriados(
                    data=feriado.data,
                    nome=feriado.nome,
                    recorrente=feriado.recorrente,
                    empresa_id=str(empresa_id),
                )
                db.add(novo)
                criados.append(novo)

        if criados:
            db.commit()
            for f in criados:
                db.refresh(f)

        return {
            "criados": criados,
            "total_criados": len(criados),
            "erros": erros if erros else None
        }

    def importar_padroes(self, db: Session, data: FeriadosImportarPadroes):
        """Importa feriados nacionais padrões para uma empresa."""
        ano = data.ano or date.today().year
        criados = []
        erros = []

        for feriado_info in FERIADOS_NACIONAIS:
            data_feriado = date(ano, feriado_info["mes"], feriado_info["dia"])

            # Verificar se já existe
            existente = db.query(Feriados).filter(
                Feriados.empresa_id == str(data.empresa_id),
                Feriados.data == data_feriado
            ).first()

            if existente:
                erros.append(f"Feriado '{feriado_info['nome']}' ({data_feriado}) já existe")
                continue

            novo = Feriados(
                data=data_feriado,
                nome=feriado_info["nome"],
                recorrente=True,
                empresa_id=str(data.empresa_id),
            )
            db.add(novo)
            criados.append(novo)

        if criados:
            db.commit()
            for f in criados:
                db.refresh(f)

        return {
            "criados": criados,
            "total_criados": len(criados),
            "erros": erros if erros else None
        }

    def listar_padroes(self):
        """Lista os feriados nacionais padrões disponíveis."""
        return FERIADOS_NACIONAIS


crud_feriados = CRUDFeriados()
