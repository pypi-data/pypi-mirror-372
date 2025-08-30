# -*- coding: utf-8 -*-
"""
Module for Cube processes.
"""

##### IMPORTS #####
# Standard imports
import re
import ast
import subprocess
import tempfile
import contextlib
from warnings import warn
from copy import deepcopy
from pathlib import Path
from collections import Counter
from typing import Optional, Any, Union

# Third party imports
import pandas as pd  # type: ignore
import polars as pl

# Local imports

##### CONSTANTS #####


##### CLASSES #####
class Node:
    """
    Simple node class for representing network nodes.

    Parameters
    ----------
    string : str or int
        String representation of the node.
    **kwargs : dict
        Additional attributes to be assigned to the node.

    Attributes
    ----------
    id : int
        Node identifier, absolute value from string.
    stopping : bool
        Whether the node is a stopping point.
    _string : str
        Internal storage of the original string representation.
    """

    def __init__(self, string: Union[str, int], **kwargs: Any) -> None:
        self._string = str(string)
        self.id = abs(int(self._string.strip()))
        self.__dict__.update(**kwargs)

        if self._string.strip().startswith("-"):
            self.stopping = False
        else:
            self.stopping = True

    @property
    def attrs(self) -> dict[str, Any]:
        """
        Returns a dictionary with user-defined attributes.

        Returns
        -------
        Dict[str, Any]
            Dictionary of custom attributes excluding internal ones.
        """
        return {
            k: v
            for k, v in self.__dict__.items()
            if "_" not in k and "id" != k and "ID" != k and "stopping" != k
        }

    def __repr__(self) -> str:
        """
        Object's summary representation.

        Returns
        -------
        str
            String representation of the node.
        """
        return f"{'-' if not self.stopping else ''}{self.id}, {self.attrs}"

    def __str__(
        self,
        node_attrs: Optional[list[str]] = None,
        exclude_node_attrs: Optional[list[str]] = None,
    ) -> str:
        """
        String representation of the node.

        Parameters
        ----------
        node_attrs : list of str, optional
            List of node attributes to include.
        exclude_node_attrs : list of str, optional
            List of node attributes to omit.

        Returns
        -------
        str
            String representation of the node with selected attributes.
        """
        txt_node = f"{'-' if not self.stopping else ''}{self.id}"

        if self.attrs:
            if node_attrs:
                attrs = {k: v for k, v in self.attrs.items() if k in node_attrs}
            else:
                attrs = self.attrs

            if exclude_node_attrs:
                attrs = {k: v for k, v in attrs.items() if k not in exclude_node_attrs}

            formatted_attrs = [f"{k}={v}" for k, v in attrs.items()]

            txt_attrs = ", ".join(formatted_attrs)

            if txt_attrs:
                txt_node = ", ".join([txt_node, txt_attrs])

        return txt_node

    def copy(self) -> "Node":
        """
        Create a deep copy of the node.

        Returns
        -------
        Node
            A new instance that is a deep copy of this node.
        """
        return deepcopy(self)


