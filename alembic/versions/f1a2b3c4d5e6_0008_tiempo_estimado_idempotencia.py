"""0008_tiempo_estimado_idempotencia

Cambios para el segundo parcial:
  - cotizacion.tiempo_estimado_min: cuanto tarda el taller en reparar.
  - asignacion.tiempo_estimado_reparacion_min: copia al aceptar la cotizacion.
  - incidente.idempotency_key + unique(id_usuario, idempotency_key):
    deduplica reintentos del modo offline (la app mobile/web manda el mismo
    UUID cuando recupera conexion).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, None] = "e3b2c9d41a77"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cotizacion",
        sa.Column("tiempo_estimado_min", sa.Integer(), nullable=True),
    )
    op.add_column(
        "asignacion",
        sa.Column(
            "tiempo_estimado_reparacion_min", sa.Integer(), nullable=True
        ),
    )
    op.add_column(
        "incidente",
        sa.Column("idempotency_key", sa.String(length=64), nullable=True),
    )
    op.create_index(
        "ix_incidente_idempotency_key",
        "incidente",
        ["idempotency_key"],
    )
    op.create_unique_constraint(
        "uq_incidente_usuario_idemkey",
        "incidente",
        ["id_usuario", "idempotency_key"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_incidente_usuario_idemkey", "incidente", type_="unique"
    )
    op.drop_index("ix_incidente_idempotency_key", table_name="incidente")
    op.drop_column("incidente", "idempotency_key")
    op.drop_column("asignacion", "tiempo_estimado_reparacion_min")
    op.drop_column("cotizacion", "tiempo_estimado_min")
