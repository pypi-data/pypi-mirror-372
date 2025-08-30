from io import BytesIO
from typing import Any
import math
import pkgutil
import tomllib
import warnings

from collections import Counter
from datetime import datetime
from openalex_analysis.data import WorksData
from openalex_analysis.plot import InstitutionsPlot
import flag
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

# bug fix: https://github.com/plotly/plotly.py/issues/3469
import plotly.io as pio
pio.kaleido.scope.mathjax = None


hal_doc_types_names_mapping = tomllib.load(BytesIO(pkgutil.get_data(__name__, "HAL_doc_types_names.toml")))


def get_hal_doc_type_name(name):
    if name in hal_doc_types_names_mapping.keys():
        return hal_doc_types_names_mapping[name]
    else:
        warnings.warn(f"Unknown HAL doc type name: {name}. Using raw name.")
        parts = name.split('_')
        return ' '.join([parts[0].capitalize()] + [part.lower() for part in parts[1:]])


# Calculate plot bar width depending on the number of bars on the plot, based on a linear interpolation of two examples
max_width = 0.7
n_bars_max_width = 10
example_width = 0.25
example_n_bars = 2
a = (max_width - example_width)/(n_bars_max_width - example_n_bars)
b = example_width - example_n_bars*(max_width - example_width)/(n_bars_max_width - example_n_bars)


def get_bar_width(n_bars: int) -> int | float:
    """
    Calculate the width of bars in a plot based on the number of bars.

    This function uses linear interpolation to determine the bar width based on the number of bars.
    The interpolation is based on two examples: one with 10 bars and a width of 0.7, and another with 2 bars and a width
    of 0.25.

    :param n_bars: Number of bars in the plot.
    :type n_bars: int
    :return: Width of the bars.
    :rtype: int | float
    """
    if n_bars >= n_bars_max_width:
        return max_width
    return a * n_bars + b


def dataframe_to_longtable(
        table_df,
        alignments: list | None = None,
        caption: str | None = None,
        label: str | None = None,
        vertical_lines: bool = True,
        classic_horizontal_lines: bool = False,
        minimal_horizontal_lines: bool = True,
        max_plotted_entities: int | None = None,
        output_file: str | None = None
) -> str:
    """
    Convert a pandas DataFrame to LaTeX longtable code without document headers.

    This function generates LaTeX code for a longtable from a pandas DataFrame. It handles various formatting options
    such as alignments, captions, labels, and lines between rows and columns.

    :param table_df: pandas DataFrame to convert.
    :type table_df: pd.DataFrame
    :param alignments: List of column alignments (e.g., ['l', 'c', 'r']).
    :type alignments: list | None, optional
    :param caption: Caption for the table.
    :type caption: str | None , optional
    :param label: Label for referencing the table.
    :type label: str | None, optional
    :param vertical_lines: Whether to include vertical lines between columns.
    :type vertical_lines: bool, optional
    :param classic_horizontal_lines: Whether to include horizontal lines between rows in a classic style.
    :type classic_horizontal_lines: bool, optional
    :param minimal_horizontal_lines: Whether to include minimal horizontal lines between rows.
    :type minimal_horizontal_lines: bool, optional
    :param max_plotted_entities: Maximum number of entities to show in the table. If None, show all entities in the
        table.
    :type max_plotted_entities: int | None, optional
    :param output_file: Path to file where the LaTeX code will be saved. If None, code is not saved to file.
    :type output_file: str | None, optional
    :return: LaTeX code for the longtable (without document headers).
    :rtype: str
    :raises AttributeError: If both classic_horizontal_lines and minimal_horizontal_lines are True.
    :raises ValueError: If the number of alignments does not match the number of columns.
    """
    def escape_latex(s: str) -> str:
        """
        Escape LaTeX special characters in a string.

        :param s: String to escape.
        :type s: str
        :return: Escaped string with LaTeX special characters.
        :rtype: str
        """
        if pd.isna(s):
            return ''
        s = str(s)
        replacements = {
            '&': '\\&',
            '%': '\\%',
            '$': '\\$',
            '#': '\\#',
            '_': '\\_',
            # '{': '\\{',
            # '}': '\\}',
            # '~': '\\textasciitilde{}',
            # '^': '\\textasciicircum{}',
            # '\\': '\\textbackslash{}'
        }
        for char, escaped in replacements.items():
            s = s.replace(char, escaped)
        return s

    if table_df.empty:
        latex_lines = ["NO DATA"]
    else:
        if classic_horizontal_lines and minimal_horizontal_lines:
            raise AttributeError("classic_horizontal_lines and minimal_horizontal_lines cannot both be True")

        num_cols = len(table_df.columns)

        if alignments is None:
            alignments = ['l'] * num_cols
        else:
            if len(alignments) != num_cols:
                raise ValueError("Number of alignments must match number of columns")

        if vertical_lines:
            col_spec = '|' + '|'.join(alignments) + '|'
        else:
            col_spec = ''.join(alignments)

        latex_lines = []

        # Begin longtable
        latex_lines.append(f'\\begin{{longtable}}{{{col_spec}}}')

        # Add caption and label after header (but before any \hline)
        if caption is not None:
            latex_lines.append(f'\\caption{{{escape_latex(caption)}}}')
        if label is not None:
            latex_lines.append(f'\\label{{{label}}}\\\\')

        if classic_horizontal_lines:
            latex_lines.append('\\hline')
        if minimal_horizontal_lines:
            latex_lines.append('\\toprule')

        # Add header row
        header = table_df.columns.tolist()
        header_line = ' & '.join([escape_latex(str(x)) for x in header]) + ' \\\\'
        latex_lines.append(header_line)

        if classic_horizontal_lines:
            latex_lines.append('\\hline')
        if minimal_horizontal_lines:
            latex_lines.append('\\midrule')

        # Add data rows with horizontal lines between them if specified
        for i, (_, row) in enumerate(table_df.iterrows()):
            row_values = []
            for item in row:
                row_values.append(escape_latex(item) if not pd.isna(item) else '')
            row_line = ' & '.join(row_values) + ' \\\\'
            latex_lines.append(row_line)

            # Add \hline after each data row except the last one
            if classic_horizontal_lines and i < len(table_df) - 1:
                latex_lines.append('\\hline')

            if max_plotted_entities is not None and i > max_plotted_entities:
                latex_lines.append(
                    '\\textbf{Seulement ' + str(i) + ' lignes affichées sur ' + str(len(table_df.index)) + '.} \\\\'
                )
                break

        # Add a final \hline
        if classic_horizontal_lines:
            latex_lines.append('\\hline')
        if minimal_horizontal_lines:
            latex_lines.append('\\bottomrule')

        # End longtable
        latex_lines.append('\\end{longtable}')

    latex_lines.append('')

    latex_code = '\n'.join(latex_lines)

    # Write to file if output_file is provided
    if output_file is not None:
        with open(output_file, 'w') as f:
            f.write(latex_code)

    return latex_code