class Line:
    """
    Simple line class representing a sequence of nodes.

    A line is a sequence of nodes with its own properties.

    Parameters
    ----------
    nodes : list of Node
        List of node objects that form the line.
    **kwargs : dict
        Additional attributes to be assigned to the line.

    Attributes
    ----------
    nodes : list of Node
        List of nodes that form the line.
    name : str
        Name of the line (set via kwargs).
    unquoted : list of str
        Class variable that defines values that should not be quoted.
    NodeLabel : str
        Label to identify nodes in string representation.
    """

    # Class variables
    unquoted = ["T", "F"]
    NodeLabel = "N"  # Or 'NODE'

    def __init__(self, nodes: list[Node], **kwargs: Any) -> None:
        """
        Initialize a line object.

        Parameters
        ----------
        nodes : list[Node]
            List of node objects that form the line.
        **kwargs : dict
            Additional attributes to be assigned to the line.
        """
        self.nodes = nodes  # a list of node objects
        self.name = kwargs.get("NAME", "")  # Use NAME if present, empty string if not

        # Remove NAME from kwargs to avoid duplication
        if "NAME" in kwargs:
            del kwargs["NAME"]

        self.__dict__.update(**kwargs)

    @property
    def attrs(self) -> dict[str, Any]:
        """
        Returns a dictionary with user-defined attributes.

        Returns
        -------
        Dict[str, Any]
            Dictionary of line attributes excluding nodes and internal ones.
        """
        return {
            k: v
            for k, v in self.__dict__.items()
            if "nodes" != k and not k.startswith("_")
        }

    @property
    def stops(self) -> list[Node]:
        """
        Returns a list of the nodes that are actual stops.

        Returns
        -------
        list[Node]
            List of nodes marked as stopping points.
        """
        return [node for node in self.nodes if node.stopping]

    def __repr__(self) -> str:
        """
        Object's summary representation.

        Returns
        -------
        str
            String summary of the line including node count and attributes.
        """
        txt = (
            f"Line with {len(self.nodes)} nodes (of which {len(self.stops)} are stops)."
        )
        txt += f"\n{self.attrs}"
        return txt

    def __str__(
        self,
        line_attrs: Optional[list[str]] = None,
        exclude_line_attrs: Optional[list[str]] = None,
        node_attrs: Optional[list[str]] = None,
        exclude_node_attrs: Optional[list[str]] = None,
    ) -> str:
        """
        String representation of the line.

        Parameters
        ----------
        line_attrs : list of str, optional
            List of line attributes to include.
        exclude_line_attrs : list of str, optional
            List of line attributes to omit.
        node_attrs : list of str, optional
            List of node attributes to include.
        exclude_node_attrs : list of str, optional
            List of node attributes to omit.

        Returns
        -------
        str
            String representation of the line with selected attributes.
        """
        # String attributes are quoted, with exceptions
        formatted_attrs = []

        if line_attrs:
            l_attrs = {k: v for k, v in self.attrs.items() if k in line_attrs}
        else:
            l_attrs = self.attrs

        if exclude_line_attrs:
            l_attrs = {k: v for k, v in l_attrs.items() if k not in exclude_line_attrs}

        for k, v in l_attrs.items():
            if isinstance(v, str) and v not in self.unquoted:
                f = repr(v)  # This will enclose in the right quotes
            else:
                f = v
            formatted_attrs.append(f"{k}={f}")

        txt_attrs = ", ".join(formatted_attrs)

        # First nodes, and nodes after attributes, are labeled
        formatted_nodes = []
        first_node = True
        for n in self.nodes:
            n_str = (
                n.__str__()
                if node_attrs is None and exclude_node_attrs is None
                else n.__str__(node_attrs, exclude_node_attrs)
            )
            if first_node:
                formatted_nodes.append(f"{self.NodeLabel}={n_str}")
                first_node = False
            else:
                formatted_nodes.append(n_str)

            if node_attrs:
                n_attrs = {k: v for k, v in n.attrs.items() if k in node_attrs}
            else:
                n_attrs = n.attrs

            if exclude_node_attrs:
                n_attrs = {
                    k: v for k, v in n_attrs.items() if k not in exclude_node_attrs
                }

            if n_attrs:
                # node has attributes printed, reset the flag:
                first_node = True

        txt_nodes = ", ".join(formatted_nodes)

        txt = f"LINE {', '.join([txt_attrs, txt_nodes])}"
        txt = txt.replace(", TF=", ",\n\tTF=")  # prettify

        return txt

    def is_node(self, n: Union[Node, int]) -> bool:
        """
        Returns True if n is one of the line's nodes.

        Parameters
        ----------
        n : Node or int
            Node or node ID to check.

        Returns
        -------
        bool
            True if the node is part of the line, False otherwise.
        """
        if isinstance(n, Node):
            node_id = n.id
        else:
            node_id = n
        return node_id in [n.id for n in self.nodes]

    def is_stop(self, n: Union[Node, int]) -> bool:
        """
        Returns True if line stops at n.

        Parameters
        ----------
        n : Node or int
            Node or node ID to check.

        Returns
        -------
        bool
            True if the node is a stopping point on the line, False otherwise.
        """
        if isinstance(n, Node):
            node_id = n.id
        else:
            node_id = n
        return node_id in [n.id for n in self.stops]

    @property
    def stop_seq(self, sep: str = "_") -> str:
        """
        Returns a concatenation of line's stops.

        Parameters
        ----------
        sep : str, default="_"
            Separator to use between stop IDs.

        Returns
        -------
        str
            Concatenated string of stop IDs.
        """
        return sep.join([str(n.id) for n in self.stops])

    @staticmethod
    def from_string(string: str, potential_seps: Optional[list[str]] = None) -> "Line":
        """
        Parse a string representation into a line object.

        Parameters
        ----------
        string : str
            String to parse.
        potential_seps : Optional[list[str]], default=None
            List of potential separators to detect.

        Returns
        -------
        Line
            Parsed line object.

        Raises
        ------
        AssertionError
            If invalid node declarations are found.
        """
        if potential_seps is None:
            potential_seps = [" ", "\t", ","]

        # Guess the separator as the most common of potential separators:
        formatted = re.sub(r"[=,][\s\n\t]+", ",", string)  # clean
        # Accounts for multiple separators.
        seps_count = [len(re.findall(f"{sep}+", formatted)) for sep in potential_seps]
        sep = potential_seps[seps_count.index(max(seps_count))]

        # Clean:
        string = string.replace("\n", "")
        string = string.replace("\x1a", "")  # EOF windows >_<
        string = re.sub(r"\ALINE\s+", "", string)
        string = re.sub(r"[\s,]*\Z", "", string)
        if sep == " ":
            string = re.sub(f"{sep}*={sep}*", "=", string)

        # src for this amazing magic:
        # https://stackoverflow.com/a/16710842/2802352
        parts_pat = (
            f"""(?:["](?:\\.|[^"])*["]|['](?:\\.|[^'])*[']|[^{sep}"]|[^{sep}'])+"""
        )
        parts = re.findall(parts_pat, string)

        node_label_pat = r"\A\s*N(?:ODES)?\b"

        nodes = []
        line_attrs = {}
        node_attrs = {}

        n = None
        attrs_section = True

        while parts:
            p = parts.pop(0)

            # Clean:
            p = re.sub(r"[\s,]*\Z", "", p)
            k, _, v = [part.strip() for part in p.partition("=")]

            try:
                # For numbers
                v = ast.literal_eval(v)
            except (ValueError, SyntaxError):
                v = str(v)

            if bool(re.search(f"{node_label_pat}\s*=\s*", p)):
                attrs_section = False

            if attrs_section:
                if k and v:
                    line_attrs.update({k: v})

            else:
                # Replace the node label
                p = re.sub(f"{node_label_pat}\s*=\s*", "", p)

                if "=" in p:
                    if bool(re.search(f"{node_label_pat}", k)):
                        msg = f'Node declaration in attribute "{k}: {v}"'
                        msg += f"in node {n}, line:\n{line_attrs}"
                        raise AssertionError(msg)

                    # Still has '=', must be an attribute:
                    if k and v:
                        node_attrs.update({k: v})

                else:
                    # It is a node:
                    if n:
                        # Add the previous node, with the attrs read so far
                        nodes.append(Node(n, **node_attrs))
                        node_attrs = {}  # reset

                    n = p  # Set the new node for future attrs to be read

        # Add the last node (if it is not empty)
        if n:
            nodes.append(Node(n, **node_attrs))

        ln = Line(nodes, **line_attrs)

        return ln

    def copy(self) -> "Line":
        """
        Create a deep copy of the line.

        Returns
        -------
        Line
            A new instance that is a deep copy of this line.
        """
        return deepcopy(self)


