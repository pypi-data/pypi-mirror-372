import numpy as np


class TableWriter:
    def __init__(self, data, index=None, cell_styles=None, max_rows=10):
        self.data = data
        self.max_rows = max_rows

        if type(data).__name__ == "DataFrame":
            if cell_styles is None:
                self.html = data.head(max_rows)._repr_html_()
            else:
                self.html = data.head(max_rows).style.apply(cell_styles)._repr_html_()
            return

        values = self._unwrap_np_dict(data)

        if index is None:
            self.index = range(0, max_rows)
        else:
            self.index = index
            if len(self.index) != len(values):
                raise ValueError(f"Index is not the same size as your data: got {len(self.index)} for data size {len(values)}")

        self.cell_styles = cell_styles

        self.header = f"""
            <thead>
                <tr>
                    {''.join(['<th></th>'] + [f'<th>{col}</th>' for col in data.keys()])}
                </tr>
            </thead>
        """
        self.body = f"""
            <tbody>
                {self.pp_tr(values)}
            </tbody>

        """
        self.html = f"<table>{self.header}{self.body}</table>"

    @staticmethod
    def _nd_len(np_dict):
        return len(np_dict[list(np_dict.keys())[0]])

    @staticmethod
    def _unwrap_np_dict(data):
        # Transpose to ensure we are oriented row-wise
        return np.array([data[col] for col in data.keys()]).T

    def pp_tr(self, values):
        index = self.index

        if len(values) > self.max_rows:
            values = values[:self.max_rows]
            index = self.index[:self.max_rows]

        return ''.join([f'<tr>{self.pp_td(idx, row)}</tr>'
                        for idx, row in zip(index, values)])

    def pp_td(self, idx, row):
        idx_cell = f'<td style="font-weight: bold">{idx}</td>'

        def get_style(cell_idx):
            basic_style = "white-space: nowrap; overflow: hidden; text-overflow: ellipsis;max-width: 30em"
            if self.cell_styles is None:
                return basic_style

            row_cell_styles = self.cell_styles[self.index.index(idx)]
            return row_cell_styles[cell_idx] + ";" + basic_style

        return ''.join([idx_cell] + [f'<td style="{get_style(cell_idx)}">{val:.5f}</td>' if isinstance(val, float) else f'<td style="{get_style(cell_idx)}">{val}</td>' for cell_idx, val in enumerate(row)])

    def _repr_html_(self):
        return self.html