class Biso:
    """
    Base class for generating plots and tables from data fetched from various APIs.
    The fetch methods are located in each child classes.
    This class is not designed to be called directly but rather to provide general methods to the different plot types.

    :cvar orientation: Orientation for plots ('v' for vertical, 'h' for horizontal).
    :cvar figure_file_extension: File extension of the figure (pdf, tex...).
    :cvar default_barcornerradius: Default corner radius for bars in plots.
    :cvar default_hal_cursor_rows_per_request: Default number of rows per request when using the cursor API.
    :cvar default_height: Default height for plots.
    :cvar default_legend_pos: Default position for the legend.
    :cvar default_main_color: Default color for plots.
    :cvar default_margin: Default margins for plots.
    :cvar default_max_entities: Default maximum number of entities used to create the plot. Default 1000.
        Set to None to disable the limit. This value limits the number of queried entities when doing analysis.
        For example, when creating the collaboration map, it limits the number of works to query from HAL to extract the
        collaborating institutions from.
    :cvar default_max_plotted_entities: Maximum number of bars in the plot or rows in the table. Default to 25.
    :cvar default_template: Default template for plots.
    :cvar default_width: Default width for plots.
    """

    orientation = 'v'
    figure_file_extension = "pdf"

    default_barcornerradius = 10
    default_hal_cursor_rows_per_request = 10000
    default_height = 600
    default_legend_pos = dict(
        x=1,
        y=1,
        xanchor='right',
        yanchor='top'
    )
    default_main_color = "blue"
    default_margin = dict(
        l=5,
        r=5,
        b=5,
        t=5,
        pad=4
    )
    default_max_entities = 1000 # default_max_requested_works
    default_max_plotted_entities = 25
    default_template = "simple_white"
    default_width = 800

    def __init__(
            self,
            lab,
            year: int | None = None,
            barcornerradius: int = default_barcornerradius,
            height: int = default_height,
            legend_pos: dict = None,
            main_color: str = default_main_color,
            margin: dict = None,
            max_entities: int | None = default_max_entities,
            max_plotted_entities: int = default_max_plotted_entities,
            template: str = default_template,
            width: int = default_width,
    ):
        """
        Initialize the Biso class with the given parameters.

        :param lab: The HAL collection identifier. This usually refers to the lab acronym.
        :type lab: str
        :param year: The year for which to fetch data. If None, uses the current year.
        :type year: int | none, optional
        :param barcornerradius: Corner radius for bars in plots.
        :type barcornerradius: int, optional
        :param height: Height of the plot.
        :type height: int, optional
        :param legend_pos: Position of the legend.
        :type legend_pos: dict, optional
        :param main_color: Main color for the plot.
        :type main_color: str, optional
        :param margin: Margins for the plot.
        :type margin: dict, optional
        :param max_entities: Default maximum number of entities used to create the plot. Default 1000.
            Set to None to disable the limit. This value limits the number of queried entities when doing analysis.
            For example, when creating the collaboration map, it limits the number of works to query from HAL to extract
            the collaborating institutions from.
        :type max_entities: int | None, optional
        :param max_plotted_entities: Maximum number of bars in the plot or rows in the table. Default to 25.
        :type max_plotted_entities: int, optional
        :param template: Template for the plot.
        :type template: str, optional
        :param width: Width of the plot.
        :type width: int, optional
        """
        self.lab = lab
        if year is None:
            # get current year
            self.year = datetime.now().year
        else:
            self.year = year
        self.barcornerradius = barcornerradius
        self.height = height
        self.main_color = main_color
        if margin is None:
            self.margin = self.default_margin
        else:
            self.margin = margin
        if legend_pos is None:
            self.legend_pos = self.default_legend_pos
        else:
            self.legend_pos = legend_pos
        self.max_plotted_entities = max_plotted_entities
        self.max_entities = max_entities
        self.template = template
        self.width = width

        self.data = None


    def get_all_dois_with_cursor(self):
        """Get all DOI articles using cursor pagination"""
        all_dois = []
        cursor_mark = "*"  # Initial cursor
        if self.max_entities is None:
            rows_per_request = self.default_hal_cursor_rows_per_request
        else:
            rows_per_request = min(self.default_hal_cursor_rows_per_request, self.max_entities)

        while True:
            # Calculate how many more results we need
            if self.max_entities is not None:
                remaining = self.max_entities - len(all_dois)
                if remaining <= 0:
                    break
                current_rows = min(rows_per_request, remaining)
            else:
                current_rows = rows_per_request

            # Build the cursor-based query URL
            cursor_url = (
                f"https://api.archives-ouvertes.fr/search/{self.lab}/?q=publicationDateY_i:{self.year} AND "
                f"docType_s:(ART OR COMM) AND doiId_s:[* TO *]&wt=json&rows={current_rows}&"
                f"sort=docid asc&cursorMark={cursor_mark}&fl=doiId_s"
            )

            try:
                response = requests.get(cursor_url)
                response.raise_for_status()
                data = response.json()

                # Extract DOIs from the response
                docs = data.get('response', {}).get('docs', [])
                for doc in docs:
                    if 'doiId_s' in doc and doc['doiId_s']:
                        all_dois.append(doc['doiId_s'])

                # Get the next cursor mark
                next_cursor_mark = data.get('nextCursorMark', '')

                # Check if we've reached the end (cursor mark unchanged)
                if next_cursor_mark == cursor_mark:
                    break

                cursor_mark = next_cursor_mark

            except requests.RequestException as e:
                # TODO: manage errors
                print(f"Error fetching data: {e}")
                break

        # Return results (with limit if max_entities is set)
        if self.max_entities is not None:
            print(f"Returning {len(all_dois)} dois (limit at {self.max_entities})")
            return all_dois[:self.max_entities]
        else:
            print(f"Returning all {len(all_dois)} dois")
            return all_dois



    def get_figure(
            self,
            title: str | None = None,
            textposition: str = "outside",
            *args,
            **kwargs
    ) -> go.Figure:
        """
        Generate a bar plot based on the fetched data.

        :param title: Title of the plot.
        :type title: str | None, optional
        :param textposition: Position of the text on bars.
        :type textposition: str, optional
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: The plotly figure.
        :rtype: go.Figure
        """
        if self.data is None:
            self.fetch_data(*args, **kwargs)

        # keep only the first max_plotted_entities items in the dictionary
        self.data =  dict(list(self.data.items())[-self.max_plotted_entities:])

        fig = go.Figure()

        if self.orientation == 'v':
            x_values = list(self.data.keys())
            y_values = list(self.data.values())
        else:
            x_values = list(self.data.values())
            y_values = list(self.data.keys())

        # Add a bar for each type
        fig.add_trace(go.Bar(
            x=x_values,
            y=y_values,
            marker_color=self.main_color,
            orientation=self.orientation,
            text=list(self.data.values()),
            textposition=textposition,
            textangle=0,
            width=get_bar_width(len(self.data.keys())),
        ))

        # Update layout for better visualization
        fig.update_layout(
            barmode='stack',
            barcornerradius=self.barcornerradius,
            width=self.width,
            height=self.height,
            template=self.template,
            legend=self.legend_pos,
            margin=self.margin,
        )
        if title is not None:
            fig.update_layout(title=title)

        return fig