class LineFile:
    """
    Class representing a file of lines.

    A LineFile is a collection of line objects and comments.

    Parameters
    ----------
    content : list of (Line or str), optional
        List of line objects and comment strings.

    Attributes
    ----------
    content : list of (Line or str)
        List containing line objects and comment strings.
    """

    def __init__(self, content: Optional[list[Union[Line, str]]] = None) -> None:
        if content:
            self.content = content
        else:
            self.content = []

    def _warn_if_duplicates(self, additional_info: Optional[str] = None) -> None:
        """
        Raises a warning if there are lines with duplicated NAME in the LineFile.

        Parameters
        ----------
        additional_info : str, optional
            Additional information to include in the warning message.
        """
        if not self.name_unique:
            msg = "Several lines have the same NAME."
            if additional_info:
                msg += f" {additional_info}"
            warn(msg)

    @property
    def content_duplicates_renamed(self) -> list[Union[Line, str]]:
        """
        Returns the LineFile's content with duplicated NAMEs renamed.

        Returns
        -------
        list
            Copy of content with renamed lines.
        """
        renamed_content = []
        counts = Counter(self.line_names)
        suffixes = {k: 1 for k in counts}

        for x in self.content:
            if isinstance(x, Line):
                name = str(x.name)  # Treats int = str
                if counts[name] > 1:
                    x = x.copy()
                    newname = f"{name}_{suffixes[name]}"
                    suffixes[name] += 1
                    x.name = newname
            renamed_content.append(x)

        # re-test (recursive)
        ren_sys = LineFile(renamed_content)
        if not ren_sys.name_unique:
            renamed_content = ren_sys.content_duplicates_renamed

        return renamed_content

    def rename_duplicates(self) -> None:
        """
        Changes the LineFile's content to avoid lines with duplicated NAMEs.
        """
        self.content = self.content_duplicates_renamed

    @property
    def name_unique(self) -> bool:
        """
        Returns True if lines' property "NAME" is a unique identifier.

        Returns
        -------
        bool
            True if all line names are unique, False otherwise.
        """
        names = self.line_names
        if not names:
            return True
        _, count = Counter(names).most_common(1)[0]
        return not count > 1

    @property
    def comments(self) -> list[str]:
        """
        Returns the list of comments in the file.

        Returns
        -------
        list of str
            All comments in the file.
        """
        return [x for x in self.content if isinstance(x, str)]

    @property
    def lines(self) -> dict[str, Line]:
        """
        Returns a dictionary of lines by NAME.

        Returns
        -------
        Dict[str, Line]
            Dictionary of lines with NAME as key.
        """
        msg = "Only the latest line is displayed for conflicting NAMEs."
        self._warn_if_duplicates(additional_info=msg)
        return {x.name: x for x in self.content if isinstance(x, Line)}

    @property
    def lines_duplicates_renamed(self) -> dict[str, Line]:
        """
        Returns a dictionary of lines with duplicated NAMEs renamed.

        Returns
        -------
        Dict[str, Line]
            Dictionary of lines with NAME as key, duplicates renamed.
        """
        return {
            x.name: x for x in self.content_duplicates_renamed if isinstance(x, Line)
        }

    @property
    def line_names(self) -> list[str]:
        """
        Returns a list of line names as strings.

        Preserves order. May contain duplicates.

        Returns
        -------
        list[str]
            List of line names.
        """
        return [str(x.name) for x in self.content if isinstance(x, Line)]

    def __repr__(self) -> str:
        """
        Object's summary representation.

        Returns
        -------
        str
            String representation summarizing the LineFile.
        """
        self._warn_if_duplicates()
        # Using self.line_names avoids triggering further warnings:
        txt = f"LineFile with {len(self.line_names)} lines, "
        txt += f"and {len(self.comments)} comments."
        txt += "\nLines:\n"
        txt += ", ".join([str(k) for k in self.line_names])  # if int NAMEs
        txt += "\nComments:\n"
        txt += "\n".join(self.comments)
        return txt

    def __str__(
        self,
        sort: bool = False,
        comments: bool = True,
        rename_duplicates: bool = False,
        **kwargs: Any,
    ) -> str:
        """
        Representation as the file itself.

        Parameters
        ----------
        sort : bool, default=False
            If False, output is sorted with the same structure as input content.
            If True, comments are first, then all lines in NAME order.
        comments : bool, default=True
            Output comments only if True.
        rename_duplicates : bool, default=False
            Rename duplicated NAMEs if True.
        **kwargs : dict
            Additional keyword arguments to pass to the line.__str__ method.

        Returns
        -------
        str
            String representation of the LineFile.
        """
        if not rename_duplicates:
            self._warn_if_duplicates()

        if sort:
            lines = self.lines
            # Use only if there are duplicates. Makes code more compact:
            if rename_duplicates and not self.name_unique:
                lines = self.lines_duplicates_renamed

            # Use str() instead of .__str__() directly
            sorted_lines = [lines[ln].__str__(**kwargs) for ln in sorted(lines)]
            txt_lines = "\n".join(sorted_lines)

            if comments:
                txt_comments = "\n".join([c for c in self.comments])
                txt = "\n".join([txt_comments, txt_lines])
            else:
                txt = txt_lines

        else:
            content = self.content
            # Use only if there are duplicates. Makes code more compact:
            if rename_duplicates and not self.name_unique:
                content = self.content_duplicates_renamed

            if comments:
                txt_content = [
                    x.__str__(**kwargs) if not isinstance(x, str) else str(x)
                    for x in content
                ]
            else:
                txt_content = [
                    x.__str__(**kwargs) for x in content if not isinstance(x, str)
                ]

            txt = "\n".join(txt_content)

        return txt

    def copy(self) -> "LineFile":
        """
        Create a deep copy of the LineFile.

        Returns
        -------
        LineFile
            A new instance that is a deep copy of this LineFile.
        """
        return deepcopy(self)

    def save(
        self,
        path: str,
        sort: bool = False,
        comments: bool = True,
        node_attrs: Optional[list[str]] = None,
        exclude_node_attrs: Optional[list[str]] = None,
        line_attrs: Optional[list[str]] = None,
        exclude_line_attrs: Optional[list[str]] = None,
        rename_duplicates: bool = True,
    ) -> None:
        """
        Save the LineFile to a file.

        Parameters
        ----------
        path : str
            Path to the output file.
        sort : bool, default=False
            If True, sorts the output.
        comments : bool, default=True
            If True, includes comments in the output.
        node_attrs : list of str, optional
            List of node attributes to include.
        exclude_node_attrs : list of str, optional
            List of node attributes to omit.
        line_attrs : list of str, optional
            List of line attributes to include.
        exclude_line_attrs : list of str, optional
            List of line attributes to omit.
        rename_duplicates : bool, default=True
            If True, renames duplicate line names.
        """
        if not self.name_unique and rename_duplicates:
            msg = "Duplicated NAMES will be renamed."
            self._warn_if_duplicates(additional_info=msg)

        with open(path, "w", encoding="utf-8") as ofile:
            # Use the method directly instead of the str() built-in
            output = self.__str__(
                sort=sort,
                comments=comments,
                node_attrs=node_attrs,
                exclude_node_attrs=exclude_node_attrs,
                line_attrs=line_attrs,
                exclude_line_attrs=exclude_line_attrs,
                rename_duplicates=rename_duplicates,
            )
            ofile.write(output)

    def lines_by_attr(self, attr: str, val: Any) -> list[Line]:
        """
        Returns a list of lines having a specific value in an attribute.

        Parameters
        ----------
        attr : str
            Attribute name to check.
        val : Any
            Value to match.

        Returns
        -------
        list[Line]
            List of lines that match the criteria.
        """
        lines = [ln for ln in self.lines.values() if getattr(ln, attr) == val]
        return lines

    def lines_query(self, qry: str) -> list[Line]:
        """
        Returns a list of lines meeting a SQL-like query.

        This relies on pandas DataFrame query:
            https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.query.html

        Parameters
        ----------
        qry : str
            SQL-like query string.

        Returns
        -------
        list[Line]
            List of lines that match the query.
        """
        lns_names = self.df.query(qry)["NAME"].tolist()

        if lns_names:
            lns = [self.lines[n] for n in lns_names]
            return lns
        else:
            return []

    @property
    def df(self) -> pd.DataFrame:
        """
        Returns a dataframe with the attributes for each line.

        Returns
        -------
        pd.DataFrame
            DataFrame containing line attributes as columns.
        """
        # Assume lines start on 1:
        data = {i: ln.attrs for i, ln in enumerate(self.lines.values(), 1)}
        df = pd.DataFrame.from_records(data).T

        # stops and nodes are objects!
        additional_attrs = "stop_seq stops nodes".split()
        for attr in additional_attrs:
            df[attr] = [getattr(ln, attr) for ln in self.lines.values()]

        return df

    @staticmethod
    def _extract_blocks(
        string: str,
        block_pat: str = r"(?s)(?:(;.*?|\n\s*)\n|LINE\s+(.*?)(?=\n\s*LINE|\n\s*;|\Z))",
    ) -> list[tuple[str, str]]:
        """
        Returns a list of tuples [(comment, line), (), ...] for each record.

        Parameters
        ----------
        string : str
            Input string to parse.
        block_pat : str, default regex pattern
            Regex pattern to extract blocks.

        Returns
        -------
        List[Tuple[str, str]]
            List of tuples containing (comment, line) pairs.
        """
        block_re = re.compile(block_pat)
        blocks = block_re.findall(string)
        return blocks

    @staticmethod
    def from_string(string: str) -> "LineFile":
        """
        Create a LineFile from a string.

        Parameters
        ----------
        string : str
            String representation of a line file.

        Returns
        -------
        LineFile
            Parsed LineFile object.
        """
        blocks = LineFile._extract_blocks(string)

        content: list[Union[str, Line]] = []
        for comment_txt, line_txt in blocks:
            if comment_txt:
                content.append(comment_txt)

            if line_txt:
                ln = Line.from_string(line_txt)
                content.append(ln)

        s = LineFile(content)

        return s

    @staticmethod
    def read_file(path: str) -> "LineFile":
        """
        Read a line file from disk.

        Parameters
        ----------
        path : str
            Path to the file.

        Returns
        -------
        LineFile
            Parsed LineFile object from the file.
        """
        with open(path, "r", encoding="utf-8") as ifile:
            content = ifile.read()

        s = LineFile.from_string(content)

        return s


