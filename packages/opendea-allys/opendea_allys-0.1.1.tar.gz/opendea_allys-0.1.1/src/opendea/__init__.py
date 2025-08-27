# --- plotting (submódulo) ---
from . import plotting

# --- duais ---
from .dual import (
    dea_bcc_input_dual,
    dea_bcc_output_dual,
    dea_ccr_input_dual,
    dea_ccr_output_dual,
)

# --- primais ---
from .models import (
    dea_additive,
    dea_bcc_input,
    dea_bcc_output,
    dea_ccr_input,
    dea_ccr_output,
    super_eff_bcc_input,
    super_eff_bcc_output,
    # Super-efficiency
    super_eff_ccr_input,
    super_eff_ccr_output,
)

# --- utils ---
from .utils import (
    peers_from_lambdas,
    projections,
    standardize_primal_output,
)
from .version import __version__

# ===========================
# Avançados (wrappers preguiçosos)
# ===========================
# Observação:
#   Não importamos de .advanced no topo para evitar ImportError durante a coleta de testes.
#   Em vez disso, definimos wrappers que importam a função real apenas quando chamados.


def dea_network_two_stage(*args, **kwargs):
    """Wrapper preguiçoso para opendea.advanced.dea_network_two_stage"""
    from .advanced import dea_network_two_stage as _impl

    return _impl(*args, **kwargs)


def dea_dynamic_carryover(*args, **kwargs):
    """Wrapper preguiçoso para opendea.advanced.dea_dynamic_carryover"""
    from .advanced import dea_dynamic_carryover as _impl

    return _impl(*args, **kwargs)


# Aliases públicos estáveis (se quiser manter no README/Quickstart)
ndea_two_stage_input = dea_network_two_stage
dynamic_dea_input = dea_dynamic_carryover


__all__ = [
    # primais
    "dea_ccr_input",
    "dea_bcc_input",
    "dea_ccr_output",
    "dea_bcc_output",
    "dea_additive",
    # super-eficiência
    "super_eff_ccr_input",
    "super_eff_bcc_input",
    "super_eff_ccr_output",
    "super_eff_bcc_output",
    # duais
    "dea_ccr_input_dual",
    "dea_bcc_input_dual",
    "dea_ccr_output_dual",
    "dea_bcc_output_dual",
    # avançados (nomes esperados pelos testes)
    "dea_network_two_stage",
    "dea_dynamic_carryover",
    # aliases “amigáveis”
    "ndea_two_stage_input",
    "dynamic_dea_input",
    # utils
    "standardize_primal_output",
    "projections",
    "peers_from_lambdas",
    # submódulo
    "plotting",
    # metadados
    "__version__",
]