class AnrProjects(Biso):
    """
    A class to fetch and plot data about ANR projects.
    """

    def __init__(self, lab: str, year: int | None = None, **kwargs):
        """
        Initialize the AnrProjects class.

        :param lab: The HAL collection identifier. This usually refers to the lab acronym.
        :type lab: str
        :param year: The year for which to fetch data. If None, uses the current year.
        :type year: int | none, optional
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        """
        super().__init__(lab, year, **kwargs)


    def fetch_data(self):
        """
        Fetch data about ANR projects from the HAL API.

        This method queries the API to get the list of ANR projects and their counts.
        The data is stored in the `data` attribute as a dictionary where keys are ANR project acronyms
        and values are their respective counts.
        """
        facet_url=(
            f"https://api.archives-ouvertes.fr/search/{self.lab}/?q=publicationDateY_i:{self.year}"
            f"&wt=json&rows=0&facet=true&facet.field=anrProjectAcronym_s&facet.limit={self.max_plotted_entities}"
        )
        facets=requests.get(facet_url).json()
        anr_projects_list=facets['facet_counts']['facet_fields']['anrProjectAcronym_s']
        self.data = {anr_projects_list[i]: anr_projects_list[i + 1] for i in range(0, len(anr_projects_list), 2)
                     if anr_projects_list[i + 1] != 0}


class Chapters(Biso):
    """
    A class to fetch and generate a table of book chapters.
    """

    figure_file_extension = "tex"


    def __init__(self, lab: str, year: int | None = None, **kwargs):
        """
        Initialize the Chapters class.

        :param lab: The HAL collection identifier. This usually refers to the lab acronym.
        :type lab: str
        :param year: The year for which to fetch data. If None, uses the current year.
        :type year: int | none, optional
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        """
        super().__init__(lab, year, **kwargs)


    def fetch_data(self):
        """
        Fetch data about book chapters from the HAL API.

        This method queries the API to get the list of book chapters and their metadata.
        The data is stored in the `data` attribute as a pandas DataFrame with columns for title (`title_s`),
        book title (`bookTitle_s`), and publisher (`publisher_s`).
        """
        url=(
            f"https://api.archives-ouvertes.fr/search/{self.lab}/?q=*:*&fq=docType_s:COUV&"
            f"fq=producedDateY_i:{self.year}&rows={self.max_plotted_entities}&wt=json&indent=true&"
            f"fl=title_s,bookTitle_s,publisher_s"
        )
        chapters=requests.get(url).json()['response']['docs']

        for i in range(len(chapters)):
            if 'title_s' not in chapters[i].keys():
                chapters[i]['title_s'] = ""
            else:
                chapters[i]['title_s'] = ' ; '.join(chapters[i]['title_s'])

            if 'publisher_s' not in chapters[i].keys():
                chapters[i]['publisher_s'] = ""
            else:
                chapters[i]['publisher_s'] = ' ; '.join(chapters[i]['publisher_s'])

        self.data = pd.DataFrame.from_records(chapters)

        self.data = self.data.rename(columns={
            "title_s": "Titre du chapitre",
            "bookTitle_s": "Titre du livre",
            "publisher_s": "Éditeur",
        })


    def get_figure(self, output_file: str | None = None, *args, **kwargs) -> str:
        """
        Generate a LaTeX longtable of book chapters.

        :param output_file: If not None, the file path where to save the LaTeX file.
        :type output_file: str | None
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: LaTeX code for the longtable representing the book chapters data.
        :rtype: str
        """
        if self.data is None:
            self.fetch_data(*args, **kwargs)

        latex_table = dataframe_to_longtable(
            self.data,
            alignments=['p{.4\\linewidth}','p{.35\\linewidth}','p{.15\\linewidth}'],
            caption='Liste des chapitres',
            label='tab_chapters',
            vertical_lines=False,
            max_plotted_entities=self.max_plotted_entities,
            output_file=output_file
        )

        return latex_table


