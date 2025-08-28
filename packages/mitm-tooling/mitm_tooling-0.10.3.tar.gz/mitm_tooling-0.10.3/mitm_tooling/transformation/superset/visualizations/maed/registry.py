from enum import StrEnum

from ..abstract import MitMVisualizationsCreator
from .dashboards import BaselineMAEDDashboard, CustomChartMAEDDashboard, ExperimentalMAEDDashboard


class MAEDVisualizationType(StrEnum):
    Baseline = 'maed-baseline'
    Experimental = 'maed-experimental'
    CustomChart = 'maed-custom-chart'


maed_visualization_creators: dict[MAEDVisualizationType, type[MitMVisualizationsCreator]] = {
    MAEDVisualizationType.Baseline: MitMVisualizationsCreator.wrap_dashboard_creator(
        MAEDVisualizationType.Baseline, BaselineMAEDDashboard
    ),
    MAEDVisualizationType.Experimental: MitMVisualizationsCreator.wrap_dashboard_creator(
        MAEDVisualizationType.Experimental, ExperimentalMAEDDashboard
    ),
    MAEDVisualizationType.CustomChart: MitMVisualizationsCreator.wrap_dashboard_creator(
        MAEDVisualizationType.CustomChart, CustomChartMAEDDashboard
    ),
}
