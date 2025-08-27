from lightningchart.themes import Themes, Color
import lightningchart.utils as utils

from lightningchart.charts.chart_xy import ChartXY
from lightningchart.charts.chart_3d import Chart3D
from lightningchart.charts.polar_chart import PolarChart
from lightningchart.charts.bar_chart import BarChart
from lightningchart.charts.spider_chart import SpiderChart
from lightningchart.charts.gauge_chart import GaugeChart
from lightningchart.charts.pie_chart import PieChart
from lightningchart.charts.funnel_chart import FunnelChart
from lightningchart.charts.pyramid_chart import PyramidChart
from lightningchart.charts.treemap_chart import TreeMapChart
from lightningchart.charts.map_chart import MapChart
from lightningchart.charts.dashboard import Dashboard
from lightningchart.charts.parallel_coordinate_chart import ParallelCoordinateChart


def set_license(license_key: str, license_information: dict[str, str] = None):
    from lightningchart import conf
    conf.LICENSE_KEY = license_key
    if license_information:
        conf.LICENSE_INFORMATION = license_information