class CollaborationMap(Biso):
    """
    A class to fetch and plot data about collaborations on a map.

    :cvar default_height: Default height for the map.
    :cvar default_width: Default width for the map.
    :cvar default_zoom_lat_range: Default latitude range for zoomed map.
    :cvar default_zoom_lon_range: Default longitude range for zoomed map.
    """

    # override Biso class default height and width
    default_height = 500
    default_width = 1200
    default_height_zoom = 800
    default_width_zoom = 1200
    default_zoom_lat_range = [33.5,71]
    default_zoom_lon_range = [-18.5, 39.5]

    def __init__(
            self,
            lab: str,
            year: int | None = None,
            countries_to_ignore: list[str] | None = None,
            height: int | None = None,
            institutions_to_exclude: list[str] | None = None,
            map_zoom: bool = False,
            markers_scale_factor: float | int | None = None,
            resolution: int = 110,
            title: str | None = None, # TODO: merge in parent class
            width: int | None = None,
            zoom_lat_range: list[float | int] | None = None,
            zoom_lon_range: list[float | int] | None = None,
            **kwargs
    ):
        """
        Initialize the CollaborationMap class.

        :param lab: The HAL collection identifier. This usually refers to the lab acronym.
        :type lab: str
        :param year: The year for which to fetch data. If None, uses the current year.
        :type year: int | none, optional
        :param countries_to_ignore: List of countries to ignore in the data.
        :type countries_to_ignore: list[str] | None, optional
        :param height: Height of the plot.
        :type height: int | None, optional
        :param institutions_to_exclude: List of institutions to exclude from the data.
        :type institutions_to_exclude: list[str] | None, optional
        :param map_zoom: If set to true, zoom the map according to the ranges of coordinates defined by
            zoom_lat_range and zoom_lat_range
        :type map_zoom: bool, optional
        :param markers_scale_factor: Scale factor for the markers. Default is 1. Increase to decrease marker size.
            If not set and map_zoom is True, default to 0.5.
        :type markers_scale_factor: float | int | None, optional
        :param resolution: Resolution of the plot: can either be 110 (low resolution) or 50 (high resolution).
        :type resolution: int, optional
        :param title: Title of the plot.
        :type title: str | None, optional
        :param width: Width of the plot.
        :type width: int | None, optional
        :param zoom_lat_range: Latitude range of coordinates for the zoom map. If set to None, the zoom will be on
            Europe.
        :type zoom_lat_range: list[float | int] | None, optional
        :param zoom_lon_range: Longitude range of coordinates for the zoom map. If set to None, the zoom will be on
            Europe.
        :type zoom_lon_range: list[float | int] | None, optional
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        """
        if height is None and width is None:
            self.has_default_width_and_height = True
        else:
            self.has_default_width_and_height = False
        if countries_to_ignore is None:
            countries_to_ignore = []
        self.countries_to_ignore = countries_to_ignore
        if height is None:
            height = self.default_height
        if institutions_to_exclude is None:
            institutions_to_exclude = []
        self.institutions_to_exclude = institutions_to_exclude
        self.map_zoom = map_zoom
        if markers_scale_factor is None:
            if map_zoom:
                self.markers_scale_factor = 0.1
            else:
                self.markers_scale_factor = 1
        else:
            self.markers_scale_factor = markers_scale_factor
        self.resolution = resolution
        self.title = title
        if width is None:
            width = self.default_width
        super().__init__(lab, year, height=height, width=width, **kwargs)
        if zoom_lat_range is None:
            self.zoom_lat_range = self.default_zoom_lat_range
        else:
            self.zoom_lat_range = zoom_lat_range
        if zoom_lon_range is None:
            self.zoom_lon_range = self.default_zoom_lon_range
        else:
            self.zoom_lon_range = zoom_lon_range


    def fetch_data(self):
        """
        Fetch data about collaborations from the HAL API and OpenAlex API.

        This method queries the API to get the list of collaborations and their metadata.
        It processes the data to create a DataFrame with latitude, longitude, and other relevant information.
        """
        # get the list of DOI from HAL:
        article_dois = self.get_all_dois_with_cursor()

        # Download articles metadata from OpenAlex:
        print(f"Downloading the metadata for {len(article_dois)} DOIs from OpenAlex...")
        works = WorksData().get_multiple_works_from_doi(article_dois, return_dataframe=False)
        works = [work for work in works if work is not None]
        print(f"{len(works)} works retrieved successfully from OpenAlex out of {len(article_dois)}")

        # Download institution metadata from OpenAlex:
        # get the list of institutions who collaborated per work:
        works_institutions = [
            list(set([institution['id'] for author in work['authorships'] for institution in author['institutions']]))
            for work in works
        ]
        # list of the institutions we collaborated with
        institutions_id = set(list([institution for institutions in works_institutions for institution in institutions
                                    if institution not in self.institutions_to_exclude]))
        print(f"{len(institutions_id)} unique institutions with which we collaborated on works")
        # remove the https://openalex.org/ at the beginning
        institutions_id = [institution_id[21:] for institution_id in institutions_id]
        # create dictionaries with the institution id as key and lon, lat and name as item
        institutions_name = {}
        institutions_lat = {}
        institutions_lon = {}
        institutions_country = {}
        institutions_count = {}
        # count the number of collaboration per institutions:
        # works_institutions contains the institutions we collaborated per work, so we
        # can count on how many works we collaborated with each institution
        all_institutions_count = Counter(list(
            [institution for institutions in works_institutions for institution in institutions]
        ))
        institutions = InstitutionsPlot().get_multiple_entities_from_id(institutions_id, return_dataframe=False)
        for institution in institutions:
            if institution['geo']['country'] not in self.countries_to_ignore:
                institutions_name[institution['id']] = institution['display_name']
                institutions_lat[institution['id']] = institution['geo']['latitude']
                institutions_lon[institution['id']] = institution['geo']['longitude']
                institutions_country[institution['id']] = institution['geo']['country']
                institutions_count[institution['id']] = all_institutions_count[institution['id']]


        # Create DataFrame to plot:
        institutions_name_s = pd.Series(dict(institutions_name), name='name')
        institutions_lat_s = pd.Series(dict(institutions_lat), name='lat')
        institutions_lon_s = pd.Series(dict(institutions_lon), name='lon')
        institutions_country_s = pd.Series(dict(institutions_country), name='country')
        institutions_count_s = pd.Series(dict(institutions_count), name='count')
        self.data = pd.concat([institutions_name_s, institutions_lat_s, institutions_lon_s, institutions_country_s,
                               institutions_count_s], axis=1)

        # calculate stats:
        collaborations_nb = int(self.data['count'].sum())
        institutions_nb = len(self.data)
        countries_nb = len(self.data['country'].unique())

        print(f"{len(self.data)} unique institutions to plot")

        stats = {
            'collaborations_nb': collaborations_nb,
            'institutions_nb': institutions_nb,
            'countries_nb': countries_nb
        }

        return stats



    def get_figure(self, *args, **kwargs) -> go.Figure:
        """
        Plot a map with the number of collaborations per institution.

        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: The plotly figure.
        :rtype: go.Figure
        """
        if self.data is None:
            self.fetch_data()

        countries_land_gray_color = "#dadada"
        countries_lines_color = "Black"

        if self.map_zoom:
            lataxis_range = self.zoom_lat_range if self.zoom_lat_range is None else self.zoom_lat_range
            lonaxis_range = self.zoom_lon_range if self.zoom_lon_range is None else self.zoom_lon_range
        else:
            lataxis_range = None
            lonaxis_range = None

        # calculate count max and count sum within lataxis_range and lonaxis_range
        if lataxis_range is not None and lonaxis_range is not None:
            # Filter data within the specified ranges
            filtered_data = self.data[
                (self.data['lat'] >= lataxis_range[0]) &
                (self.data['lat'] <= lataxis_range[1]) &
                (self.data['lon'] >= lonaxis_range[0]) &
                (self.data['lon'] <= lonaxis_range[1])
            ]
            count_max = filtered_data['count'].max() if not filtered_data.empty else 0
            count_sum = filtered_data['count'].sum() if not filtered_data.empty else 0
        else:
            # Use all data if no range is specified
            count_max = self.data['count'].max() if not self.data.empty else 0
            count_sum = self.data['count'].sum() if not self.data.empty else 0

        # example values: 0.05 for 10 entities, 0.5 for 1000 entities
        # calculate markers_size_ref to auto-adjust based on count_max and count_sum
        # markers_size_ref = 3.54e-3*math.sqrt(count_max*20 + count_sum.sum())
        markers_size_ref = self.markers_scale_factor*1e-2*math.sqrt(count_max*20 + count_sum.sum())
        # markers_size_ref = 0.5
        # set a ln scale
        self.data['size'] = np.log(self.data['count'] + 1)

        fig = px.scatter_geo(
            self.data,
            lat='lat',
            lon='lon',
            size='size',
            custom_data=['name', 'country', 'count'],
            height=self.default_height_zoom if self.map_zoom and self.has_default_width_and_height else self.height,
            width=self.default_width_zoom if self.map_zoom and self.has_default_width_and_height else self.width,
            #color_discrete_sequence=["#eb7125"]
        )
        # add the hover
        hover_template = [
                "%{customdata[0]}",
                "%{customdata[1]}",
                "%{customdata[2]} co-authored paper(s)",
        ]
        fig.update_traces(
            hovertemplate="<br>".join(hover_template),
            marker=dict(
                color=self.main_color,
                opacity=1,
                # sizemode='area',
                sizeref=markers_size_ref,
                #size=1,
                line=dict(
                    color="white",
                    width=0 # 0.1
                )
            ),
        )

        fig.update_layout(
            margin=self.margin,
            # showlegend=True,
            # autosize=True
        )

        if self.title is not None:
            fig.update_layout(title=self.title)

        fig.update_geos(
            visible=False,
            resolution=self.resolution,
            projection_type="natural earth",
            showcountries=True,
            showland=True,
            countrycolor=countries_lines_color,
            landcolor=countries_land_gray_color,
            showframe=True,
        )

        if self.map_zoom:
            fig.update_geos(
                lataxis_range=lataxis_range,
                lonaxis_range=lonaxis_range,
            )

        return fig


