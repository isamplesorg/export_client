"""
Convert iSamples GeoParquet exports to PQG (Property Graph) format.

This module provides functionality to transform the nested iSamples data structure
into PQG's node-edge property graph format.
"""

import logging
import hashlib
from typing import Any, Dict, List, Optional, Set
import pandas as pd
import geopandas as gpd

try:
    from pqg import Graph
    PQG_AVAILABLE = True
except ImportError:
    PQG_AVAILABLE = False
    logging.warning("PQG library not available. Install with: pip install pqg")


class ISamplesPQGConverter:
    """
    Converter for transforming iSamples GeoParquet files to PQG format.

    The converter decomposes the nested iSamples structure into individual nodes
    and creates edges to represent relationships between entities.
    """

    def __init__(self, db_path: str = ":memory:"):
        """
        Initialize the PQG converter.

        Args:
            db_path: Path to DuckDB database file (default: in-memory)
        """
        if not PQG_AVAILABLE:
            raise ImportError("PQG library is required. Install with: pip install pqg")

        self.graph = Graph(db_path)
        self.node_pids: Set[str] = set()  # Track created nodes to avoid duplicates

    def _generate_pid(self, prefix: str, data: Dict[str, Any]) -> str:
        """
        Generate a unique PID for a node based on its content.

        Args:
            prefix: Prefix for the PID (e.g., 'site', 'event')
            data: Dictionary of node data

        Returns:
            Unique PID string
        """
        # Create hash from string representation of data
        content = str(sorted(data.items()))
        hash_suffix = hashlib.md5(content.encode()).hexdigest()[:12]
        return f"{prefix}_{hash_suffix}"

    def _add_node_if_not_exists(self, pid: str, otype: str, **kwargs) -> str:
        """
        Add a node to the graph if it doesn't already exist.

        Args:
            pid: Unique identifier for the node
            otype: Object type
            **kwargs: Additional node properties

        Returns:
            The PID of the node
        """
        if pid not in self.node_pids:
            self.graph.addNode(pid=pid, otype=otype, **kwargs)
            self.node_pids.add(pid)
            logging.debug(f"Created node: {otype} - {pid}")
        return pid

    def _extract_location(self, sample_pid: str, location_data: Optional[Dict]) -> Optional[str]:
        """
        Extract and create a Location node from location data.

        Args:
            sample_pid: PID of the parent sample
            location_data: Dictionary containing location information

        Returns:
            PID of the created Location node, or None if no data
        """
        if not location_data or not isinstance(location_data, dict):
            return None

        lat = location_data.get('latitude')
        lon = location_data.get('longitude')
        elev = location_data.get('elevation')

        if lat is None and lon is None and elev is None:
            return None

        location_pid = self._generate_pid('location', location_data)

        self._add_node_if_not_exists(
            pid=location_pid,
            otype='Location',
            label=f"Location ({lat}, {lon})" if lat and lon else "Location",
            latitude=float(lat) if lat is not None else None,
            longitude=float(lon) if lon is not None else None,
            elevation=float(elev) if elev is not None else None
        )

        return location_pid

    def _extract_sampling_site(self, sample_pid: str, site_data: Optional[Dict]) -> Optional[str]:
        """
        Extract and create a SamplingSite node from site data.

        Args:
            sample_pid: PID of the parent sample
            site_data: Dictionary containing sampling site information

        Returns:
            PID of the created SamplingSite node, or None if no data
        """
        if not site_data or not isinstance(site_data, dict):
            return None

        site_pid = self._generate_pid('site', site_data)

        # Extract place names if present
        place_names = site_data.get('place_name', [])
        if isinstance(place_names, list) and place_names:
            place_name_str = ', '.join(str(p) for p in place_names if p)
        else:
            place_name_str = None

        self._add_node_if_not_exists(
            pid=site_pid,
            otype='SamplingSite',
            label=site_data.get('label') or place_name_str or 'Sampling Site',
            description=site_data.get('description'),
            place_names=place_names if place_names else None
        )

        # Create location node if present
        location_data = site_data.get('sample_location')
        if location_data:
            location_pid = self._extract_location(sample_pid, location_data)
            if location_pid:
                self.graph.addEdge(s=site_pid, p='sample_location', o=[location_pid])

        return site_pid

    def _extract_sampling_event(self, sample_pid: str, event_data: Optional[Dict]) -> Optional[str]:
        """
        Extract and create a SamplingEvent node from produced_by data.

        Args:
            sample_pid: PID of the parent sample
            event_data: Dictionary containing sampling event information

        Returns:
            PID of the created SamplingEvent node, or None if no data
        """
        if not event_data or not isinstance(event_data, dict):
            return None

        event_pid = self._generate_pid('event', event_data)

        # Extract result_time
        result_time = event_data.get('result_time')

        self._add_node_if_not_exists(
            pid=event_pid,
            otype='SamplingEvent',
            label=event_data.get('label') or 'Sampling Event',
            description=event_data.get('description'),
            identifier=event_data.get('identifier'),
            result_time=result_time
        )

        # Create sampling site node if present
        site_data = event_data.get('sampling_site')
        if site_data:
            site_pid = self._extract_sampling_site(sample_pid, site_data)
            if site_pid:
                self.graph.addEdge(s=event_pid, p='sampling_site', o=[site_pid])

        # Create agent nodes for responsibility
        responsibility = event_data.get('responsibility', [])
        if isinstance(responsibility, list):
            for resp_data in responsibility:
                if isinstance(resp_data, dict):
                    agent_pid = self._extract_agent(resp_data)
                    if agent_pid:
                        role = resp_data.get('role', 'participant')
                        self.graph.addEdge(s=event_pid, p=f'responsibility_{role}', o=[agent_pid])

        return event_pid

    def _extract_agent(self, agent_data: Optional[Dict]) -> Optional[str]:
        """
        Extract and create an Agent node.

        Args:
            agent_data: Dictionary containing agent information

        Returns:
            PID of the created Agent node, or None if no data
        """
        if not agent_data or not isinstance(agent_data, dict):
            return None

        name = agent_data.get('name')
        if not name:
            return None

        agent_pid = self._generate_pid('agent', agent_data)

        self._add_node_if_not_exists(
            pid=agent_pid,
            otype='Agent',
            label=name,
            name=name,
            role=agent_data.get('role')
        )

        return agent_pid

    def _extract_related_resource(self, resource_data: Optional[Dict]) -> Optional[str]:
        """
        Extract and create a RelatedResource node.

        Args:
            resource_data: Dictionary containing related resource information

        Returns:
            PID of the created RelatedResource node, or None if no data
        """
        if not resource_data or not isinstance(resource_data, dict):
            return None

        target = resource_data.get('target')
        if not target:
            return None

        # Use target as pid if it's a URI, otherwise generate one
        if target.startswith('http://') or target.startswith('https://'):
            resource_pid = target
        else:
            resource_pid = self._generate_pid('resource', resource_data)

        relationship = resource_data.get('relationship', 'related')
        label = resource_data.get('label', target)

        self._add_node_if_not_exists(
            pid=resource_pid,
            otype='RelatedResource',
            label=label,
            target=target,
            relationship_type=relationship
        )

        return resource_pid

    def _extract_curation(self, sample_pid: str, curation_data: Optional[Dict]) -> Optional[str]:
        """
        Extract and create a Curation node.

        Args:
            sample_pid: PID of the parent sample
            curation_data: Dictionary containing curation information

        Returns:
            PID of the created Curation node, or None if no data
        """
        if not curation_data or not isinstance(curation_data, dict):
            return None

        curation_pid = self._generate_pid('curation', curation_data)

        # Extract access constraints if present
        access_constraints = curation_data.get('access_constraints', [])

        self._add_node_if_not_exists(
            pid=curation_pid,
            otype='Curation',
            label=curation_data.get('label') or 'Curation Info',
            description=curation_data.get('description'),
            curation_location=curation_data.get('curation_location'),
            access_constraints=access_constraints if access_constraints else None
        )

        return curation_pid

    def _extract_categories(self, sample_pid: str, category_data: Optional[List],
                           category_type: str) -> List[str]:
        """
        Extract and create Category nodes from category arrays.

        Args:
            sample_pid: PID of the parent sample
            category_data: List of category dictionaries
            category_type: Type of category (specimen, material, context)

        Returns:
            List of PIDs for created Category nodes
        """
        if not category_data or not isinstance(category_data, list):
            return []

        category_pids = []

        for cat in category_data:
            if isinstance(cat, dict):
                label = cat.get('label')
                if label:
                    cat_pid = f"category_{category_type}_{label.lower().replace(' ', '_')}"

                    self._add_node_if_not_exists(
                        pid=cat_pid,
                        otype='Category',
                        label=label,
                        category_type=category_type
                    )

                    category_pids.append(cat_pid)

        return category_pids

    def _process_sample(self, row: pd.Series) -> None:
        """
        Process a single sample row and create all related nodes and edges.

        Args:
            row: Pandas Series representing a sample
        """
        sample_id = row.get('sample_identifier')
        if not sample_id:
            logging.warning("Skipping row with no sample_identifier")
            return

        # Create main Sample node
        label = row.get('label', sample_id)
        description = row.get('description')

        # Extract keywords if present
        keywords_data = row.get('keywords', [])
        keywords = []
        if isinstance(keywords_data, list):
            for kw in keywords_data:
                if isinstance(kw, dict):
                    keyword = kw.get('keyword')
                    if keyword:
                        keywords.append(keyword)

        # Extract informal classification
        informal_class = row.get('informal_classification', [])
        if not isinstance(informal_class, list):
            informal_class = []

        # Extract alternate identifiers for PQG's altids field
        altids = []
        alt_ids_data = row.get('alternate_identifiers', [])
        if isinstance(alt_ids_data, list):
            for alt_id in alt_ids_data:
                if isinstance(alt_id, dict):
                    identifier = alt_id.get('identifier')
                    if identifier:
                        altids.append(str(identifier))

        # Extract related resources, complies_with, and other fields
        related_resources = row.get('related_resource', [])
        if not isinstance(related_resources, list):
            related_resources = []

        complies_with = row.get('complies_with', [])
        if not isinstance(complies_with, list):
            complies_with = []

        # Extract geometry as WKT if present
        geometry_wkt = None
        if hasattr(row, 'geometry') and row.geometry is not None:
            try:
                geometry_wkt = row.geometry.wkt
            except Exception:
                # Geometry conversion failed - continue without geometry
                # (Some records may have malformed or unsupported geometry types)
                pass

        # Use source_collection as named graph
        named_graph = row.get('source_collection')

        self._add_node_if_not_exists(
            pid=sample_id,
            otype='Sample',
            label=label,
            description=description,
            altids=altids if altids else None,
            keywords=keywords if keywords else None,
            informal_classification=informal_class if informal_class else None,
            source_collection=named_graph,
            sampling_purpose=row.get('sampling_purpose'),
            complies_with=complies_with if complies_with else None,
            dc_rights=row.get('dc_rights'),
            geometry_wkt=geometry_wkt,
            n=named_graph  # Use source_collection as named graph
        )

        # Process produced_by -> SamplingEvent
        produced_by = row.get('produced_by')
        if produced_by:
            event_pid = self._extract_sampling_event(sample_id, produced_by)
            if event_pid:
                self.graph.addEdge(s=sample_id, p='produced_by', o=[event_pid])

        # Process curation
        curation = row.get('curation')
        if curation:
            curation_pid = self._extract_curation(sample_id, curation)
            if curation_pid:
                self.graph.addEdge(s=sample_id, p='curation', o=[curation_pid])

        # Process registrant
        registrant = row.get('registrant')
        if registrant:
            registrant_pid = self._extract_agent(registrant)
            if registrant_pid:
                self.graph.addEdge(s=sample_id, p='registrant', o=[registrant_pid])

        # Process categories
        for cat_field, cat_type in [
            ('has_specimen_category', 'specimen'),
            ('has_material_category', 'material'),
            ('has_context_category', 'context')
        ]:
            cat_data = row.get(cat_field)
            cat_pids = self._extract_categories(sample_id, cat_data, cat_type)
            if cat_pids:
                self.graph.addEdge(s=sample_id, p=cat_field, o=cat_pids)

        # Process related resources
        if related_resources:
            for resource_data in related_resources:
                if isinstance(resource_data, dict):
                    resource_pid = self._extract_related_resource(resource_data)
                    if resource_pid:
                        relationship = resource_data.get('relationship', 'related_to')
                        self.graph.addEdge(s=sample_id, p=f'related_{relationship}', o=[resource_pid])

    def convert_parquet_to_pqg(self, parquet_file: str, output_file: str) -> None:
        """
        Convert an iSamples GeoParquet file to PQG format.

        Args:
            parquet_file: Path to input GeoParquet file
            output_file: Path to output PQG Parquet file
        """
        logging.info(f"Reading GeoParquet file: {parquet_file}")

        # Read the GeoParquet file
        gdf = gpd.read_parquet(parquet_file)

        logging.info(f"Processing {len(gdf)} samples")

        # Initialize the graph
        self.graph.initialize()

        # Process each sample
        for idx, row in gdf.iterrows():
            self._process_sample(row)

            if (idx + 1) % 100 == 0:
                logging.info(f"Processed {idx + 1} samples")

        # Commit changes
        self.graph.db.commit()

        logging.info(f"Created {len(self.node_pids)} unique nodes")

        # Export to Parquet
        logging.info(f"Exporting to PQG Parquet: {output_file}")
        self.graph.toParquet(output_file)

        logging.info("Conversion complete!")

    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics about the converted graph.

        Returns:
            Dictionary with node and edge counts by type
        """
        # Query node counts by type
        result = self.graph.db.execute("""
            SELECT otype, COUNT(*) as count
            FROM node
            WHERE s IS NULL  -- Only count nodes, not edges
            GROUP BY otype
            ORDER BY count DESC
        """).fetchall()

        stats = {'nodes_by_type': {row[0]: row[1] for row in result}}

        # Query edge counts by predicate
        result = self.graph.db.execute("""
            SELECT p, COUNT(*) as count
            FROM node
            WHERE s IS NOT NULL  -- Only count edges
            GROUP BY p
            ORDER BY count DESC
        """).fetchall()

        stats['edges_by_type'] = {row[0]: row[1] for row in result}

        return stats


def convert_isamples_to_pqg(input_file: str, output_file: str,
                            db_path: str = ":memory:") -> Dict[str, Any]:
    """
    Convert an iSamples GeoParquet export to PQG format.

    Args:
        input_file: Path to input GeoParquet file
        output_file: Path to output PQG Parquet file
        db_path: Path to DuckDB database (default: in-memory)

    Returns:
        Dictionary with conversion statistics
    """
    converter = ISamplesPQGConverter(db_path=db_path)
    converter.convert_parquet_to_pqg(input_file, output_file)
    return converter.get_stats()