##### FUNCTIONS #####
@contextlib.contextmanager
def _temp_run_dir(parent: Path, stem: str, keep: bool = False):
    """
    Context manager for a temporary Voyager run directory.

    Parameters
    ----------
    parent : Path
        Parent directory where the temp folder will be created.
    stem : str
        Prefix / stem for the temp folder name.
    keep : bool
        If True, directory is kept (for debugging).
    """
    if keep:
        path = Path(tempfile.mkdtemp(prefix=f"{stem}_", dir=parent))
        try:
            yield path
        finally:
            # caller decides when to delete
            pass
    else:
        with tempfile.TemporaryDirectory(prefix=f"{stem}_", dir=parent) as td:
            yield Path(td)


def _run_voyager(
    voyager_exe: Path,
    parent_dir: Path,
    script_name: str,
    script_lines: list[str],
    keep_temp: bool = False,
    raise_on_code: int = 2,
) -> subprocess.CompletedProcess:
    """
    Write a Voyager script into a temp directory, execute it, handle cleanup.

    Parameters
    ----------
    voyager_exe : Path
        Path to voyager executable.
    parent_dir : Path
        Directory under which temp folder will be created.
    script_name : str
        Script filename (e.g. 'ParseRoutes.S').
    script_lines : list[str]
        Script body lines.
    keep_temp : bool
        Keep temp directory (debug).
    raise_on_code : int
        Return code that triggers RuntimeError.

    Returns
    -------
    subprocess.CompletedProcess
    """
    # Create temp directory
    stem = Path(script_name).stem
    with _temp_run_dir(parent_dir, stem, keep=keep_temp) as tmp:
        script_path = tmp / script_name
        script_path.write_text("\n".join(script_lines), encoding="utf-8")
        # Execute Voyager
        args = [
            str(voyager_exe.resolve()),
            str(script_path.resolve()),
            "-Pvdmi",
            "/Start",
            "/Hide",
            "/HideScript",
        ]
        proc = subprocess.run(args, capture_output=True, check=False)
        # Check for errors
        if proc.returncode == raise_on_code:
            prn = script_path.with_suffix(".PRN")
            msg = f"Voyager failed (returncode {proc.returncode}). Check: {prn}"
            if not keep_temp:
                # Optionally dump stdout/stderr somewhere else if needed
                pass
            raise RuntimeError(msg)

        return proc


