"""0016_comision_plataforma_pct

Agrega comision_plataforma_pct (% que la plataforma retiene de cada servicio) a
configuracion_plataforma. Antes la comision estaba fija en 10% en el codigo;
ahora es configurable por el super-admin.

Idempotente: solo agrega la columna si la tabla existe y la columna no.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c1d2e3f40016"
down_revision: Union[str, None] = "041523340c01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(bind, table: str, col: str) -> bool:
    insp = sa.inspect(bind)
    if not insp.has_table(table):
        return False
    return col in {c["name"] for c in insp.get_columns(table)}


def upgrade() -> None:
    bind = op.get_bind()
    if sa.inspect(bind).has_table("configuracion_plataforma") and not _has_column(
        bind, "configuracion_plataforma", "comision_plataforma_pct"
    ):
        op.add_column(
            "configuracion_plataforma",
            sa.Column(
                "comision_plataforma_pct",
                sa.Integer(),
                nullable=False,
                server_default="10",
            ),
        )


def downgrade() -> None:
    bind = op.get_bind()
    if _has_column(bind, "configuracion_plataforma", "comision_plataforma_pct"):
        op.drop_column("configuracion_plataforma", "comision_plataforma_pct")
