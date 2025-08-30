"""
Provides functionality for parsing, manipulating, and visualizing
MATSim network XML files. Handles conversion between XML and graph representations.
"""

##### IMPORTS #####
# Standard imports
import gzip
from pathlib import Path
import xml.etree.ElementTree as ET
from typing import Optional, Any, Union

# Third-party imports
import polars as pl
import networkx as nx  # type: ignore


##### CONSTANTS #####
DEFAULT_CRS = "EPSG:4326"  # Default coordinate reference system
##### GLOBALS #####


##### CLASSES #####
class NetworkParser:
    """Class for parsing, manipulating and visualizing MATSim network files."""

    def __init__(self, filepath: Optional[Union[str, Path]] = None):
        """Initialize the NetworkParser.

        Parameters
        ----------
        filepath : Optional[Union[str, Path]], default None
            Optional path to a MATSim network XML file. Can be .xml or .xml.gz.
        """
        self.filepath = Path(filepath) if filepath else None
        self.nodes: dict[str, dict[str, Any]] = {}  # Dictionary to store node data
        self.links: dict[str, dict[str, Any]] = {}  # Dictionary to store link data
        self.graph = nx.DiGraph()  # Directed graph representation
        self.attributes: dict[str, Any] = {}  # Dictionary to store network attributes

        if filepath and Path(filepath).exists():
            self.read_network(filepath)

    def _is_gzipped(self, filepath: Path) -> bool:
        """Check if a file is gzipped.

        Parameters
        ----------
        filepath : Path
            Path to the file to check

        Returns
        -------
        bool
            True if the file is gzipped, False otherwise
        """
        return filepath.name.endswith(".gz")

    def read_network(self, filepath: Optional[Union[str, Path]] = None) -> nx.DiGraph:
        """Read a MATSim network XML file and parse it into a NetworkX graph.

        Supports both plain XML and gzipped XML files (.xml.gz).
        Preserves all attributes from the XML file, allowing for custom attributes
        beyond the standard MATSim ones.

        Parameters
        ----------
        filepath : Optional[Union[str, Path]], default None
            Path to the MATSim network XML file.

        Returns
        -------
        nx.DiGraph
            A NetworkX directed graph representing the network.

        Raises
        ------
        ValueError
            When no filepath is provided.
        FileNotFoundError
            When the specified file doesn't exist.
        """
        if filepath:
            self.filepath = Path(filepath)

        if not self.filepath:
            raise ValueError("No filepath provided for reading network.")

        if not self.filepath.exists():
            raise FileNotFoundError(f"Network file not found: {self.filepath}")

        # Parse XML from file (handle gzipped files)
        if self._is_gzipped(self.filepath):
            with gzip.open(self.filepath, "rb") as f:
                tree = ET.parse(f)
        else:
            tree = ET.parse(self.filepath)

        root = tree.getroot()

        # Parse network attributes
        self.attributes = {}

        # Get network name if present
        if "name" in root.attrib:
            self.attributes["name"] = root.attrib["name"]

        # Parse attributes element if it exists
        for attrs_elem in root.findall("./attributes"):
            for attr_elem in attrs_elem.findall("./attribute"):
                attr_name = attr_elem.get("name", "")
                if attr_name:
                    # Try to get the text content
                    attr_value = attr_elem.text
                    if attr_value is not None:
                        # Handle common conversions
                        if attr_value.lower() == "true":
                            attr_value = True
                        elif attr_value.lower() == "false":
                            attr_value = False
                        else:
                            try:
                                # Try converting to number
                                attr_value = float(attr_value)
                                # Convert to int if it's a whole number
                                if attr_value.is_integer():
                                    attr_value = int(attr_value)
                            except (ValueError, TypeError):
                                # Keep as string
                                pass

                        self.attributes[attr_name] = attr_value

        # Set default CRS if not found
        if "coordinateReferenceSystem" not in self.attributes:
            self.attributes["coordinateReferenceSystem"] = DEFAULT_CRS

        # Set attributes on the graph
        for key, value in self.attributes.items():
            self.graph.graph[key] = value

        # Parse nodes
        self.nodes = {}
        for node_elem in root.findall(".//node"):
            node_id = node_elem.get("id", "")
            if not node_id:
                continue

            # Create a dictionary with all attributes from the node element
            node_data = {"id": node_id}

            # Add all attributes from the XML element
            for attr_name, attr_value in node_elem.attrib.items():
                if attr_name == "id":
                    continue  # Skip id since we already added it

                # Try to convert numeric values
                try:
                    # Convert to float if it looks like a number
                    attr_value = float(attr_value)
                except (ValueError, TypeError):
                    # Keep as string if not a number
                    pass

                node_data[attr_name] = attr_value

            # Ensure x and y coordinates are present and are floats
            if "x" in node_data and "y" in node_data:
                x = float(node_data["x"])
                y = float(node_data["y"])
                node_data["x"] = x
                node_data["y"] = y
                node_data["coords"] = (x, y)

            # Parse node attributes if present
            for attrs_elem in node_elem.findall("./attributes"):
                for attr_elem in attrs_elem.findall("./attribute"):
                    attr_name = attr_elem.get("name", "")
                    if attr_name:
                        # Try to get the text content
                        attr_value = attr_elem.text
                        if attr_value is not None:
                            # Handle common conversions
                            if attr_value.lower() == "true":
                                attr_value = True
                            elif attr_value.lower() == "false":
                                attr_value = False
                            else:
                                try:
                                    # Try converting to number
                                    attr_value = float(attr_value)
                                    # Convert to int if it's a whole number
                                    if attr_value.is_integer():
                                        attr_value = int(attr_value)
                                except (ValueError, TypeError):
                                    # Keep as string
                                    pass

                            node_data[attr_name] = attr_value

            self.nodes[node_id] = node_data

            # Add node to graph with all attributes
            self.graph.add_node(
                node_id, **{k: v for k, v in node_data.items() if k != "coords"}
            )

        # Parse links
        self.links = {}
        for link_elem in root.findall(".//link"):
            link_id = link_elem.get("id", "")
            if not link_id:
                continue

            from_node = link_elem.get("from", "")
            to_node = link_elem.get("to", "")
            if not from_node or not to_node:
                continue

            # Create a dictionary with all attributes from the link element
            link_data = {"id": link_id, "from_node": from_node, "to_node": to_node}

            # Add all attributes from the XML element
            for attr_name, attr_value in link_elem.attrib.items():
                if attr_name in ["id", "from", "to"]:
                    continue  # Skip already processed attributes

                # Handle modes specially
                if attr_name == "modes":
                    link_data["modes"] = attr_value.split(",") if attr_value else []  # type: ignore
                    continue

                # Try to convert numeric values
                try:
                    # Convert to float if it looks like a number
                    attr_value = float(attr_value)
                except (ValueError, TypeError):
                    # Keep as string if not a number
                    pass

                link_data[attr_name] = attr_value

            # Parse link attributes if present
            for attrs_elem in link_elem.findall("./attributes"):
                for attr_elem in attrs_elem.findall("./attribute"):
                    attr_name = attr_elem.get("name", "")
                    if attr_name:
                        # Try to get the text content
                        attr_value = attr_elem.text
                        if attr_value is not None:
                            # Handle common conversions
                            if attr_value.lower() == "true":
                                attr_value = True
                            elif attr_value.lower() == "false":
                                attr_value = False
                            else:
                                try:
                                    # Try converting to number
                                    attr_value = float(attr_value)
                                    # Convert to int if it's a whole number
                                    if attr_value.is_integer():
                                        attr_value = int(attr_value)
                                except (ValueError, TypeError):
                                    # Keep as string
                                    pass

                            link_data[attr_name] = attr_value

            # Add standard attributes with default values if not present
            standard_attrs = ["length", "capacity", "freespeed", "permlanes"]
            for attr in standard_attrs:
                if attr not in link_data:
                    link_data[attr] = 0.0 if attr != "permlanes" else 1.0

            # Ensure modes exists
            if "modes" not in link_data:
                link_data["modes"] = []

            self.links[link_id] = link_data

            # Add edge to graph with all attributes
            edge_attrs = {
                k: v for k, v in link_data.items() if k not in ["from_node", "to_node"]
            }
            self.graph.add_edge(from_node, to_node, **edge_attrs)

        return self.graph

    def write_network(
        self, filepath: Optional[Union[str, Path]] = None, compress: bool = False
    ) -> None:
        """Write the current network to a MATSim XML file.

        Supports writing to both plain XML and gzipped XML files (.xml.gz).
        Preserves all custom attributes when writing to XML.

        Parameters
        ----------
        filepath : Optional[Union[str, Path]], default None
            Path where to save the MATSim network XML file.
        compress : bool, default False
            If True, compress the output file using gzip (.xml.gz).

        Raises
        ------
        ValueError
            When no filepath is provided and no default filepath is set.
        """
        if not filepath and not self.filepath:
            raise ValueError("No filepath provided for writing network.")

        output_path = Path(filepath) if filepath else self.filepath

        # Determine if output should be compressed
        # Either explicitly requested or path ends with .gz
        should_compress = compress or (
            output_path.name.endswith(".gz") if output_path else False
        )

        # Ensure path has .gz extension if compressing
        if should_compress and not output_path.name.endswith(".gz"):  # type: ignore
            output_path = Path(str(output_path) + ".gz")

        # Create root element
        root = ET.Element("network")

        # Add network name if present
        if "name" in self.attributes:
            root.set("name", str(self.attributes["name"]))

        # Add attributes element if we have network attributes
        network_attrs = {k: v for k, v in self.attributes.items() if k != "name"}
        if network_attrs:
            attrs_elem = ET.SubElement(root, "attributes")
            for attr_name, attr_value in network_attrs.items():
                attr_elem = ET.SubElement(attrs_elem, "attribute")
                attr_elem.set("name", attr_name)

                # Add class attribute for Java types if needed
                if isinstance(attr_value, str):
                    attr_elem.set("class", "java.lang.String")
                elif isinstance(attr_value, bool):
                    attr_elem.set("class", "java.lang.Boolean")
                elif isinstance(attr_value, int):
                    attr_elem.set("class", "java.lang.Integer")
                elif isinstance(attr_value, float):
                    attr_elem.set("class", "java.lang.Double")

                # Set the text value
                attr_elem.text = str(attr_value)

        nodes_elem = ET.SubElement(root, "nodes")
        links_elem = ET.SubElement(root, "links")

        # Add nodes with all attributes
        for node_id, node_data in self.nodes.items():
            # Convert all values to strings for XML
            node_attrs = {}
            for key, value in node_data.items():
                if key not in ["id", "coords"]:  # Skip coords, it's derived
                    node_attrs[key] = str(value)

            # Ensure id is included
            node_attrs["id"] = node_id

            ET.SubElement(nodes_elem, "node", node_attrs)

        # Add links with all attributes
        for link_id, link_data in self.links.items():
            # Convert all values to strings for XML
            link_attrs = {}
            for key, value in link_data.items():
                if key == "from_node":
                    link_attrs["from"] = str(value)
                elif key == "to_node":
                    link_attrs["to"] = str(value)
                elif key == "modes":
                    link_attrs["modes"] = ",".join(value) if value else ""
                elif key != "id":  # Skip id, we'll add it separately
                    link_attrs[key] = str(value)

            # Ensure id is included
            link_attrs["id"] = link_id

            ET.SubElement(links_elem, "link", link_attrs)

        # Create the XML tree
        tree = ET.ElementTree(root)

        # Write to file (plain or compressed)
        if should_compress:
            with gzip.open(output_path, "wb") as f:  # type: ignore
                tree.write(f, encoding="utf-8", xml_declaration=True)
        else:
            tree.write(output_path, encoding="utf-8", xml_declaration=True)  # type: ignore

    def get_crs(self) -> str:
        """Get the coordinate reference system of the network.

        Returns
        -------
        str
            The coordinate reference system (CRS) string, defaults to EPSG:4326 if not specified
        """
        return str(self.attributes.get("coordinateReferenceSystem", DEFAULT_CRS))

    def set_crs(self, crs: str) -> None:
        """Set the coordinate reference system of the network.

        Parameters
        ----------
        crs : str
            The coordinate reference system (CRS) string, e.g., "EPSG:4326"
        """
        self.attributes["coordinateReferenceSystem"] = crs
        self.graph.graph["coordinateReferenceSystem"] = crs

    def get_attributes(self) -> dict[str, Any]:
        """Get all network attributes.

        Returns
        -------
        dict[str, Any]
            Dictionary of network attributes
        """
        return self.attributes.copy()

    def set_attribute(self, name: str, value: Any) -> None:
        """Set a network attribute.

        Parameters
        ----------
        name : str
            Name of the attribute
        value : Any
            Value of the attribute
        """
        self.attributes[name] = value
        self.graph.graph[name] = value

    def get_nodes_df(self) -> pl.DataFrame:
        """Get nodes as a polars DataFrame.

        All node attributes are included in the DataFrame, including any custom attributes.

        Returns
        -------
        pl.DataFrame
            DataFrame with node data
        """
        # Convert dictionary to Polars DataFrame
        if not self.nodes:
            return pl.DataFrame()

        # Get all unique attribute names across all nodes
        all_attributes: set = set()
        for node_data in self.nodes.values():
            all_attributes.update(node_data.keys())

        # Remove 'coords' as it's derived from x and y
        if "coords" in all_attributes:
            all_attributes.remove("coords")

        # Initialize data dictionary with all attributes
        data: dict = {attr: [] for attr in all_attributes}

        # Fill data with values from each node
        for _, node_data in self.nodes.items():
            for attr in all_attributes:
                if attr in node_data:
                    data[attr].append(node_data[attr])
                else:
                    data[attr].append(None)  # Use None for missing attributes

        # create dataframe and order it
        nodes_df = pl.DataFrame(data).select(
            pl.col("id").cast(pl.Utf8),  # Ensure id is string
            pl.col("x").cast(pl.Utf8),  # Ensure from_node is string
            pl.col("y").cast(pl.Utf8),  # Ensure to_node is string
            *[pl.col(attr) for attr in all_attributes if attr not in ["id", "x", "y"]],
        )

        return nodes_df

    def get_links_df(self) -> pl.DataFrame:
        """Get links as a polars DataFrame.

        All link attributes are included in the DataFrame, including any custom attributes.

        Returns
        -------
        pl.DataFrame
            DataFrame with link data
        """
        if not self.links:
            return pl.DataFrame()

        # Get all unique attribute names across all links
        all_attributes: set = set()
        for link_data in self.links.values():
            all_attributes.update(link_data.keys())

        # Initialize data dictionary with all attributes
        data: dict = {attr: [] for attr in all_attributes}

        # Fill data with values from each link
        for _, link_data in self.links.items():
            for attr in all_attributes:
                if attr in link_data:
                    data[attr].append(link_data[attr])
                else:
                    data[attr].append(None)  # Use None for missing attributes
        # create dataframe and order it
        links_df = pl.DataFrame(data).select(
            pl.col("id").cast(pl.Utf8),  # Ensure id is string
            pl.col("from_node").cast(pl.Utf8),  # Ensure from_node is string
            pl.col("to_node").cast(pl.Utf8),  # Ensure to_node is string
            *[
                pl.col(attr)
                for attr in all_attributes
                if attr not in ["id", "from_node", "to_node"]
            ],
        )
        return links_df

    def update_from_dfs(
        self, links_df: pl.DataFrame, nodes_df: Optional[pl.DataFrame] = None
    ) -> None:
        """Update the network from modified polars DataFrames.

        This allows you to make changes to the network data using polars operations,
        then synchronize those changes back to the NetworkParser's internal representation.
        Preserves all custom attributes in both nodes and links.

        Parameters
        ----------
        links_df : pl.DataFrame
            DataFrame containing the updated link data. Must contain at least 'id',
            'from_node', and 'to_node' columns.
        nodes_df : Optional[pl.DataFrame], default None
            Optional DataFrame containing the updated node data. Must contain at least
            'id', 'x', and 'y' columns.

        Raises
        ------
        ValueError
            When required columns are missing from the DataFrames
        """
        # Validate required columns in links_df
        required_link_cols = ["id", "from_node", "to_node"]
        for col in required_link_cols:
            if col not in links_df.columns:
                raise ValueError(
                    f"Required column '{col}' missing from links DataFrame"
                )

        # Update from nodes_df if provided
        if nodes_df is not None:
            # Validate required columns in nodes_df
            required_node_cols = ["id", "x", "y"]
            for col in required_node_cols:
                if col not in nodes_df.columns:
                    raise ValueError(
                        f"Required column '{col}' missing from nodes DataFrame"
                    )

            # Create new nodes dictionary
            new_nodes = {}
            for row in nodes_df.iter_rows(named=True):
                node_id = str(row["id"])

                # Add all columns as attributes
                node_data = {"id": node_id}
                for col in nodes_df.columns:
                    if col != "id":  # Skip id as we already added it
                        node_data[col] = row[col]

                # Ensure x and y are present and add coords
                if "x" in node_data and "y" in node_data:
                    x = float(node_data["x"])
                    y = float(node_data["y"])
                    node_data["coords"] = (x, y)  # type: ignore

                new_nodes[node_id] = node_data

            # Replace the existing nodes dictionary
            self.nodes = new_nodes

        # Create new links dictionary
        new_links = {}
        for row in links_df.iter_rows(named=True):
            link_id = str(row["id"])
            from_node = str(row["from_node"])
            to_node = str(row["to_node"])

            # Add all columns as attributes
            link_data = {"id": link_id, "from_node": from_node, "to_node": to_node}
            for col in links_df.columns:
                if col not in [
                    "id",
                    "from_node",
                    "to_node",
                ]:  # Skip already added columns
                    link_data[col] = row[col]

            # Handle modes specially if present
            if "modes" in link_data:
                modes = link_data["modes"]
                # Handle different ways modes might be stored
                if isinstance(modes, str):
                    link_data["modes"] = modes.split(",")  # type: ignore
                elif not isinstance(modes, list):
                    link_data["modes"] = []

            new_links[link_id] = link_data

        # Replace the existing links dictionary
        self.links = new_links

        # Rebuild the graph with updated data
        self._rebuild_graph()

    def from_dataframes(
        self,
        nodes_df: pl.DataFrame,
        links_df: pl.DataFrame,
        attributes: Optional[dict[str, Any]] = None,
    ) -> None:
        """Create a network from nodes and links DataFrames.

        This method allows you to completely create or replace a network using
        polars DataFrames for nodes and links.

        Parameters
        ----------
        nodes_df : pl.DataFrame
            DataFrame containing node data. Must contain at least 'id', 'x', and 'y' columns.
        links_df : pl.DataFrame
            DataFrame containing link data. Must contain at least 'id', 'from_node', and
            'to_node' columns.
        attributes : Optional[dict[str, Any]], default None
            Optional dictionary of network attributes, including coordinateReferenceSystem

        Raises
        ------
        ValueError
            When required columns are missing from the DataFrames
        """
        # Reset the current network
        self.nodes = {}
        self.links = {}
        self.graph = nx.DiGraph()

        # Set network attributes
        if attributes:
            self.attributes = attributes.copy()

            # Ensure CRS is set
            if "coordinateReferenceSystem" not in self.attributes:
                self.attributes["coordinateReferenceSystem"] = DEFAULT_CRS

            # Set attributes on the graph
            for key, value in self.attributes.items():
                self.graph.graph[key] = value
        else:
            # Initialize with default attributes
            self.attributes = {"coordinateReferenceSystem": DEFAULT_CRS}
            self.graph.graph["coordinateReferenceSystem"] = DEFAULT_CRS

        # Update with the new data
        self.update_from_dfs(links_df, nodes_df)

    @classmethod
    def create_from_dataframes(
        cls,
        nodes_df: pl.DataFrame,
        links_df: pl.DataFrame,
        attributes: Optional[dict[str, Any]] = None,
    ) -> "NetworkParser":
        """Create a new NetworkParser instance from nodes and links DataFrames.

        This is a convenience class method to create a network directly from DataFrames
        without needing to first create an empty NetworkParser instance.

        Parameters
        ----------
        nodes_df : pl.DataFrame
            DataFrame containing node data. Must contain at least 'id', 'x', and 'y' columns.
        links_df : pl.DataFrame
            DataFrame containing link data. Must contain at least 'id', 'from_node', and
            'to_node' columns.
        attributes : Optional[dict[str, Any]], default None
            Optional dictionary of network attributes, including coordinateReferenceSystem

        Returns
        -------
        NetworkParser
            A new NetworkParser instance with the network built from the DataFrames

        Raises
        ------
        ValueError
            When required columns are missing from the DataFrames
        """
        network = cls()
        network.from_dataframes(nodes_df, links_df, attributes)
        return network

    def add_node(self, node_id: str, x: float, y: float, **attributes) -> None:
        """Add a new node to the network with arbitrary attributes.

        Parameters
        ----------
        node_id : str
            Unique identifier for the node
        x : float
            X-coordinate of the node
        y : float
            Y-coordinate of the node
        **attributes
            Any additional attributes to store with the node

        Raises
        ------
        ValueError
            If a node with this ID already exists
        """
        if node_id in self.nodes:
            raise ValueError(f"Node with ID {node_id} already exists")

        # Create node data with all attributes
        node_data = {
            "id": node_id,
            "x": float(x),
            "y": float(y),
            "coords": (float(x), float(y)),
        }
        node_data.update(attributes)

        # Add to nodes dictionary
        self.nodes[node_id] = node_data

        # Add to graph
        self.graph.add_node(
            node_id, **{k: v for k, v in node_data.items() if k != "coords"}
        )

    def _rebuild_graph(self) -> None:
        """Rebuild the NetworkX graph from current nodes and links.

        This is called after updating the network data to ensure the graph
        reflects the current state of nodes and links.
        """
        # Create a new graph
        new_graph = nx.DiGraph()

        # Add nodes
        for node_id, node_data in self.nodes.items():
            new_graph.add_node(
                node_id, x=node_data.get("x", 0), y=node_data.get("y", 0)
            )

        # Add edges
        for _, link_data in self.links.items():
            from_node = link_data.get("from_node", "")
            to_node = link_data.get("to_node", "")

            # Skip invalid links
            if (
                not from_node
                or not to_node
                or from_node not in self.nodes
                or to_node not in self.nodes
            ):
                continue
            # Extract standard attributes if available
            edge_attrs = {
                k: v for k, v in link_data.items() if k not in ["from_node", "to_node"]
            }

            # Add the edge with all its attributes
            new_graph.add_edge(from_node, to_node, **edge_attrs)

        # Replace the old graph
        self.graph = new_graph


##### FUNCTIONS #####
def load_network(filepath: Union[str, Path]) -> NetworkParser:
    """Load a MATSim network file.

    Supports both plain XML and gzipped XML files (.xml.gz).

    Parameters
    ----------
    filepath : Union[str, Path]
        Path to the MATSim network XML file (can be .xml or .xml.gz)

    Returns
    -------
    NetworkParser
        NetworkParser instance with loaded network

    Raises
    ------
    FileNotFoundError
        When the specified file doesn't exist
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Network file not found: {filepath}")

    return NetworkParser(filepath)
