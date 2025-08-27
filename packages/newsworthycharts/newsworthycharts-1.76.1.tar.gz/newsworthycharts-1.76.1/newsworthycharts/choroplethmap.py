"""
Simple choropleths for common administrative areas
"""
from .map import Map
import geopandas as gpd
import numpy as np
import pandas as pd
import mapclassify
import matplotlib as mpl
import matplotlib.patches as mpatches
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


class ChoroplethMap(Map):
    """Plot a dataset on a coropleth map

    Data should be an iterables of (region, value) tuples, eg:
    `[("SE-8", 2), ("SE-9", 2.3)]`
    Newsworthy region names are also supported:
    `[("Stockholms kommun", 2), ("Solna kommun", 2.3)]`
    Note that unlike many other chart types, this one only allows
    a single dataset to be plotted, and the data is hence provided
    as a single iterable, rather than a list of iterables.
    """

    _uses_categorical_data = True

    def __init__(self, *args, **kwargs):
        super(ChoroplethMap, self).__init__(*args, **kwargs)
        self.label_order = kwargs.get("label_order", None)

    def _add_data(self):

        df = self._prepare_map_data()

        missing_color = "gainsboro"
        if self.missing_color:
            missing_color = self.missing_color

        args = {
            "categorical": True,
            "legend": True,  # bug in geopandas, fixed in master but not released
            "legend_kwds": {
                "loc": "upper left",
                "bbox_to_anchor": (1.05, 1.0),
            },
            "edgecolor": "white",
            "linewidth": 0.2,
            "missing_kwds": {
                "color": missing_color,
            },
        }
        # This should be adjusted per basemap
        label_kwargs = {
            "bbox_to_anchor": (0.92, 0.95),
            "loc": "upper left",
        }

        patches = []  # for legend
        if not self.categorical and self.use_bins is False:
            # We can not provide vmin/vmax to geopandas, so we need to
            # normalize the data ourselves, otherwise the inset maps will be off
            norm = mpl.colors.Normalize(vmin=df["data"].min(), vmax=df["data"].max())
            mapper = mpl.cm.ScalarMappable(norm=norm, cmap=self.color_ramp)
            df["color"] = df["data"].apply(lambda x: mapper.to_rgba(x) if not np.isnan(x) else missing_color)
            df["color"] = df["color"].fillna(missing_color)
            args["color"] = df["color"]

            self._fig.tight_layout()
            fmt = self._get_value_axis_formatter()
            cax = inset_axes(
                self.ax,
                width=0.1,
                height=2,  # 2 tum = 200 px vid 100 dpi
                loc='upper right',
                borderpad=0.1,
                # formatter
            )
            cb = self._fig.colorbar(
                mapper,
                cax=cax,
                format=mpl.ticker.FuncFormatter(fmt),
                drawedges=False,
                shrink=0.9,
                # use_gridspec=False,
                # pad=0.1,
            )
            # args["legend_kwds"]["pad"] = 0.15
            # args["legend_kwds"]["location"] = "left"

            if self.legend_title:
                cb.set_label(self.legend_title)
                self.legend_title = None
            """
            _min = df["data"].min()
            _max = df["data"].max()
            _median = df["data"].median()
            fmt = self._get_value_axis_formatter()
            patches.append(mpatches.Patch(color=mapper.to_rgba(_min), label=fmt(_min)))
            if _median != _min and _median != _max:
                patches.append(mpatches.Patch(color=mapper.to_rgba(_median), label=fmt(_median)))
            if _max != _min:
                patches.append(mpatches.Patch(color=mapper.to_rgba(_max), label=fmt(_max)))
            """

        elif not self.categorical:
            # mapclassify doesn't work well with nan values,
            # but we to keep them for plotting, hence
            # this hack with cutting out nan's and re-pasting them below
            _has_value = df[~df["data"].isna()].copy()
            if not pd.to_numeric(_has_value['data'], errors='coerce').notnull().all():
                # We can't bin non-numeric data
                raise ValueError("Data must be numeric")
            binning = mapclassify.classify(
                np.asarray(_has_value["data"]),  # .astype("category")
                self.binning_method,
                k=self.bins
            )
            values = pd.Categorical.from_codes(
                binning.yb,
                categories=binning.bins,
                ordered=True
            )
            _has_value["cats"] = values

            # df["data"] = pd.merge(_has_value, df, on="id", how="right")["cats"]
            _dict = _has_value[["id", "cats"]].set_index("id").to_dict()
            df["data"] = df["id"].map(_dict["cats"])

            # args["column"] = "data"
            # args["cmap"] = self.color_ramp
            # We can not provide vmin/vmax to geopandas, so we need to
            # normalize the data ourselves, otherwise the inset maps will be off
            norm = mpl.colors.Normalize(vmin=_has_value["data"].min(), vmax=_has_value["data"].max())
            mapper = mpl.cm.ScalarMappable(norm=norm, cmap=self.color_ramp)
            df["color"] = df["data"].apply(lambda x: mapper.to_rgba(x) if not np.isnan(x) else missing_color)
            df["color"] = df["color"].fillna(missing_color)
            args["color"] = df["color"]

            # Add labels legend (manually, Geopandas is too crude as of now)
            fmt = self._get_value_axis_formatter()
            for idx, cat in enumerate(binning.bins):
                # cat is the upper limit of each category
                if binning.counts[idx] == 1:
                    txt_val = fmt(cat)
                elif idx == 0:
                    if self.units == "number":
                        txt_val = f"–{fmt(cat)}"
                    else:
                        txt_val = f"– {fmt(cat)}"
                else:
                    if self.units == "number":
                        txt_val = f"{fmt(binning.bins[idx - 1])}–{fmt(cat)}"
                    else:
                        txt_val = f"{fmt(binning.bins[idx - 1])} – {fmt(cat)}"
                patches.append(mpatches.Patch(color=mapper.to_rgba(cat), label=txt_val))

        elif self.categorical:
            # We'll categorize manually further down the line,
            # to easier implement custom coloring
            # df["data"] = pd.Categorical(
            #     df["data"],
            #     ordered=True,
            # )

            cat = df[~df["data"].isna()]["data"].astype(str).unique()
            args["categories"] = cat
            if self.colors:
                color_map = self.colors
            else:
                color_map = {}
                if len(cat) > len(self._nwc_style["qualitative_colors"]):
                    raise ValueError(
                        "Too many categories for the available colors in the current style. " +  # noqa:W504
                        "Add a custom color map, or use a style with more categorical colors!"
                    )
                for idx, cat in enumerate(cat):
                    color_map[cat] = self._nwc_style["qualitative_colors"][idx]
            df["color"] = df["data"].astype(str).map(color_map)
            df["color"] = df["color"].fillna(missing_color)
            args["color"] = df["color"]

            # Geopandas does not handle legend if color keyword is used
            # We need to add it ourselves
            label_order = self.label_order or color_map.keys()
            for label in reversed(label_order):
                if label not in color_map:
                    if str(label) in color_map:
                        label = str(label)
                    else:
                        continue
                color = color_map[label]
                # A bit of an hack:
                # Check if this corresponds to one of our predefined
                # color names:
                if f"{color}_color" in self._nwc_style:
                    color = self._nwc_style[f"{color}_color"]
                patch = mpatches.Patch(color=color, label=label)
                patches.append(patch)
        patches = list(reversed(patches))
        if self.missing_label and len(patches):
            patches.append(mpatches.Patch(color=missing_color, label=self.missing_label))

        df.plot(ax=self.ax, **args)
        # Add outer edge
        gpd.GeoSeries(df.union_all()).plot(
            ax=self.ax,
            edgecolor="lightgrey",
            linewidth=0.2,
            facecolor="none",
            color="none",
        )

        self.ax.axis("off")
        for inset in self.insets:
            if "prefix" in inset:
                _df = df[df["id"].str.startswith(inset["prefix"])].copy()
            else:
                _df = df[df["id"].isin(inset["list"])].copy()
            if _df["data"].isnull().all():
                # Skip if no data
                continue

            args["color"] = _df["color"]
            args["legend"] = False
            axin = self.ax.inset_axes(inset["axes"])
            gpd.GeoSeries(_df.union_all()).plot(
                ax=axin,
                edgecolor="lightgrey",
                linewidth=0.3,
                facecolor="none",
            )
            axin.axis('off')
            _df.plot(
                ax=axin,
                **args,
            )
            artist = self.ax.indicate_inset_zoom(axin)
            for _line in artist.connectors:
                _line.set_visible(False)

        if len(patches):
            self.ax.legend(
                handles=patches,
                **label_kwargs,
            )
        # self.ax.get_figure().savefig("TST.png", bbox_inches="tight")
        self.df = df
