#!/usr/bin/env python3

"""
Canonical Domain and Relationship Extraction Service

This script provides a comprehensive solution for extracting, aggregating, and
normalizing government web relationships from scan data.

Key Features:
1. Extract relationships from HTML (links, scripts, styles, forms)
2. Aggregate and deduplicate observations by domain relationships
3. Build canonical domain records following institutional evidence precedence
4. Generate partitioned static JSON datasets
5. Provide CLI interface for batch processing

The implementation reuses the existing MultiScanner for HTML fetching to avoid
redundant HTTP requests while supporting the RelationshipScanner for extraction
of links, scripts, stylesheets, fonts, images, and forms from fetched HTML.

Installation: uv venv && source .venv/bin/activate
Usage: python3 -m src.cli.scan_relationships --help
"""