def process_cube_routes(
    voyager_exe: Path,
    routes_print_file: Path,
    outputs_routes_file: Path | None = None,
    keep_temp: bool = False,
) -> None:
    """Parse and format Cube routes.

    Parameters
    ----------
    voyager_exe : Path
        Path to voyager executable
    routes_print_file: Path
        Path to Cube routes file
    outputs_routes_file: Path | None
        Output (CSV/DBF) base path. Defaults to same folder/name as routes_print_file.
    keep_temp : bool
        Keep temp directory (for debugging).
    """
    if outputs_routes_file:
        outputs_part = [
            f'FILEO PRINTO[1] = "{outputs_routes_file.with_suffix(".CSV")}"',
            f'FILEO RECO[1] = "{outputs_routes_file.with_suffix(".DBF")}"',
            "      FIELDS=from_zone_id, to_zone_id, userclass, "
            "count, bundle, L, probability(6.4),",
            "             a_node, b_node, mode, WaitA(6.2), TimeA(6.2), Actual(6.2), "
            "BXFerPen(6.2), Percvd(6.2), LegDist(6.2), TotDist(6.2)",
        ]
    else:
        base = routes_print_file.parent / routes_print_file.stem
        outputs_part = [
            f'FILEO PRINTO[1] = "{base}.CSV"',
            f'FILEO RECO[1] = "{base}.DBF"',
            "      FIELDS=from_zone_id, to_zone_id, userclass, "
            "count, bundle, L, probability(6.4),",
            "             a_node, b_node, mode, WaitA(6.2), TimeA(6.2), Actual(6.2), "
            "BXFerPen(6.2), Percvd(6.2), LegDist(6.2), TotDist(6.2)",
        ]

    script_lines = (
        [
            f'RUN PGM=MATRIX PRNFILE="ParseRoutes_{routes_print_file.stem}.PRN"',
            "; Outputs",
        ]
        + outputs_part
        + [
            "; Inputs",
            f'FILEI RECI = "{routes_print_file}"',
            "",
            "; Process",
            "",
            "MAXSTRINGS=1000",
            "ARRAY TYPE=C999 _LINE_LIST=100",
            "ARRAY _NODE_LIST=100 _MODE_LIST=100 _WAITA_LIST=100 _TimeA_LIST=100 _Actual_LIST=100",
            "ARRAY _BXferPen_LIST=100 _Percvd_LIST=100 _Dist_LIST=100 _Total_LIST=100",
            "",
            "IF(Reci.RecNo=1)",
            "  PRINT  PRINTO=1, CSV=T, LIST='from_stn_zone_id', 'to_stn_zone_id', "
            "'bundle', 'L', 'probability', 'a_node', 'b_node',",
            "                               'mode', 'WaitActual', 'TimeActual', "
            "'TotalActual', 'BrdXFerPen', 'PercvdTime', 'LegDistance', 'TotDistance', 'Services'",
            "ENDIF",
            "",
            "IF (STRPOS('User',RECI)=1)",
            "    _UserClass = _UserClass + 1",
            "    IF(_UserClass > 1)",
            "      _UserClass = 1",
            "    ENDIF",
            "ENDIF",
            "",
            "IF (STRPOS('N:',RECI)=1)",
            "    _COUNTN=1",
            "    _NODE_LIST[_COUNTN]=VAL(TRIM(LTRIM(SUBSTR(RECI,3, STRPOS('Mode',RECI)-3))))",
            "    _ROUTEBUNDLE=_ROUTEBUNDLE+1",
            "ENDIF",
            "IF (STRPOS('->',RECI)=1)",
            "    _COUNTN=_COUNTN+1",
            "    _NODE_LIST[_COUNTN]=VAL(SUBSTR(RECI,3,6))",
            "    _MODE_LIST[_COUNTN]=VAL(SUBSTR(RECI,9,5))",
            "    _WAITA_LIST[_COUNTN]=VAL(SUBSTR(RECI,14,7))",
            "    _TimeA_LIST[_COUNTN]=VAL(SUBSTR(RECI,21,7))",
            "    _Actual_LIST[_COUNTN]=VAL(SUBSTR(RECI,28,7))",
            "    _BXferPen_LIST[_COUNTN]=VAL(SUBSTR(RECI,35,7))",
            "    _Percvd_LIST[_COUNTN]=VAL(SUBSTR(RECI,42,7))",
            "    _Dist_LIST[_COUNTN]=VAL(SUBSTR(RECI,49,7))",
            "    _Total_LIST[_COUNTN]=VAL(SUBSTR(RECI,56,7))",
            "    _LINE_LIST[_COUNTN]=LTRIM(SUBSTR(RECI,65,800))",
            "ENDIF",
            "",
            "IF (STRPOS('Probability=', RECI)=1)",
            "    _ProbTemp = VAL(SUBSTR(RECI,13,800))",
            "",
            "    IF(_ProbTemp>0)",
            "",
            "      RO.probability=VAL(SUBSTR(RECI,13,800))",
            "      LOOP L=1,_COUNTN-1",
            "          RO.from_stn_zone_id=_NODE_LIST[1]",
            "          RO.to_stn_zone_id=_NODE_LIST[_COUNTN]",
            "          RO.userclass = _UserClass",
            "          RO.count = _COUNTN",
            "          RO.bundle=_ROUTEBUNDLE",
            "          RO.a_node=_NODE_LIST[L]",
            "          RO.b_node=_NODE_LIST[L+1]",
            "          RO.mode=_MODE_LIST[L+1]",
            "          RO.WAITA=_WAITA_LIST[L+1]",
            "          RO.TimeA=_TimeA_LIST[L+1]",
            "          RO.Actual=_Actual_LIST[L+1]",
            "          RO.BXferPen=_BXferPen_LIST[L+1]",
            "          RO.Percvd=_Percvd_LIST[L+1]",
            "          RO.LegDist=_Dist_LIST[L+1]",
            "          RO.TotDist=_Total_LIST[L+1]",
            "          WRITE RECO=1",
            "          PRINT CSV=T, LIST=RO.from_stn_zone_id(5.0L), RO.to_stn_zone_id(5.0L), "
            "RO.bundle(5.0L), L(5.0), RO.probability(6.4L), RO.a_node(6.0L), RO.b_node(6.0L),",
            "                          RO.mode(3.0L), RO.WaitA(12.2L), RO.TimeA(12.2L), "
            "RO.Actual(12.2L), RO.BXferPen(12.2L), RO.Percvd(12.2L), RO.LegDist(12.2L), RO.TotDist(12.2L),",
            "                          _LINE_LIST[L+1](L999) PRINTO=1",
            "      ENDLOOP",
            "    ENDIF",
            "    _COUNTN=0",
            "ENDIF",
            "",
            "IF (STRPOS('REval Route(s)', RECI)>0)",
            "    _ROUTEBUNDLE=0",
            "ENDIF",
            "ENDRUN",
        ]
    )

    _run_voyager(
        voyager_exe=voyager_exe,
        parent_dir=routes_print_file.parent,
        script_name=f"ParseRoutes_{routes_print_file.stem}.S",
        script_lines=script_lines,
        keep_temp=keep_temp,
    )


