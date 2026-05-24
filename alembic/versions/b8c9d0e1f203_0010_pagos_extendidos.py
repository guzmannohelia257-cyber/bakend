"""0010_pagos_extendidos

Pagos Fase 1 y 3 del segundo parcial:
  - incidente.monto_preautorizacion + stripe_preauth_id: el cliente
    reserva (no cobra) el monto estimado antes de buscar taller.
  - pago.tipo (servicio|penalizacion|preauth): permite distinguir el
    pago de servicio normal del cobro de penalizacion y del reservado
    inicial. Sirve para reportes y para evitar duplicados.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b8c9d0e1f203"
down_revision: Union[str, None] = "a7b8c9d0e1f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "incidente",
        sa.Column("monto_preautorizacion", sa.Numeric(10, 2), nullable=True),
    )
    op.add_column(
        "incidente",
        sa.Column("stripe_preauth_id", sa.String(length=100), nullable=True),
    )

    op.add_column(
        "pago",
        sa.Column(
            "tipo",
            sa.String(length=20),
            nullable=False,
            server_default="servicio",
        ),
    )
    op.create_check_constraint(
        "chk_pago_tipo",
        "pago",
        "tipo IN ('servicio','penalizacion','preauth')",
    )


def downgrade() -> None:
    op.drop_constraint("chk_pago_tipo", "pago", type_="check")
    op.drop_column("pago", "tipo")
    op.drop_column("incidente", "stripe_preauth_id")
    op.drop_column("incidente", "monto_preautorizacion")
