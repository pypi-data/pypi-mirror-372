from typing import Any, Dict, List
import yaml
from tabulate import tabulate
import json

class OutputFormatter:
    """Base class for output formatters"""
    @staticmethod
    def format(data: Any) -> str:
        raise NotImplementedError

class JsonFormatter(OutputFormatter):
    @staticmethod
    def format(data: Any) -> str:
        return json.dumps(data, indent=2)

class YamlFormatter(OutputFormatter):
    @staticmethod
    def format(data: Any) -> str:
        return yaml.dump(data, sort_keys=False)

class TableFormatter(OutputFormatter):
    @staticmethod
    def format(data: Any) -> str:
        if isinstance(data, dict):
            if 'processes' in data:  # Handle paginated process list
                return tabulate(
                    [[p['id'], p['name']] for p in data['processes']],
                    headers=['ID', 'Name'],
                    tablefmt='grid'
                )
            elif 'metadataSet' in data:  # Handle process details
                metadata = [[m['name'], m['value']] for m in data['metadataSet']]
                parameters = [[p['name'], p['value'], p['units']] for p in data['parameterSet']]
                
                return (
                    f"Process: {data['name']}\n\n"
                    f"Metadata:\n{tabulate(metadata, headers=['Name', 'Value'], tablefmt='grid')}\n\n"
                    f"Parameters:\n{tabulate(parameters, headers=['Name', 'Value', 'Units'], tablefmt='grid')}"
                )
        elif isinstance(data, list):  # Handle simple lists (teams, collections)
            if data and isinstance(data[0], dict):
                headers = data[0].keys()
                rows = [item.values() for item in data]
                return tabulate(rows, headers=headers, tablefmt='grid')
        
        return str(data)  # Fallback for unknown formats

class TextFormatter(OutputFormatter):
    @staticmethod
    def format(data: Any) -> str:
        if isinstance(data, dict):
            if 'processes' in data:  # Handle paginated process list
                result = [f"Total processes: {data['totalCount']}"]
                for p in data['processes']:
                    result.append(f"Process: {p['name']} (ID: {p['id']})")
                return "\n".join(result)
            elif 'metadataSet' in data:  # Handle process details
                result = [
                    f"Process: {data['name']}",
                    f"Description: {data['description']}",
                    f"Creation Date: {data['creationDate']}",
                    f"Start Time: {data['startTime']}",
                    "\nMetadata:"
                ]
                for meta in data['metadataSet']:
                    result.append(f"  {meta['name']}: {meta['value']}")
                result.append("\nParameters:")
                for param in data['parameterSet']:
                    result.append(f"  {param['name']}: {param['value']} {param['units'] or ''}")
                return "\n".join(result)
        elif isinstance(data, list):  # Handle simple lists (teams, collections)
            return "\n".join(f"{item['name']} (ID: {item['id']})" for item in data)
        
        return str(data)  # Fallback for unknown formats

FORMATTERS = {
    'json': JsonFormatter,
    'yaml': YamlFormatter,
    'table': TableFormatter,
    'text': TextFormatter,
}