def network_to_shapefile(
    voyager_exe: Path,
    network_file: Path,
    nodes_file: Path | None = None,
    links_file: Path | None = None,
    projection_string: Optional[str] = None,
    keep_temp: bool = False,
) -> None:
    """Export Cube network to Links and Nodes shapefiles.

    Parameters
    ----------
    voyager_exe : Path
        Path to voyager executable
    network_file: Path
        Path to run folder
    nodes_file: Path | None
        Path to nodes shapefile
    links_file: Path | None
        Path to links shapefile
    projection_string: Optional[str]
        projection string to use for shapefiles
    keep_temp: bool
        whether to keep temporary files

    Raises
    ------
    RuntimeError
        When Cube fails
    """
    if nodes_file:
        nodes_file_str = f"{nodes_file.with_suffix('')}.SHP"
    else:
        nodes_file_str = f"{network_file.with_suffix('')}_Nodes.SHP"
    if links_file:
        links_file_str = f"{links_file.with_suffix('')}.SHP"
    else:
        links_file_str = f"{network_file.with_suffix('')}_Links.SHP"

    script_lines = [
        f'RUN PGM=NETWORK PRNFILE="ConvertNetwork_{network_file.stem}.PRN"',
        "; Outputs",
        f'FILEO NODEO = "{nodes_file_str}",',
        "     FORMAT=SHP",
        f'FILEO LINKO = "{links_file_str}",',
        "     FORMAT=SHP",
        "; Inputs",
        f'FILEI LINKI[1] = "{network_file.resolve()}"',
        "; Process",
        "",
        "PROCESS PHASE = NODEMERGE",
        "   GEOMETRYSOURCE=1",
        "ENDPROCESS",
        "",
        "PROCESS PHASE = LINKMERGE",
        "   GEOMETRYSOURCE=1",
        "ENDPROCESS",
        "",
        "ENDRUN",
    ]

    _run_voyager(
        voyager_exe=voyager_exe,
        parent_dir=network_file.parent,
        script_name=f"ConvertNetwork_{network_file.stem}.S",
        script_lines=script_lines,
        keep_temp=keep_temp,
    )

    if projection_string:
        (network_file.parent / f"{Path(nodes_file_str).stem}.PRJ").write_text(
            projection_string, encoding="utf-8"
        )
        (network_file.parent / f"{Path(links_file_str).stem}.PRJ").write_text(
            projection_string, encoding="utf-8"
        )


