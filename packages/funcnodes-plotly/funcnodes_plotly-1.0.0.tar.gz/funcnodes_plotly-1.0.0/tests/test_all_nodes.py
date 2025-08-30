from all_nodes_test_base import TestAllNodesBase
import funcnodes_plotly as fnp
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os
import unittest
import funcnodes_images
from funcnodes import NoValue
from funcnodes_core import testing

PLOT = False
if PLOT:

    def plot(fig, name):
        basepath = os.path.join(os.path.dirname(__file__), "imaged")
        if not os.path.exists(basepath):
            os.makedirs(basepath)
        fig.write_image(os.path.join(basepath, f"{name}.png"))
else:

    def plot(fig, name):
        pass


tn = [
    "funcnodes_plotly.figure.Add trace to figureNode",
    "funcnodes_plotly.figure.PlotNode",
    "funcnodes_plotly.figure.To jsonNode",
]


class TestExpressNodes(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        testing.setup()

    async def test_express_xy(self):
        df = pd.DataFrame(
            {
                "A": [1, 2, 3, 4, 5],
                "B": [5, 4, 3, 2, 1],
                "C": [1, 3, 5, 3, 1],
                "D": [1, 2, 3, 2, 1],
            }
        )

        for nodeclass in [
            fnp.express.scatter,
            fnp.express.line,
            fnp.express.bar,
            fnp.express.area,
            fnp.express.funnel,
        ]:
            node = nodeclass()
            node.inputs["data"].value = df
            node.inputs["x"].value = "A"
            node.inputs["y"].value = "B"

            await node
            out = node.get_output("figure").value
            self.assertIsInstance(out, go.Figure)
            self.assertEqual(
                node.inputs["x"].value_options["options"], [NoValue, "A", "B", "C", "D"]
            )
            plot(out, node.node_id)

    async def test_express_timeline(self):
        node = fnp.express.timeline()
        node.inputs["data"].value = pd.DataFrame(
            [
                dict(Task="Job A", Start="2009-01-01", Finish="2009-02-28"),
                dict(Task="Job B", Start="2009-03-05", Finish="2009-04-15"),
                dict(Task="Job C", Start="2009-02-20", Finish="2009-05-30"),
            ]
        )

        node.inputs["x_start"].value = "Start"
        node.inputs["x_end"].value = "Finish"
        node.inputs["y"].value = "Task"

        await node
        out = node.get_output("figure").value
        self.assertIsInstance(out, go.Figure)
        plot(out, node.node_id)

    async def test_express_pie(self):
        node = fnp.express.pie()

        node.inputs["data"].value = pd.DataFrame(
            {
                "labels": ["A", "B", "C", "D"],
                "values": [1, 2, 3, 4],
            }
        )
        node.inputs["names"].value = "labels"
        node.inputs["values"].value = "values"

        await node
        out = node.get_output("figure").value
        self.assertIsInstance(out, go.Figure)
        plot(out, node.node_id)

    async def test_express_tree_structure(self):
        for nodeclass in [
            fnp.express.sunburst,
            fnp.express.treemap,
            fnp.express.icicle,
        ]:
            node = nodeclass()

            node.inputs["data"].value = pd.DataFrame(
                {
                    "ids": ["A", "B", "C", "D", "E"],
                    "labels": [1, 2, 1, 5, 2],
                    "parents": ["", "A", "B", "C", "C"],
                }
            )

            node.inputs["names"].value = "ids"
            node.inputs["values"].value = "labels"
            node.inputs["parents"].value = "parents"

            await node
            out = node.get_output("figure").value
            self.assertIsInstance(out, go.Figure)
            plot(out, node.node_id)

    async def test_express_funnel_area(self):
        node = fnp.express.funnel_area()

        node.inputs["data"].value = pd.DataFrame(
            {
                "stage": ["A", "B", "C", "D"],
                "value": [1, 2, 3, 4],
            }
        )

        node.inputs["names"].value = "stage"
        node.inputs["values"].value = "value"

        await node
        out = node.get_output("figure").value
        self.assertIsInstance(out, go.Figure)
        plot(out, node.node_id)

    async def test_express_histogram(self):
        node = fnp.express.histogram()

        node.inputs["data"].value = pd.DataFrame(
            {
                "A": [1, 2, 3, 4, 5],
                "B": [5, 4, 3, 2, 1],
                "C": [1, 3, 5, 3, 1],
                "D": [1, 2, 3, 2, 1],
            }
        )

        node.inputs["x"].value = "A"

        await node
        out = node.get_output("figure").value
        self.assertIsInstance(out, go.Figure)
        plot(out, node.node_id)

    async def test_expressdist(self):
        for nodeclass in [fnp.express.box, fnp.express.violin, fnp.express.strip]:
            node = nodeclass()

            node.inputs["data"].value = pd.DataFrame(
                {
                    "A": [1, 2, 3, 4, 5],
                    "B": [5, 4, 3, 2, 1],
                    "C": [1, 3, 5, 3, 1],
                    "D": [1, 2, 3, 2, 1],
                }
            )

            node.inputs["x"].value = "A"
            node.inputs["y"].value = "B"

            await node
            out = node.get_output("figure").value
            self.assertIsInstance(out, go.Figure)

    async def test_express_ecdf(self):
        node = fnp.express.ecdf()

        node.inputs["data"].value = pd.DataFrame(
            {
                "A": [1, 2, 3, 4, 5],
                "B": [5, 4, 3, 2, 1],
                "C": [1, 3, 5, 3, 1],
                "D": [1, 2, 3, 2, 1],
            }
        )

        node.inputs["x"].value = "A"

        await node
        out = node.get_output("figure").value
        self.assertIsInstance(out, go.Figure)
        plot(out, node.node_id)

    async def test_express_density(self):
        for nodeclass in [fnp.express.density_heatmap, fnp.express.density_contour]:
            node = nodeclass()

            node.inputs["data"].value = pd.DataFrame(
                {
                    "A": [1, 2, 3, 4, 5],
                    "B": [5, 4, 3, 2, 1],
                    "C": [1, 3, 5, 3, 1],
                    "D": [1, 2, 3, 2, 1],
                }
            )

            node.inputs["x"].value = "A"
            node.inputs["y"].value = "B"

            await node
            out = node.get_output("figure").value
            self.assertIsInstance(out, go.Figure, f"nodeclass={nodeclass}")
            plot(out, node.node_id)

    async def test_express_image(self):
        node = fnp.express.imshow()

        node.inputs["data"].value = np.random.rand(200, 200).reshape(200, 200)

        await node
        out = node.get_output("figure").value
        self.assertIsInstance(out, go.Figure)
        plot(out, node.node_id)

    async def test_express_3d(self):
        for nodeclass in [fnp.express.scatter_3d, fnp.express.line_3d]:
            node = nodeclass()

            node.inputs["data"].value = pd.DataFrame(
                {
                    "A": [1, 2, 3, 4, 5],
                    "B": [5, 4, 3, 2, 1],
                    "C": [1, 3, 5, 3, 1],
                    "D": [1, 2, 3, 2, 1],
                }
            )

            node.inputs["x"].value = "A"
            node.inputs["y"].value = "B"
            node.inputs["z"].value = "C"

            await node
            out = node.get_output("figure").value
            self.assertIsInstance(out, go.Figure)
            plot(out, node.node_id)

    async def test_express_matrix(self):
        node = fnp.express.scatter_matrix()

        node.inputs["data"].value = pd.DataFrame(
            {
                "A": [1, 2, 3, 4, 5],
                "B": [5, 4, 3, 2, 1],
                "C": [1, 3, 5, 3, 1],
                "D": [1, 2, 3, 2, 1],
            }
        )

        await node
        out = node.get_output("figure").value
        self.assertIsInstance(out, go.Figure)
        plot(out, node.node_id)

    async def test_express_parallel(self):
        for nodeclass in [
            fnp.express.parallel_coordinates,
            fnp.express.parallel_categories,
        ]:
            node = nodeclass()

            node.inputs["data"].value = pd.DataFrame(
                {
                    "A": [1, 2, 3, 4, 5],
                    "B": [5, 4, 3, 2, 1],
                    "C": [1, 3, 5, 3, 1],
                    "D": [1, 2, 3, 2, 1],
                }
            )

            await node
            out = node.get_output("figure").value
            self.assertIsInstance(out, go.Figure)
            plot(out, node.node_id)

    async def test_express_polar(self):
        for nodeclass in [
            fnp.express.scatter_polar,
            fnp.express.line_polar,
            fnp.express.bar_polar,
        ]:
            node = nodeclass()

            node.inputs["data"].value = pd.DataFrame(
                {
                    "A": [1, 2, 3, 4, 5],
                    "B": [5, 4, 3, 2, 1],
                    "C": [1, 3, 5, 3, 1],
                    "D": [1, 2, 3, 2, 1],
                }
            )

            node.inputs["r"].value = "A"
            node.inputs["theta"].value = "B"

            await node
            out = node.get_output("figure").value
            self.assertIsInstance(out, go.Figure)
            plot(out, node.node_id)

    async def test_express_ternary(self):
        for nodeclass in [fnp.express.scatter_ternary, fnp.express.line_ternary]:
            node = nodeclass()

            node.inputs["data"].value = pd.DataFrame(
                {
                    "A": [1, 2, 3, 4, 5],
                    "B": [5, 4, 3, 2, 1],
                    "C": [1, 3, 5, 3, 1],
                    "D": [1, 2, 3, 2, 1],
                }
            )

            node.inputs["a"].value = "A"
            node.inputs["b"].value = "B"
            node.inputs["c"].value = "C"

            await node
            out = node.get_output("figure").value
            self.assertIsInstance(out, go.Figure)
            plot(out, node.node_id)

    async def test_express_dictionary_data(self):
        node = fnp.express.plot_multidata()

        node.inputs["data"].value = {
            "A": [1, 2, 3, 4, 5],
            "B": [5, 4, 3, 2, 1],
            "C": [1, 3, 5, 3, 1],
            "D": [1, 2, 3, 2, 1],
        }

        node.inputs["x"].value = "A"

        await node
        out = node.get_output("figure").value
        self.assertIsInstance(out, go.Figure)
        self.assertEqual(
            node.inputs["x"].value_options["options"], ["index", "A", "B", "C", "D"]
        )
        plot(out, node.node_id)


class TestPlotlyNodes(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        testing.setup()

    async def test_make_scatter_plot(self):
        node = fnp.plots.make_scatter()

        node.inputs["y"].value = [1, 2, 3, 4, 5]

        await node
        out = node.get_output("trace").value

        self.assertIsInstance(out, go.Scatter)

    async def test_make_bar_plot(self):
        node = fnp.plots.make_bar()

        node.inputs["y"].value = [1, 2, 3, 4, 5]

        await node
        out = node.get_output("trace").value

        self.assertIsInstance(out, go.Bar)

    async def test_make_heatmap_plot(self):
        node = fnp.plots.make_heatmap()

        node.inputs["z"].value = np.random.rand(10, 10)

        await node
        out = node.get_output("trace").value

        self.assertIsInstance(out, go.Heatmap)

    # layout

    async def test_label_axis(self):
        node = fnp.layout.label_axis()

        node.inputs["fig"].value = go.Figure()
        node.inputs["label"].value = "test"
        await node
        out = node.get_output("out").value

        self.assertIsInstance(out, go.Figure)
        self.assertEqual(out.layout.xaxis.title.text, "test")

    async def test_title(self):
        node = fnp.layout.title()

        node.inputs["fig"].value = go.Figure()
        node.inputs["title"].value = "test"
        await node
        out = node.get_output("out").value

        self.assertIsInstance(out, go.Figure)
        self.assertEqual(out.layout.title.text, "test")

    # region figure

    async def test_make_figure(self):
        node = fnp.figure.make_figure()

        await node
        out = node.get_output("out").value

        self.assertIsInstance(out, go.Figure)

    async def test_add_trace(self):
        node = fnp.figure.add_trace()

        node.inputs["figure"].value = go.Figure()
        node.inputs["trace"].value = go.Scatter()
        await node
        out = node.get_output("new figure").value

        self.assertIsInstance(out, go.Figure)

    async def test_plot(self):
        node = fnp.figure.plot()

        node.inputs["figure"].value = go.Figure()
        await node
        out = node.get_output("out").value

        self.assertIsInstance(out, go.Figure)

    async def test_to_json(self):
        node = fnp.figure.to_json()

        node.inputs["figure"].value = go.Figure()
        await node
        out = node.get_output("out").value

        self.assertIsInstance(out, dict)

    async def test_to_img(self):
        node = fnp.figure.to_img()

        node.inputs["figure"].value = go.Figure()
        await node
        out = node.get_output("img").value

        self.assertIsInstance(out, funcnodes_images.PillowImageFormat)

    # endregion figure


class TestAllNodes(TestAllNodesBase):
    sub_test_classes = [TestExpressNodes, TestPlotlyNodes]