class CollaborationNames(Biso):
    """
    A class to fetch and plot data about institutions collaboration names.

    :cvar orientation: Orientation for plots ('h' for horizontal).
    """

    orientation = 'h'

    def __init__(self, lab: str, year: int | None = None, **kwargs):
        """
        Initialize the CollaborationNames class.

        :param lab: The HAL collection identifier. This usually refers to the lab acronym.
        :type lab: str
        :param year: The year for which to fetch data. If None, uses the current year.
        :type year: int | none, optional
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        """
        super().__init__(lab, year, **kwargs)


    def fetch_data(self, countries_to_exclude: list[str] | None = None):
        """
        Fetch data about collaboration names from the HAL API only.

        This method queries the API to get the list of collaboration names and their counts.
        It processes the data to create a dictionary where keys are formatted structure names (including country flags)
        and values are their respective counts.

        :param countries_to_exclude: List of countries to exclude from the data.
        :type countries_to_exclude: list[str] | None, optional
        """
        def format_structure_name(struct_name: str, country_code: str) -> str:
            """
            Format the structure name by cropping if too long and adding a country flag.

            :param struct_name: The structure name.
            :type struct_name: str
            :param country_code: The country code.
            :type country_code: str
            :return: The formatted structure name with country flag.
            :rtype: str
            """
            # crop name if too long
            if len(struct_name) > 75:
                struct_name = struct_name[:75]+"... "
            # add country flag
            if country_code is not None:
                struct_name += " " + flag.flag(country_code)

            return struct_name

        if countries_to_exclude is None:
            countries_to_exclude = []

        # Get count of each structure id in publications
        structs_facet_url=(
            f"https://api.archives-ouvertes.fr/search/{self.lab}/?q=publicationDateY_i:{self.year} AND "
            f"docType_s:(ART OR COMM)&wt=json&rows=0&facet=true&facet.field=structId_i&"
            f"facet.limit={self.max_plotted_entities}"
        )
        structs_id_facets=requests.get(structs_facet_url).json()
        structs_id_facets = structs_id_facets['facet_counts']['facet_fields']['structId_i']
        structs_id_count = {
            struct_id: count for struct_id, count in zip(structs_id_facets[::2], structs_id_facets[1::2])
        }

        struct_list = []
        # get metadata of each structure (name + country code)
        for i in range (0, len(structs_id_count), 500):
            facet_url = (
                f"https://api.archives-ouvertes.fr/ref/structure/?q=docid:"
                f"{" OR ".join(list(structs_id_count.keys())[i:i+500])}&fl=docid,label_s,country_s&rows=10000"
            )
            facets = requests.get(facet_url).json()
            facets_res = facets['response']['docs']
            # As HAL returns structures that were not requested, we remove non-requested structures + remove structures
            # not in countries to exclude
            struct_list[i:i+500] = [
                struct for struct in facets_res if struct['docid'] in list(structs_id_count.keys())[i:i+500]
                                                   and struct['country_s'] not in countries_to_exclude
            ]

        self.data = {
            format_structure_name(struct['label_s'], struct.get('country_s', None)): structs_id_count[struct['docid']]
            for struct in struct_list
        }

        # sort values
        self.data = {k: v for k, v in sorted(self.data.items(), key=lambda item: item[1])}