def network_to_csvs(
    voyager_exe: Path,
    network_file: Path,
    nodes_file: Path | None = None,
    links_file: Path | None = None,
    keep_temp: bool = False,
) -> None:
    """Export Cube network to Links and Nodes CSVs.

    Parameters
    ----------
    voyager_exe : Path
        Path to voyager executable
    network_file: Path
        Path to run folder
    nodes_file: Path | None
        Path to nodes CSV
    links_file: Path | None
        Path to links CSV
    keep_temp: bool = False
        whether to keep temporary files

    Raises
    ------
    RuntimeError
        When Cube fails
    """
    if nodes_file:
        nodes_file_str = f"{nodes_file.with_suffix('')}.CSV"
    else:
        nodes_file_str = f"{network_file.with_suffix('')}_Nodes.CSV"
    if links_file:
        links_file_str = f"{links_file.with_suffix('')}.CSV"
    else:
        links_file_str = f"{network_file.with_suffix('')}_Links.CSV"

    script_lines = [
        f'RUN PGM=NETWORK PRNFILE="ConvertNetwork_{network_file.stem}.PRN"',
        "; Outputs",
        f'FILEO NODEO = "{nodes_file_str}",',
        '     FORMAT=TXT, DELIMITER=","',
        f'FILEO LINKO = "{links_file_str}",',
        '     FORMAT=TXT, DELIMITER=","',
        "; Inputs",
        f'FILEI LINKI[1] = "{network_file.resolve()}"',
        "; Process",
        "",
        "ENDRUN",
    ]

    _run_voyager(
        voyager_exe=voyager_exe,
        parent_dir=network_file.parent,
        script_name=f"ConvertNetwork_{network_file.stem}.S",
        script_lines=script_lines,
        keep_temp=keep_temp,
    )


def build_network_from_csvs(
    voyager_exe: Path,
    links_file: Path,
    nodes_file: Path,
    network_path: Path,
    links_var: list[str],
    nodes_var: list[str],
    keep_temp: bool = False,
) -> None:
    """Build Cube network from links and nodes CSVs.

    Parameters
    ----------
    voyager_exe : Path
        Path to voyager executable
    links_file: Path
        Path to links CSV
    nodes_file: Path
        Path to nodes CSV
    network_path: Path
        Path to network folder
    links_var: list[str]
        List of Links csv variables, must include "A" and "B"
    nodes_var: list[str]
        List of Nodes csv variables, must include "N", "X" and "Y"
    keep_temp: bool = False
        whether to keep temporary files

    Raises
    ------
    RuntimeError
        When Cube fails
    """
    script_lines = [
        f'RUN PGM=NETWORK PRNFILE="CreateNetwork_{network_path.stem}.PRN"',
        "; Outputs",
        f'FILEO NETO = "{network_path.with_suffix(".NET")}"',
        "; Inputs",
        f'FILEI LINKI[1] = "{links_file.with_suffix(".CSV")}",',
        f"      VAR={', '.join([f'"{item}"' for item in links_var])}",
        f'FILEI NODEI[1] = "{nodes_file.with_suffix(".CSV")}",',
        f"      VAR={', '.join([f'"{item}"' for item in nodes_var])}",
        "; Process",
        "",
        "ENDRUN",
    ]

    _run_voyager(
        voyager_exe=voyager_exe,
        parent_dir=network_path.parent,
        script_name=f"CreateNetwork_{network_path.stem}.S",
        script_lines=script_lines,
        keep_temp=keep_temp,
    )


def omx_to_mat(
    voyager_exe: Path,
    omx_path: Path,
    mat_path: Path | None = None,
    keep_temp: bool = False,
) -> None:
    """Convert OMX Matrix to Cube MAT matrix.

    Parameters
    ----------
    voyager_exe : Path
        Path to voyager executable
    omx_path : Path
        Path to OMX matrix file
    mat_path: Path | None
        Path to Cube MAT matrix
    keep_temp: bool = False
        whether to keep temporary files

    Raises
    ------
    RuntimeError
        When Cube fails
    """
    if not mat_path:
        mat_path = omx_path.with_suffix(".MAT")

    script_lines = [
        f'CONVERTMAT FROM="{omx_path.with_suffix(".OMX")}" '
        f'TO="{mat_path.with_suffix(".MAT")}" FORMAT=TPP COMPRESSION=0'
    ]

    _run_voyager(
        voyager_exe=voyager_exe,
        parent_dir=omx_path.parent,
        script_name=f"Convert_OMX2MAT_{omx_path.stem}.S",
        script_lines=script_lines,
        keep_temp=keep_temp,
    )


