from enum import StrEnum

from ..abstract import MitMVisualizationsCreator
from .dashboards import MitMBaselineDashboard


class MitMVisualizationType(StrEnum):
    Baseline = 'mitm-baseline'


mitm_visualization_creators: dict[MitMVisualizationType, type[MitMVisualizationsCreator]] = {
    MitMVisualizationType.Baseline: MitMVisualizationsCreator.wrap_dashboard_creator(
        MitMVisualizationType.Baseline, MitMBaselineDashboard
    ),
}