class Conferences(Biso):
    """
    A class to fetch and plot data about conferences.

    :cvar orientation: Orientation for plots ('h' for horizontal).
    """

    orientation = 'h'

    def __init__(self, lab: str, year: int | None = None, **kwargs):
        """
        Initialize the Conferences class.

        :param lab: The HAL collection identifier. This usually refers to the lab acronym.
        :type lab: str
        :param year: The year for which to fetch data. If None, uses the current year.
        :type year: int | none, optional
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        """
        super().__init__(lab, year, **kwargs)

    def fetch_data(self):
        """
        Fetch data about conferences from the HAL API.

        This method queries the API to get the list of conferences and their counts.
        It processes the data to create a dictionary where keys are formatted conference names (including country flags)
        and values are their respective counts.
        """
        def format_conference_name(conf_name: str, country_code: str) -> str:
            """
            Format the conference name by cropping if too long and adding a country flag.

            :param conf_name: The conference name.
            :type conf_name: str
            :param country_code: The country code.
            :type country_code: str
            :return: The formatted conference name with country flag.
            :rtype: str
            """
            # crop name if too long
            if len(conf_name) > 75:
                conf_name = conf_name[:75]+"... "
            # add country flag
            conf_name += " " + flag.flag(country_code)

            return conf_name

        facet_url=(
            f"https://api.archives-ouvertes.fr/search/{self.lab}/?q=publicationDateY_i:{self.year}&wt=json&rows=0"
            f"&facet=true&facet.pivot=conferenceTitle_s,country_s&facet.limit={self.max_plotted_entities}"
        )
        facets=requests.get(facet_url).json()
        conferences_list=facets['facet_counts']['facet_pivot']['conferenceTitle_s,country_s']
        conferences_list = sorted(conferences_list, key=lambda conf: conf['count'])
        self.data = {format_conference_name(conf['value'], conf['pivot'][0]['value']): conf['count']
                     for conf in conferences_list}


class EuropeanProjects(Biso):
    """
    A class to fetch and plot data about European projects.

    :cvar orientation: Orientation for plots ('h' for horizontal).
    """

    orientation = 'h'

    def __init__(self, lab: str, year: int | None = None, **kwargs):
        """
        Initialize the EuropeanProjects class.

        :param lab: The HAL collection identifier. This usually refers to the lab acronym.
        :type lab: str
        :param year: The year for which to fetch data. If None, uses the current year.
        :type year: int | none, optional
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        """
        super().__init__(lab, year, **kwargs)


    def fetch_data(self):
        """
        Fetch data about European projects from the HAL API.

        This method queries the API to get the list of European projects and their counts.
        The data is stored in the `data` attribute as a dictionary where keys are European project acronyms
        and values are their respective counts.
        """
        facet_url=(
            f"https://api.archives-ouvertes.fr/search/{self.lab}/?q=publicationDateY_i:{self.year}&wt=json&rows=0"
            f"&facet=true&facet.field=europeanProjectAcronym_s&facet.limit={self.max_plotted_entities}"
        )
        facets=requests.get(facet_url).json()
        eu_projects_list=facets['facet_counts']['facet_fields']['europeanProjectAcronym_s']
        self.data = {eu_projects_list[i]: eu_projects_list[i + 1] for i in range(0, len(eu_projects_list), 2)
                     if eu_projects_list[i + 1] != 0}