def mat_to_omx(
    voyager_exe: Path,
    mat_path: Path,
    omx_path: Path | None = None,
    compression: int = 0,
    keep_temp: bool = False,
) -> None:
    """Convert Cube .MAT to OMX Matrix

    Parameters
    ----------
    voyager_exe : Path
        Path to voyager executable
    mat_path: Path
        Path to Cube MAT matrix
    omx_path : Path | None
        Path to OMX matrix file
    compression: int, default 0
        Compression level of output matrix
    keep_temp: bool = False
        whether to keep temporary files

    Raises
    ------
    RuntimeError
        When Cube fails
    """
    if not omx_path:
        omx_path = mat_path.with_suffix(".OMX")

    script_lines = [
        f'CONVERTMAT FROM="{mat_path.with_suffix(".MAT")}" '
        f'TO="{omx_path.with_suffix(".OMX")}" FORMAT=OMX COMPRESSION={compression}'
    ]

    _run_voyager(
        voyager_exe=voyager_exe,
        parent_dir=mat_path.parent,
        script_name=f"Convert_MAT2OMX_{mat_path.stem}.S",
        script_lines=script_lines,
        keep_temp=keep_temp,
    )


def parse_cube_zones_character(
    cube_range: str,
) -> list[Any]:
    """Parse Cube format list of zones/ranges into list of zones

    Parameters
    ----------
    cube_range : str
        range of Cube style list/range of zones

    Returns
    -------
    zones_list : list[Any]
        list of individual zones
    """
    # remove white space
    cube_range = cube_range.replace(" ", "")
    zones = cube_range.split(",")
    zones_list: list[Any] = []

    for zone in zones:
        if "-" in zone:
            # split range
            start, end = map(int, zone.split("-"))
            # create inclusive range
            zones_list.extend(range(start, end + 1))
        else:
            try:
                zones_list.append(int(zone))
            except ValueError:
                zones_list.append(str(zone))

    return zones_list


def parse_sqex_file(
    sqex_file: Path,
    level: str,
    sectors: str,
) -> pl.DataFrame:
    """Read Cube's SQEX file and create a lookup dataframe between zones and sectors.

    NOTE: The function currently assumes a full weighting zones<>sectors.
    i.e. if a zone is split weighted across multiple sectors then the function will
    ignore that and take first appearance.

    Parameters
    ----------
    sqex_file : Path
        path to the sqex file
    level : str
        the zone level either "stn" or "zone"
    sectors : str
        number of sectors

    Returns
    -------
    sqex_df : pl.DataFrame
        stn/zone to sectors lookup
    """
    # read sqex file into a dataframe
    sqex_df = pl.read_csv(
        sqex_file,
        columns=[0, 1],
        has_header=False,
        new_columns=[f"{level}_zone_id", f"Sectors_{sectors}"],
        dtypes=[pl.Int32, pl.Int32],
    )  # type: ignore
    # drop duplicates to remove split weights
    sqex_df = sqex_df.unique()

    return sqex_df


def csv_to_mat(
    voyager_exe: Path,
    zones: int,
    csvs: list[list[str | Path]],
    mat_path: Path,
    remove_csvs: bool = True,
    keep_temp: bool = False,
) -> None:
    """Convert CSVs to CUBE's .MAT format.
    CSVs should have 3 columns: origin, destination and trips,
    with no header row.

    Parameters
    ----------
    zones : int
        Number of zones in the matrix.
    csvs : list[list[str | Path]]
        List of lists containing the CSV file names and paths.
    mat_path : Path
        Output CUBE .mat file to create.
    remove_csvs : bool, optional
        Whether or not to remove the input CSVs after conversion,
        by default True
    keep_temp : bool, optional
        Whether or not to keep temporary files after conversion,
        by default False

    Raises
    ------
    FileNotFoundError
        If any of the input CSVs don't exist.
    """
    for csv in csvs:
        if not Path(csv[1]).is_file():  # type: ignore
            raise FileNotFoundError(f"cannot find CSV: {csv[1]}")

    if mat_path.suffix.lower() != ".mat":
        mat_path = mat_path.with_suffix(".mat")

    script_lines: list[str] = [
        "RUN PGM=MATRIX",
        f'FILEO MATO[1]="{mat_path.resolve()}",',
        f"      mo=1-{len(csvs)},dec={len(csvs)}*d,name="
        + ",".join(str(nm[0]) for nm in csvs),
    ]
    for n, csv in enumerate(csvs, start=1):
        script_lines.append(f'FILEI MATI[{n}]="{Path(csv[1]).resolve()}",')
        script_lines.append("      fields=#1,2,3, pattern=ij:v")
    script_lines += ["", f"zones={zones}", "fillmw"]
    script_lines += [f"mw[{n}]=mi.{n}.1" for n in range(1, len(csvs) + 1)]
    script_lines += ["", "ENDRUN"]

    _run_voyager(
        voyager_exe=voyager_exe,
        parent_dir=mat_path.parent,
        script_name=f"CSV2MAT_{mat_path.stem}.S",
        script_lines=script_lines,
        keep_temp=keep_temp,
    )

    if not mat_path.is_file():
        raise RuntimeError("error converting CSV to CUBE .mat")

    if remove_csvs:
        for csv in csvs:
            try:
                Path(csv[1]).unlink(missing_ok=True)
            except Exception:
                pass
