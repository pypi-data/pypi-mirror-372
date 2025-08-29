import svgwrite
import io
import matplotlib.colors as clr

from feyn._svgrenderer import layout_2d
from ._themes import Theme
from ._render import truncate_input_names


class RenderState:
    def __init__(self):
        self.x_loc = 0
        self.y_loc = 0
        self.heights = [0]
        self.widths = [0]

    def wrap(self):
        self.x_loc = 0
        self.y_loc = self.y_loc + self.current_row_height()
        self.heights = [0]

    def update_xloc(self, x):
        self.x_loc += x
        self.widths.append(self.x_loc)

    def update_height(self, y):
        self.heights.append(y)

    def current_row_height(self):
        return max(self.heights)

    def abs_max_width(self):
        return max(self.widths)


class SVGGraphToolkit:
    def __init__(self, auto_wrap_px=None):
        self.nodew = 90
        self.nodeh = 35
        self.margin = 20
        self.node_margin = 2

        self.auto_wrap_px = auto_wrap_px

        self.drawing = svgwrite.Drawing(profile="full")

        self.render_items = []

    def _repr_svg_(self):
        return self.render()

    def _repr_html_(self):
        return self.render()

    def render(self):
        drawing = svgwrite.Drawing(profile="full", size=(0, 0))

        state = RenderState()

        for item in self.render_items.copy():
            item_width = item.attribs["width"]
            item_height = item.attribs["height"]

            if item.attribs["class"] == "h_space":
                state.wrap()
            elif self.auto_wrap_px is not None:
                # If item is not already the first and the total is larger than max, wrap
                if state.x_loc > 0 and state.x_loc + item_width >= self.auto_wrap_px:
                    state.wrap()

            # Reposition the svg element w.r.t. state
            item.attribs["x"] = state.x_loc
            item.attribs["y"] = state.y_loc

            # TODO: Consider adding dynamic spacer objects
            drawing.add(item)
            state.update_xloc(item_width)
            state.update_height(item_height)

            if item.attribs["class"] == "h_space":
                state.wrap()

        f = io.StringIO()

        colorbar_correction = 5  # Sometimes the colorbar gets a little wonky.

        drawing.attribs["height"] = (
            state.y_loc + state.current_row_height() + colorbar_correction
        )
        drawing.attribs["width"] = state.abs_max_width()
        drawing.attribs["viewBox"] = (
            f'0 0 {drawing.attribs["width"]} {drawing.attribs["height"]}'
        )
        drawing.attribs["preserveAspectRatio"] = "none"
        drawing.write(f)
        return f.getvalue()

    def _add_txt(
        self,
        parent,
        content,
        insert,
        color="dark",
        font_size="medium",
        anchor="start",
        selectable=True,
        **kwargs,
    ):
        txt = self.drawing.text(
            content,
            insert=insert,
            fill=Theme.color(color),
            text_anchor=anchor,
            font_size=Theme.font_size(font_size),
            font_family="monospace",
            **kwargs,
        )
        if not selectable:
            txt.attribs["style"] = "pointer-events:none"
        parent.add(txt)

    def _add_bold_text(self, parent, text, start, end, insert=(0, 0), size="medium"):
        x_pos, y_pos = insert[0], insert[1]
        start_text = text[:start]
        end_text = text[end:]
        bold_part = text[start:end]
        txt = self.drawing.text(
            start_text,
            insert=(x_pos, y_pos),
            fill=Theme.color("dark"),
            text_anchor="start",
            font_size=Theme.font_size(size),
            font_family="monospace",
        )
        txt.add(self.drawing.tspan(bold_part, font_weight="bold"))
        txt.add(self.drawing.tspan(end_text))
        parent.add(txt)

    def add_horizontal_spacer(self, title="", size="large"):
        font_size = Theme.font_size(size)
        title_spacing = font_size + 5
        t_width = Theme._get_string_length(title, size=size)

        spacer = self.drawing.svg(insert=(0, 0), size=(t_width, title_spacing))
        spacer.attribs["class"] = "h_space"
        self._add_txt(
            spacer,
            title,
            insert=(0, font_size),
            font_size=font_size,
        )

        line = self.drawing.line(
            start=(0, title_spacing),
            end=(t_width, title_spacing),
            stroke=Theme.color("dark"),
        )
        spacer.add(line)

        self.render_items.append(spacer)
        return self

    def add_input_table(self, model):
        from ._render import isolate_interesting_regions

        self.add_horizontal_spacer(title="Inputs", size="large")
        inputs = model.inputs
        row_count = len(inputs)
        content_size = "medium"
        content_fontsize = Theme.font_size(content_size)
        text_spacing = content_fontsize + 4

        bottom_padding = 5
        boxh = row_count * text_spacing + bottom_padding
        boxw = max(
            [Theme._get_string_length(value, size=content_size) for value in inputs]
        )

        table = self.drawing.svg(insert=(0, 0), size=(boxw + self.margin, boxh))
        table.attribs["class"] = "table"

        text_indent = 5

        trunc_size = 8
        regions = isolate_interesting_regions(inputs, trunc_size=trunc_size, lb=3)

        entry_ix = 1  # 1 indexed for pixel reasons
        for idx, name in enumerate(inputs):
            entry_y = text_spacing * entry_ix
            if len(name) <= trunc_size:
                self._add_txt(
                    table,
                    name,
                    insert=(text_indent, entry_y),
                    font_size=content_size,
                )
            else:
                start = regions[idx]
                end = regions[idx] + trunc_size
                self._add_bold_text(
                    table,
                    name,
                    start,
                    end,
                    insert=(text_indent, entry_y),
                    size=content_size,
                )

            entry_ix += 1

        self.render_items.append(table)
        return self

    def add_summary_information(self, metrics, title="", short=False):
        summaryw = 160 if not short else 60
        font_size = Theme.font_size("large")
        text_spacing = font_size + 1
        title_spacing = font_size + 5
        summaryh = len(metrics) * text_spacing + title_spacing

        # Adjust header according to content size
        max_metric_width = max([len(f"{m:.3}") for m in metrics.values()])
        content_width = max(
            Theme._get_string_length(title, size="large"), max_metric_width * font_size
        )
        summaryw = max(summaryw, content_width)

        text_margin = 5

        summary = self.drawing.svg(
            insert=(0, 0), size=(summaryw + self.margin, summaryh)
        )
        summary.attribs["class"] = "summary"
        self._add_txt(summary, title, insert=(0, font_size), font_size=font_size)
        line = self.drawing.line(
            start=(0, title_spacing),
            end=(summaryw, title_spacing),
            stroke=Theme.color("dark"),
        )
        summary.add(line)

        # Draw summary information in rectangle
        m_ix = 0
        for name, metric in metrics.items():
            m_ix += 1  # 1 indexed for pixel reasons
            if not short:
                self._add_txt(
                    summary,
                    name,
                    insert=(text_margin, title_spacing + text_spacing * (m_ix)),
                    font_size=font_size,
                )
            self._add_txt(
                summary,
                f"{metric:.3}",
                insert=(summaryw - text_margin, title_spacing + text_spacing * (m_ix)),
                font_size=font_size,
                anchor="end",
            )

        self.render_items.append(summary)
        return self

    @staticmethod
    def _get_element_color(element):
        if element.name == "":
            return Theme.color("light"), Theme.color("accent")
        else:
            return Theme.color("highlight"), Theme.color("dark")

    def _add_colorbar(self, svg, label, color_text, cmap):
        bar_w = 50
        bar_h = 20

        svg.attribs["height"] += bar_h + 20  # Add offset
        w = svg.attribs["width"]
        h = svg.attribs["height"]
        colorbar_loc = (w / 2 - bar_w * 1.5, h - bar_h)

        bar_stops = len(color_text)
        gradient = Theme.cmap(cmap)
        norm = clr.Normalize(vmin=0, vmax=bar_stops - 1)

        for i in range(bar_stops):
            color = clr.rgb2hex(gradient(norm(i)))

            # Signal rect
            rect = self.drawing.rect(
                (colorbar_loc[0] + i * bar_w, colorbar_loc[1]),
                (bar_w, bar_h),
                fill=color,
                stroke_width=1,
            )
            svg.add(rect)

            # Text on signal
            self._add_txt(
                svg,
                color_text[i],
                insert=(
                    colorbar_loc[0] + i * bar_w + bar_w / 2,
                    colorbar_loc[1] + bar_h / 2 + 3,
                ),
                anchor="middle",
            )

        self._add_txt(
            svg,
            label,
            insert=(colorbar_loc[0] + bar_w * 1.5, colorbar_loc[1] - 5),
            anchor="middle",
        )

        return self

    def _add_loss_value(self, model, locs, svg):
        if model.loss_value is not None:
            loss_label = "Loss: %.2E" % (model.loss_value)
            loc = locs[0]  # Put this on the output node
            self._add_txt(
                svg,
                loss_label,
                insert=(loc[0] + self.nodew / 2, loc[1] + 1.4 * self.nodeh),
                anchor="middle",
            )
        return self

    def _add_label(self, label, height, svg):
        if label:
            label_margin = self.margin - 10
            self._add_txt(svg, label, insert=(0, height - label_margin))
        return self

    def _iter_nodes(self):
        for graph in self._iter_graphs():
            for elem in graph.elements:
                if "class" in elem.attribs and elem.attribs["class"] == "node":
                    yield graph, elem

    def _iter_graphs(self):
        for item in self.render_items:
            if item.attribs["class"] == "graph":
                yield item

    def color_nodes(self, by, crange=None, cmap="feyn-signal"):
        """Will color all nodes in all graphs currently to be rendered according to the values in 'by'.
           Normalizes the colors using the crange

        Arguments:
            by {list[int]} -- values to color by
            crange {list[int]} -- Range of values from which we'll take the min and max for normalization. Defaults to 'by' if not set.

        Returns:
            SVGGraphToolKit -- returns self
        """
        cmap = Theme.cmap(cmap)
        if crange is None:
            crange = by

        norm = clr.Normalize(vmin=min(crange), vmax=max(crange))

        node_ix = 0
        for _, node in self._iter_nodes():
            node.attribs["fill"] = clr.rgb2hex(cmap(norm(by[node_ix])))
            node.attribs["stroke"] = Theme.color("dark")
            node_ix += 1
        return self

    def label_nodes(self, labels):
        """Will label all nodes with the labels provided.

        Arguments:
            labels {list[Union(str, int)]} -- Must be a list of things that work as a label.

        Returns:
            SVGGraphToolKit -- returns self
        """
        node_ix = 0
        for model, node in self._iter_nodes():
            x = node.attribs["x"]
            y = node.attribs["y"]
            center = self.nodew / 2
            self._add_txt(
                model,
                labels[node_ix],
                insert=(x + center, y - 5),
                anchor="middle",
                font_size="small",
            )
            node_ix += 1
        return self

    def add_colorbars(
        self,
        label="Signal capture",
        color_text=["low", "mid", "high"],
        cmap="feyn-signal",
    ):
        """Will add a colorbar with the given label to all models currently to be rendered.

        Arguments:
            label {str} -- A label for the colorbars

        Returns:
            SVGGraphToolKit -- returns self
        """
        for graph in self._iter_graphs():
            self._add_colorbar(graph, label=label, color_text=color_text, cmap=cmap)
        return self

    def add_graph(self, model, label=None, show_loss=True, show_sources=False):
        """Adds a model to the SVG plot with all the nodes, edges and default colors.

        Arguments:
            model {feyn.Model} -- The model to plot

        Keyword Arguments:
            label {str} -- A label to show under the model (default: {None})
            show_loss {bool} -- Whether to display the loss (default: {True})
            show_sources {bool} -- Whether to display the source numbers for each node (default: {False})

        Returns:
            SVGGraphToolKit -- returns self
        """
        locs = layout_2d(model)

        # Move y values so the smallest is 0
        min_y = min([loc[1] for loc in locs])
        locs = [
            (1 + loc[0] * 120, (loc[1] - min_y) * 60 + 20) for loc in locs
        ]  # Magic numbers

        max_x = max([loc[0] for loc in locs])
        max_y = max([loc[1] for loc in locs])
        width = max_x + self.nodew + self.margin
        height = max_y + self.nodeh + self.margin * 2

        graph_svg = self.drawing.svg(insert=(0, 0), size=(width, height))
        graph_svg.attribs["class"] = "graph"

        if show_loss:
            self._add_loss_value(model, locs, graph_svg)
        if label:
            self._add_label(label, height, graph_svg)
            label_width = Theme._get_string_length(label)
            if width < label_width:
                graph_svg.attribs["width"] = label_width + self.margin

        trunc_inputs = truncate_input_names(model.inputs)
        for ix, elem in enumerate(model):
            loc = locs[ix]

            fill, stroke = self._get_element_color(elem)

            # The node rect + tooltip
            rect = self.drawing.rect(
                (loc[0], loc[1]),
                (self.nodew, self.nodeh),
                fill=fill,
                stroke=stroke,
                stroke_width=1,
            )
            tooltip = svgwrite.base.Title(elem.tooltip)
            rect.add(tooltip)
            rect.attribs["class"] = "node"
            graph_svg.add(rect)

            # The node text
            if elem.name in model.inputs:
                idx = model.inputs.index(elem.name)
                trunc_name = trunc_inputs[idx]
            elif elem.name == model.output:
                trunc_name = truncate_input_names([model.output])[0]
            else:
                trunc_name = elem.fname.split(":")[0]

            self._add_txt(
                graph_svg,
                trunc_name,
                insert=(loc[0] + self.nodew / 2, loc[1] + self.nodeh / 2 + 4),
                anchor="middle",
                selectable=False,
            )
            # The index markers
            self._add_txt(
                graph_svg,
                ix,
                insert=(loc[0] + self.nodew - self.node_margin, loc[1] + 9),
                anchor="end",
                font_size="small",
                selectable=False,
            )

            # The type text
            if elem.name != "":
                if elem.arity == 0:
                    if elem.fname == "in-linear:0":
                        type_text = "num"
                    else:
                        type_text = "cat"
                else:
                    if elem.fname == "out-lr:1":
                        type_text = "logistic"
                    elif elem.fname == "out-linear:1":
                        type_text = "linear"
                    else:
                        type_text = "out"

                self._add_txt(
                    graph_svg,
                    type_text,
                    insert=(loc[0] + self.node_margin, loc[1] + 9),
                    font_size="small",
                    selectable=False,
                )

            for ord, src_ix in enumerate(elem.children):
                src_loc = locs[src_ix]
                x0 = src_loc[0] + self.nodew
                y0 = src_loc[1] + self.nodeh / 2

                x1 = loc[0]
                y1 = loc[1] + self.nodeh / 2
                if elem.arity == 2:
                    y1 += (ord * 18) - 9

                # Connecting lines
                line = self.drawing.line((x0, y0), (x1, y1), stroke=Theme.color("dark"))
                graph_svg.add(line)

                if ix == 0:
                    # Output
                    continue

                # The ordinal markers
                if show_sources:
                    self._add_txt(
                        graph_svg,
                        f"x{ord}",
                        insert=(x1 + self.node_margin, y1 + 3),
                        font_size="small",
                        selectable=False,
                    )

        self.render_items.append(graph_svg)
        return self