class Journals(Biso):
    """
    A class to fetch and generate a table of journals.
    """

    figure_file_extension = "tex"

    def __init__(self, lab: str, year: int | None = None, **kwargs):
        """
        Initialize the Journals class.

        :param lab: The HAL collection identifier. This usually refers to the lab acronym.
        :type lab: str
        :param year: The year for which to fetch data. If None, uses the current year.
        :type year: int | none, optional
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        """
        super().__init__(lab, year, **kwargs)

    def fetch_data(self):
        """
        Fetch data about journals from the API.

        TODO
        """
        # TODO: Add code to get data from bibliohub (use self.max_plotted_entities)
        # TODO: sort by nb publications
        self.data = pd.read_csv(
            "bibliohub_top_journals_em2c_2023.csv",
            na_values="-",
            usecols=[
                'bso.journal_name',
                'bso.oa_details.2024Q4.oa_colors_with_priority_to_publisher',
                'bso.apc_paid.currency',
                'bso.apc_paid.value'
            ],
        )

        self.data = self.data.dropna(subset=['bso.journal_name'])

        self.data['bso.oa_details.2024Q4.oa_colors_with_priority_to_publisher'] = self.data[
            'bso.oa_details.2024Q4.oa_colors_with_priority_to_publisher'].replace('green_only', 'green')

        # Fix data
        self.data['bso.journal_name'] = [work.replace('&amp;', '&') for work in self.data['bso.journal_name']]


    def get_figure(self, output_file: str | None = None, *args, **kwargs) -> str:
        """
        Generate a LaTeX longtable of journals.

        :param output_file: If not None, the file path where to save the LaTeX file.
        :type output_file: str | None
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: LaTeX code for the longtable representing the journals data.
        :rtype: str
        """
        if self.data is None:
            self.fetch_data(*args, **kwargs)

        journals = {}

        for index, work in self.data.iterrows():
            if work['bso.journal_name'] not in journals.keys():
                journals[work['bso.journal_name']] = []
            journals[work['bso.journal_name']].append(
                {'oa_color': work['bso.oa_details.2024Q4.oa_colors_with_priority_to_publisher']}
            )
            if pd.notna(work['bso.apc_paid.value']):
                journals[work['bso.journal_name']][-1]['apc_paid.value'] = work['bso.apc_paid.value']
                journals[work['bso.journal_name']][-1]['apc_paid.currency'] = work['bso.apc_paid.currency']

        journals_table = []

        for journal, works in journals.items():
            apcs = ""
            oa_colors = []
            for work in works:
                oa_colors.append(work['oa_color'])
                if 'apc_paid.value' not in work.keys():
                    pass
                else:
                    if len(apcs) > 0:
                        apcs += ", \\\\ "
                    apcs += work['apc_paid.value'].replace(",", " ") + " " + work['apc_paid.currency']
            oa_colors = ", \\\\ " .join([f"{count} {color}" for color, count in pd.Index(oa_colors).value_counts().items()])

            journals_table.append(
                {
                    'Revue': journal,
                    'Nombre de publications': "\\makecell{" + str(len(works)) + "}",
                    'Status des accès ouverts des publications': "\\makecell{" + oa_colors + "}",
                    'APC payés': "\\makecell{" + apcs + "}"
                }
            )

        df = pd.DataFrame.from_records(journals_table)

        latex_table = dataframe_to_longtable(
            df,
            alignments=['p{.55\\linewidth}','P{.08\\linewidth}','P{.11\\linewidth}','P{.11\\linewidth}'],
            caption='Liste des revues',
            label='tab_journals',
            vertical_lines=False,
            max_plotted_entities=self.max_plotted_entities,
            output_file=output_file
        )

        return latex_table


