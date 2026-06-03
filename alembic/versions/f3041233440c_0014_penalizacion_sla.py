"""0014_penalizacion_sla

Anade tenant.pct_penalizacion_sla (default 15): porcentaje que se cobra al
taller cuando incumple el SLA de llegada (tiempo real > eta_minutos + 20 min
de tolerancia). Se aplica sobre el monto final del servicio. Configurable por
el admin del tenant.

Idempotente.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f3041233440c"
down_revision: Union[str, None] = "e2f30412330b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(bind, table: str, col: str) -> bool:
    return col in {c["name"] for c in sa.inspect(bind).get_columns(table)}


def upgrade() -> None:
    bind = op.get_bind()
    if not _has_column(bind, "tenant", "pct_penalizacion_sla"):
        op.add_column(
            "tenant",
            sa.Column(
                "pct_penalizacion_sla",
                sa.Integer(),
                nullable=False,
                server_default="15",
            ),
        )


def downgrade() -> None:
    op.drop_column("tenant", "pct_penalizacion_sla")