class OpenAccessWorks(Biso):
    """
    A class to fetch and plot data about the open access status of works.

    :cvar default_year_range_difference: Default difference in years for the range when no year range is provided.
    :cvar default_oa_colors: Default colors for different open access statuses.
    """

    default_year_range_difference = 4

    default_oa_colors = {
        "TI dans HAL": "#00807A",
        "OA hors HAL": "#FEBC18",
        "Accès fermé": "#C60B46"
    }

    def __init__(
            self,
            lab: str,
            year: int | None = None,
            year_range: tuple[int, int] | int | None = None,
            colors: Any = None,
            **kwargs
    ):
        """
        Initialize the OpenAccessWorks class.

        :param lab: The HAL collection identifier. This usually refers to the lab acronym.
        :type lab: str
        :param year: The year for which to fetch data. If None, uses the current year. Ignored if `year_range` is
            provided. If `year_range` is not provided, `year_range` will be set to
            `[year - self.default_year_range_difference, year]`
        :type year: int | none, optional
        :param year_range: Range of years to fetch data for. If None, fetch the years from
            `self.year - default_year_range_difference` to `self.year`. If only one int is provided, it replaces
            self.year.
        :type year_range: tuple[int, int] | int | None, optional
        :param colors: Colors for different open access statuses.
        :type colors: Any, optional
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        """
        if year is not None and year_range is not None:
            warnings.warn(
                f"You provided year and year_range, so year will be ignored. The plot will use year_range={year_range}."
            )
        super().__init__(lab, year, **kwargs)
        if colors is None:
            self.colors = self.default_oa_colors
        else:
            self.colors = colors
        if isinstance(year_range, int):
            self.year = year_range
            year_range = None
        if year_range is None:
            year_range = (self.year - self.default_year_range_difference, self.year)
        self.year_range = year_range


    def fetch_data(self):
        """
        Fetch data about open access works from the HAL API.

        This method queries the API to get the count of open access works for each year in the specified year range.
        The data is stored in the `data` attribute as a pandas DataFrame with counts for different open access statuses.
        """
        self.data=pd.DataFrame(
            columns=['ti_dans_hal', 'oa_hors_hal', 'non_oa'],
            index=range(self.year_range[0], self.year_range[1] + 1)
        )
        facet_url=(
            f"https://api.archives-ouvertes.fr/search/{self.lab}/?q=publicationDateY_i:[{self.year_range[0]} TO "
            f"{self.year_range[1]}] AND submitType_s:(file OR annex) AND docType_s:(ART OR COMM)&wt=json&"
            f"rows=0&facet=true&facet.field=publicationDateY_i&facet.limit={self.max_plotted_entities}"
        )
        facets=requests.get(facet_url).json()
        ti_numbers=facets['facet_counts']['facet_fields']['publicationDateY_i']
        for ind, i in enumerate(ti_numbers):
            if isinstance(i,str):
                self.data.loc[int(i),'ti_dans_hal']=ti_numbers[ind+1]
            else:
                pass

        oa_url=(
            f"https://api.archives-ouvertes.fr/search/{self.lab}/?q=publicationDateY_i:[{self.year_range[0]} TO "
            f"{self.year_range[1]}] AND openAccess_bool:true AND submitType_s:notice AND docType_s:(ART OR COMM)&"
            f"wt=json&rows=0&facet=true&facet.field=publicationDateY_i&facet.limit={self.max_plotted_entities}"
        )
        oa=requests.get(oa_url).json()
        oa_numbers=oa['facet_counts']['facet_fields']['publicationDateY_i']
        for ind, i in enumerate(oa_numbers):
            if isinstance(i,str):
                self.data.loc[int(i),'oa_hors_hal']=oa_numbers[ind+1]
            else:
                pass

        non_oa_url=(
            f"https://api.archives-ouvertes.fr/search/{self.lab}/?q=publicationDateY_i:[{self.year_range[0]} TO "
            f"{self.year_range[1]}] AND openAccess_bool:false AND submitType_s:notice  AND docType_s:(ART OR COMM)&"
            f"wt=json&rows=0&facet=true&facet.field=publicationDateY_i&facet.limit={self.max_plotted_entities}"
        )
        non_oa=requests.get(non_oa_url).json()
        non_oa_numbers=non_oa['facet_counts']['facet_fields']['publicationDateY_i']
        for ind, i in enumerate(non_oa_numbers):
            if isinstance(i,str):
                self.data.loc[int(i),'non_oa']=int(non_oa_numbers[ind+1])
            else:
                pass
        self.data = self.data.infer_objects().fillna(0)

        stats = {
            'oa_works_period': f"{self.year_range[0]} - {self.year_range[1]}",
        }
        return stats


    def get_figure(
            self,
            title: str | None = None,
            *args,
            **kwargs
    ) -> go.Figure:
        """
        Plot the open access status of works.

        :param title: Title of the plot.
        :type title: str | None, optional
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: The plotly figure.
        :rtype: go.Figure
        """
        if self.data is None:
            self.fetch_data()

        years=tuple(self.data.index)

        oa_values={
            "TI dans HAL": np.array(self.data['ti_dans_hal']),
            "OA hors HAL": np.array(self.data['oa_hors_hal']),
            "Accès fermé": np.array(self.data['non_oa'])
        }

        fig = go.Figure()

        # invisible left bars
        for i, (oa_type, count) in enumerate(oa_values.items()):
            fig.add_trace(go.Bar(
                x=years,
                y=count,
                marker_color="rgba(0,0,0,0)",
                offsetgroup=-0.1,
                width=0.1,
                showlegend=False,
                hoverinfo="skip",
            ))

        # Bars
        for i, (oa_type, count) in enumerate(oa_values.items()):
            fig.add_trace(go.Bar(
                x=years,
                y=count,
                name=oa_type,
                marker_color=self.colors[oa_type],
                insidetextanchor="middle",
                textangle=0,  # Prevent text from rotating
                offsetgroup=0,
            ))

        # invisible right bars with text
        for i, (oa_type, count) in enumerate(oa_values.items()):
            fig.add_trace(go.Bar(
                x=years,
                y=count,
                name=oa_type,
                marker_color="rgba(0,0,0,0)",
                text=count,
                textposition="inside",
                textfont_color="black",
                insidetextanchor="middle",
                textangle=0,  # Prevent text from rotating
                offsetgroup=1,
                showlegend=False,
                hoverinfo="skip",
            ))

        # Update layout for better visualization
        fig.update_layout(
            barmode='stack',
            barcornerradius=self.barcornerradius,
            width=self.width,
            height=self.height,
            template="simple_white",
            uniformtext_minsize=8,
            uniformtext_mode='show',
            bargap=0.0,
            bargroupgap=0.0,
            legend=self.legend_pos,
            margin=self.margin,
        )

        if title is not None:
            fig.update_layout(title=title)

        return fig


class WorksType(Biso):
    """
    A class to fetch and plot data about work types.
    """

    def __init__(self, lab, year: int | None = None, **kwargs):
        """
        Initialize the WorksType class.

        :param lab: The HAL collection identifier. This usually refers to the lab acronym.
        :type lab: str
        :param year: The year for which to fetch data. If None, uses the current year.
        :type year: int | none, optional
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        """
        super().__init__(lab, year, **kwargs)


    def fetch_data(self):
        """
        Fetch data about work types from the HAL API.

        This method queries the API to get the list of work types and their counts.
        It processes the data to create a dictionary where keys are work type names and values are their respective
        counts.
        """
        facet_url=(
            f"https://api.archives-ouvertes.fr/search/{self.lab}/?q=publicationDateY_i:{self.year} &"
            f"wt=json&rows=0&facet=true&facet.pivot=docType_s&facet.limit={self.max_plotted_entities}"
        )
        facets=requests.get(facet_url).json()
        document_types_list=facets['facet_counts']['facet_pivot']['docType_s']

        self.data = {get_hal_doc_type_name(doc_type['value']): doc_type['count'] for doc_type in document_types_list}
