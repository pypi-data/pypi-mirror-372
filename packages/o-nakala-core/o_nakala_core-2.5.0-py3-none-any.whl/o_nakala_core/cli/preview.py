#!/usr/bin/env python3
"""
NAKALA Metadata Preview and Validation Tool

Provides comprehensive preview, validation, and assistance for researchers
preparing metadata CSV files for NAKALA upload.
"""

import csv
import json
import sys
import os
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Confirm, Prompt
from rich.text import Text

# Import our core utilities
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from o_nakala_core.common.utils import NakalaCommonUtils
from o_nakala_core.common.exceptions import NakalaError

console = Console()


class MetadataEnhancer:
    """Intelligent metadata enhancement based on content analysis."""
    
    def __init__(self):
        self.enhancement_patterns = {
            'images': {
                'keywords': ['images', 'photo', 'picture', 'visual', 'jpg', 'png'],
                'enhanced': {
                    'title_fr': 'Images de Site Web Optimisées',
                    'title_en': 'Optimized Website Images',
                    'desc_fr': "Collection d'images photographiques professionnelles pour documentation de site",
                    'desc_en': 'Collection of professional photographic images for site documentation',
                    'keywords': 'fr:images;photographie;site;documentation|en:images;photography;site;documentation'
                }
            },
            'code': {
                'keywords': ['code', 'script', 'python', 'r', 'analysis', '.py', '.r', 'programming'],
                'enhanced': {
                    'title_fr': "Scripts d'Analyse Professionnels",
                    'title_en': 'Professional Analysis Scripts',
                    'desc_fr': "Scripts Python et R optimisés pour l'analyse de données de recherche avec documentation complète",
                    'desc_en': 'Optimized Python and R scripts for research data analysis with complete documentation',
                    'keywords': 'fr:code;scripts;analyse;recherche;python;r|en:code;scripts;analysis;research;python;r'
                }
            },
            'presentations': {
                'keywords': ['presentation', 'slide', 'conference', 'meeting', 'ppt', 'pptx'],
                'enhanced': {
                    'title_fr': 'Matériaux de Présentation Académiques',
                    'title_en': 'Academic Presentation Materials',
                    'desc_fr': 'Supports de communication pour conférences et réunions académiques professionnels',
                    'desc_en': 'Professional communication materials for academic conferences and meetings',
                    'keywords': 'fr:présentations;académique;conférences;communication|en:presentations;academic;conferences;communication'
                }
            },
            'documents': {
                'keywords': ['document', 'paper', 'report', 'protocol', 'methodology', '.doc', '.pdf', '.md'],
                'enhanced': {
                    'title_fr': 'Documentation de Recherche Complète',
                    'title_en': 'Complete Research Documentation',
                    'desc_fr': 'Documentation académique exhaustive incluant protocoles, méthodologie et analyses',
                    'desc_en': 'Comprehensive academic documentation including protocols, methodology and analyses',
                    'keywords': 'fr:documentation;recherche;protocoles;méthodologie|en:documentation;research;protocols;methodology'
                }
            },
            'data': {
                'keywords': ['data', 'dataset', 'survey', 'results', 'csv', 'excel', 'statistics'],
                'enhanced': {
                    'title_fr': 'Données de Recherche Validées',
                    'title_en': 'Validated Research Data',
                    'desc_fr': 'Jeux de données collectés, traités et validés pour analyse statistique approfondie',
                    'desc_en': 'Data sets collected, processed and validated for in-depth statistical analysis',
                    'keywords': 'fr:données;recherche;analyse;statistiques;validé|en:data;research;analysis;statistics;validated'
                }
            }
        }
    
    def suggest_enhancements(self, csv_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze CSV data and suggest intelligent metadata enhancements."""
        enhancements = {
            'total_entries': len(csv_data),
            'enhanced_entries': 0,
            'suggestions': [],
            'auto_improvements': {}
        }
        
        for i, entry in enumerate(csv_data):
            title = entry.get('title', '').lower()
            file_path = entry.get('file', '').lower()
            description = entry.get('description', '').lower()
            
            # Combine text for analysis
            content_text = f"{title} {file_path} {description}"
            
            # Find matching enhancement pattern
            enhancement_type = self._identify_content_type(content_text)
            
            if enhancement_type:
                enhanced = self.enhancement_patterns[enhancement_type]['enhanced']
                
                # Create enhancement suggestion
                suggestion = {
                    'entry_index': i,
                    'original_title': entry.get('title', 'Untitled'),
                    'content_type': enhancement_type,
                    'enhancements': {
                        'title': f"fr:{enhanced['title_fr']}|en:{enhanced['title_en']}",
                        'description': f"fr:{enhanced['desc_fr']}|en:{enhanced['desc_en']}",
                        'keywords': enhanced['keywords']
                    },
                    'confidence': self._calculate_confidence(content_text, enhancement_type)
                }
                
                enhancements['suggestions'].append(suggestion)
                enhancements['enhanced_entries'] += 1
        
        return enhancements
    
    def _identify_content_type(self, content_text: str) -> Optional[str]:
        """Identify the most likely content type based on keywords."""
        scores = {}
        
        for content_type, pattern in self.enhancement_patterns.items():
            score = 0
            for keyword in pattern['keywords']:
                if keyword in content_text:
                    score += 1
            scores[content_type] = score
        
        # Return the type with highest score, if any matches found
        max_score = max(scores.values()) if scores else 0
        if max_score > 0:
            return max(scores, key=scores.get)
        
        return None
    
    def _calculate_confidence(self, content_text: str, enhancement_type: str) -> float:
        """Calculate confidence score for the enhancement suggestion."""
        keywords = self.enhancement_patterns[enhancement_type]['keywords']
        matches = sum(1 for keyword in keywords if keyword in content_text)
        confidence = min(matches / len(keywords) * 100, 95)  # Cap at 95%
        return round(confidence, 1)
    
    def apply_enhancements(self, csv_data: List[Dict[str, Any]], selected_suggestions: List[int]) -> List[Dict[str, Any]]:
        """Apply selected enhancements to CSV data."""
        enhancements = self.suggest_enhancements(csv_data)
        enhanced_data = csv_data.copy()
        
        for suggestion_index in selected_suggestions:
            if suggestion_index < len(enhancements['suggestions']):
                suggestion = enhancements['suggestions'][suggestion_index]
                entry_index = suggestion['entry_index']
                
                # Apply enhancements to the entry
                enhanced_data[entry_index].update(suggestion['enhancements'])
        
        return enhanced_data


class MetadataValidator:
    """Validates metadata CSV files and provides helpful feedback."""
    
    def __init__(self):
        self.utils = NakalaCommonUtils()
        self.required_fields = {'title', 'type'}
        self.recommended_fields = {'description', 'creator', 'keywords'}
        
    def validate_csv_structure(self, csv_file: str) -> Dict[str, Any]:
        """Validate CSV file structure and return analysis."""
        validation_result = {
            'file_exists': False,
            'readable': False,
            'entries_count': 0,
            'fields_found': [],
            'missing_required': [],
            'missing_recommended': [],
            'unknown_fields': [],
            'entries_preview': [],
            'issues': []
        }
        
        try:
            if not os.path.exists(csv_file):
                validation_result['issues'].append(f"File not found: {csv_file}")
                return validation_result
                
            validation_result['file_exists'] = True
            
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                validation_result['readable'] = True
                validation_result['fields_found'] = reader.fieldnames or []
                
                entries = []
                for row in reader:
                    entries.append(row)
                    if len(entries) >= 3:  # Preview first 3 entries
                        break
                        
                validation_result['entries_count'] = len(entries)
                validation_result['entries_preview'] = entries
                
                # Check required fields
                fields_set = set(validation_result['fields_found'])
                validation_result['missing_required'] = list(self.required_fields - fields_set)
                validation_result['missing_recommended'] = list(self.recommended_fields - fields_set)
                
                # Check for unknown fields
                known_fields = set(self.utils.PROPERTY_URIS.keys()) | {'file', 'status'}
                validation_result['unknown_fields'] = list(fields_set - known_fields)
                
        except Exception as e:
            validation_result['issues'].append(f"Error reading CSV: {str(e)}")
            
        return validation_result
        
    def validate_field_values(self, row: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate individual field values and return issues."""
        issues = []
        
        # Check title format
        if 'title' in row and row['title']:
            title = row['title']
            if '|' in title:
                # Check bilingual format
                if not title.startswith(('fr:', 'en:')):
                    issues.append({
                        'field': 'title',
                        'severity': 'warning',
                        'message': 'Bilingual titles should start with "fr:" or "en:"',
                        'suggestion': 'Use format: "fr:Titre français|en:English title"'
                    })
            else:
                issues.append({
                    'field': 'title',
                    'severity': 'info',
                    'message': 'Consider adding bilingual title',
                    'suggestion': 'Format: "fr:Titre français|en:English title"'
                })
                
        # Check COAR resource type
        if 'type' in row and row['type']:
            type_uri = row['type']
            if not type_uri.startswith('http://purl.org/coar/resource_type/'):
                issues.append({
                    'field': 'type',
                    'severity': 'error',
                    'message': 'Invalid resource type URI',
                    'suggestion': 'Use COAR resource type URI, e.g., http://purl.org/coar/resource_type/c_ddb1'
                })
                
        # Check date format
        if 'date' in row and row['date']:
            date_val = row['date']
            if not (date_val.isdigit() or '-' in date_val):
                issues.append({
                    'field': 'date',
                    'severity': 'warning',
                    'message': 'Date format might be invalid',
                    'suggestion': 'Use YYYY or YYYY-MM-DD format'
                })
                
        return issues


class MetadataPreview:
    """Generates JSON preview of metadata that will be sent to NAKALA API."""
    
    def __init__(self):
        self.utils = NakalaCommonUtils()
        
    def generate_preview(self, csv_file: str) -> Dict[str, Any]:
        """Generate complete preview of CSV conversion to NAKALA JSON."""
        preview_result = {
            'success': False,
            'entries': [],
            'summary': {
                'total_entries': 0,
                'total_metadata_fields': 0,
                'unique_properties': set(),
                'languages_used': set()
            },
            'errors': []
        }
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for i, row in enumerate(reader, 1):
                    try:
                        # Generate metadata using our fixed utils
                        metas = self.utils.prepare_nakala_metadata(row)
                        
                        entry_preview = {
                            'entry_number': i,
                            'original_data': dict(row),
                            'generated_metadata': metas,
                            'summary': {
                                'metadata_count': len(metas),
                                'properties_used': list(set(m['propertyUri'] for m in metas))
                            }
                        }
                        
                        preview_result['entries'].append(entry_preview)
                        
                        # Update summary stats
                        preview_result['summary']['total_metadata_fields'] += len(metas)
                        for meta in metas:
                            preview_result['summary']['unique_properties'].add(meta['propertyUri'])
                            if 'lang' in meta:
                                preview_result['summary']['languages_used'].add(meta['lang'])
                                
                    except Exception as e:
                        preview_result['errors'].append(f"Entry {i}: {str(e)}")
                        
                preview_result['summary']['total_entries'] = len(preview_result['entries'])
                preview_result['summary']['unique_properties'] = len(preview_result['summary']['unique_properties'])
                preview_result['summary']['languages_used'] = list(preview_result['summary']['languages_used'])
                preview_result['success'] = True
                
        except Exception as e:
            preview_result['errors'].append(f"File error: {str(e)}")
            
        return preview_result


class ResearcherAssistant:
    """Provides proactive assistance for researchers creating metadata."""
    
    def __init__(self):
        self.utils = NakalaCommonUtils()
        
    def suggest_coar_types(self, content_hint: str = "") -> List[Dict[str, str]]:
        """Suggest COAR resource types based on content hints."""
        suggestions = [
            {
                'uri': 'http://purl.org/coar/resource_type/c_ddb1',
                'label': 'Dataset',
                'description': 'Research data, CSV files, survey results',
                'keywords': ['data', 'données', 'csv', 'results', 'survey']
            },
            {
                'uri': 'http://purl.org/coar/resource_type/c_5ce6', 
                'label': 'Software',
                'description': 'Code, scripts, programs, R/Python files',
                'keywords': ['code', 'script', 'program', 'python', 'r', '.py', '.R']
            },
            {
                'uri': 'http://purl.org/coar/resource_type/c_18cf',
                'label': 'Text',
                'description': 'Documents, papers, reports, documentation',
                'keywords': ['document', 'paper', 'report', 'text', '.pdf', '.md']
            },
            {
                'uri': 'http://purl.org/coar/resource_type/c_c513',
                'label': 'Image',
                'description': 'Photos, figures, diagrams, visualizations',
                'keywords': ['image', 'photo', 'figure', '.jpg', '.png', 'visual']
            },
            {
                'uri': 'http://purl.org/coar/resource_type/c_8544',
                'label': 'Lecture',
                'description': 'Presentations, slides, conference materials',
                'keywords': ['presentation', 'slides', 'lecture', 'conference']
            }
        ]
        
        if content_hint:
            # Score suggestions based on content hint
            hint_lower = content_hint.lower()
            for suggestion in suggestions:
                suggestion['score'] = sum(1 for keyword in suggestion['keywords'] 
                                        if keyword in hint_lower)
            suggestions.sort(key=lambda x: x['score'], reverse=True)
            
        return suggestions[:3]  # Return top 3
        
    def generate_templates(self, content_type: str) -> Dict[str, str]:
        """Generate metadata templates based on content type."""
        templates = {
            'research_paper': {
                'title': 'fr:Titre de l\'article de recherche|en:Research paper title',
                'description': 'fr:Résumé détaillé de la recherche et méthodologie|en:Detailed research abstract and methodology',
                'keywords': 'fr:recherche;méthodologie;analyse|en:research;methodology;analysis',
                'type': 'http://purl.org/coar/resource_type/c_18cf'
            },
            'dataset': {
                'title': 'fr:Jeu de données de recherche|en:Research dataset',
                'description': 'fr:Description des données collectées et méthodes de collecte|en:Description of collected data and collection methods', 
                'keywords': 'fr:données;recherche;analyse|en:data;research;analysis',
                'type': 'http://purl.org/coar/resource_type/c_ddb1'
            },
            'code': {
                'title': 'fr:Scripts d\'analyse et code source|en:Analysis scripts and source code',
                'description': 'fr:Scripts pour le traitement et l\'analyse des données|en:Scripts for data processing and analysis',
                'keywords': 'fr:code;programmation;scripts;analyse|en:code;programming;scripts;analysis',
                'type': 'http://purl.org/coar/resource_type/c_5ce6'
            }
        }
        return templates.get(content_type, {})


@click.command()
@click.option('--csv', 'csv_file', required=True, help='Path to CSV metadata file')
@click.option('--interactive', '-i', is_flag=True, help='Interactive mode with assistance')
@click.option('--enhance', '-e', is_flag=True, help='Suggest intelligent metadata enhancements')
@click.option('--json-output', help='Save JSON preview to file')
@click.option('--validate-only', is_flag=True, help='Only validate, don\'t show preview')
def preview(csv_file: str, interactive: bool, enhance: bool, json_output: str, validate_only: bool):
    """
    Preview and validate NAKALA metadata CSV files with intelligent enhancements.
    
    This tool helps researchers prepare metadata by:
    - Validating CSV structure and field values
    - Intelligently enhancing metadata quality (--enhance)
    - Previewing the exact JSON that will be sent to NAKALA
    - Providing suggestions and templates
    - Offering interactive assistance
    
    NEW in v2.5.0: Use --enhance to automatically improve metadata quality!
    """
    
    console.print(Panel.fit(
        "[bold blue]🔍 NAKALA Metadata Preview Tool[/bold blue]\n"
        "Validate CSV metadata and preview NAKALA API JSON",
        border_style="blue"
    ))
    
    # Initialize components
    validator = MetadataValidator()
    previewer = MetadataPreview()
    assistant = ResearcherAssistant()
    enhancer = MetadataEnhancer() if enhance else None
    
    # Step 1: Validate CSV structure
    console.print("\n[bold yellow]Step 1: Validating CSV structure...[/bold yellow]")
    validation_result = validator.validate_csv_structure(csv_file)
    
    if not validation_result['file_exists']:
        console.print(f"[red]❌ File not found: {csv_file}[/red]")
        sys.exit(1)
        
    if not validation_result['readable']:
        console.print(f"[red]❌ Cannot read CSV file[/red]")
        for issue in validation_result['issues']:
            console.print(f"   • {issue}")
        sys.exit(1)
        
    # Display validation summary
    table = Table(title="CSV Structure Analysis")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Entries found", str(validation_result['entries_count']))
    table.add_row("Fields found", str(len(validation_result['fields_found'])))
    table.add_row("Missing required", str(len(validation_result['missing_required'])) if validation_result['missing_required'] else "✅ All present")
    table.add_row("Missing recommended", str(len(validation_result['missing_recommended'])) if validation_result['missing_recommended'] else "✅ All present")
    table.add_row("Unknown fields", str(len(validation_result['unknown_fields'])) if validation_result['unknown_fields'] else "✅ All recognized")
    
    console.print(table)
    
    # Show issues if any
    if validation_result['missing_required']:
        console.print(f"\n[red]❌ Missing required fields: {', '.join(validation_result['missing_required'])}[/red]")
        
    if validation_result['missing_recommended']:
        console.print(f"\n[yellow]⚠️  Missing recommended fields: {', '.join(validation_result['missing_recommended'])}[/yellow]")
        
    if validation_result['unknown_fields']:
        console.print(f"\n[orange3]ℹ️  Unknown fields (will be ignored): {', '.join(validation_result['unknown_fields'])}[/orange3]")
        
    if validate_only:
        console.print("\n[green]✅ Validation complete[/green]")
        return
    
    # Step 1.5: Intelligent metadata enhancement (if requested)
    enhanced_csv_file = csv_file  # Default to original file
    if enhancer:
        console.print("\n[bold yellow]Step 1.5: Analyzing content for metadata enhancements...[/bold yellow]")
        
        # Read CSV data for enhancement analysis
        csv_data = []
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                csv_data = list(reader)
        except Exception as e:
            console.print(f"[red]❌ Error reading CSV for enhancement: {e}[/red]")
            csv_data = []
        
        if csv_data:
            enhancements = enhancer.suggest_enhancements(csv_data)
            
            # Display enhancement summary
            if enhancements['suggestions']:
                console.print(f"[green]🎯 Found {enhancements['enhanced_entries']} enhancement opportunities:[/green]")
                
                enhancement_table = Table()
                enhancement_table.add_column("Entry", style="cyan")
                enhancement_table.add_column("Content Type", style="yellow")
                enhancement_table.add_column("Confidence", style="green")
                enhancement_table.add_column("Enhancement Preview", style="white")
                
                for i, suggestion in enumerate(enhancements['suggestions'][:5]):  # Show first 5
                    title_preview = suggestion['enhancements']['title'].split('|')[0].replace('fr:', '')[:40]
                    enhancement_table.add_row(
                        f"#{suggestion['entry_index']+1}",
                        suggestion['content_type'].title(),
                        f"{suggestion['confidence']}%",
                        f"{title_preview}..."
                    )
                
                console.print(enhancement_table)
                
                # Interactive enhancement application
                if interactive:
                    if Confirm.ask("\n🚀 Apply these intelligent enhancements?"):
                        # Apply all suggestions
                        selected_suggestions = list(range(len(enhancements['suggestions'])))
                        enhanced_data = enhancer.apply_enhancements(csv_data, selected_suggestions)
                        
                        # Create enhanced CSV file
                        enhanced_csv_file = csv_file.replace('.csv', '_enhanced.csv')
                        with open(enhanced_csv_file, 'w', newline='', encoding='utf-8') as f:
                            if enhanced_data:
                                fieldnames = enhanced_data[0].keys()
                                writer = csv.DictWriter(f, fieldnames=fieldnames)
                                writer.writeheader()
                                writer.writerows(enhanced_data)
                        
                        console.print(f"[green]✅ Enhanced metadata saved to: {enhanced_csv_file}[/green]")
                        console.print(f"[cyan]💡 Original file preserved as: {csv_file}[/cyan]")
                else:
                    # Non-interactive: auto-apply high-confidence suggestions
                    high_confidence = [i for i, s in enumerate(enhancements['suggestions']) if s['confidence'] >= 70]
                    if high_confidence:
                        enhanced_data = enhancer.apply_enhancements(csv_data, high_confidence)
                        enhanced_csv_file = csv_file.replace('.csv', '_enhanced.csv')
                        with open(enhanced_csv_file, 'w', newline='', encoding='utf-8') as f:
                            if enhanced_data:
                                fieldnames = enhanced_data[0].keys()
                                writer = csv.DictWriter(f, fieldnames=fieldnames)
                                writer.writeheader()
                                writer.writerows(enhanced_data)
                        console.print(f"[green]✅ Auto-applied {len(high_confidence)} high-confidence enhancements[/green]")
                        console.print(f"[green]📁 Enhanced file: {enhanced_csv_file}[/green]")
            else:
                console.print("[yellow]💡 No obvious enhancement opportunities detected[/yellow]")
                console.print("[dim]   Content appears to already have good metadata quality[/dim]")
        
    # Step 2: Generate preview
    console.print("\n[bold yellow]Step 2: Generating metadata preview...[/bold yellow]")
    preview_result = previewer.generate_preview(enhanced_csv_file)
    
    if not preview_result['success']:
        console.print("[red]❌ Failed to generate preview[/red]")
        for error in preview_result['errors']:
            console.print(f"   • {error}")
        return
        
    # Display summary
    summary = preview_result['summary']
    table = Table(title="Metadata Generation Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Entries processed", str(summary['total_entries']))
    table.add_row("Total metadata fields", str(summary['total_metadata_fields']))
    table.add_row("Unique properties", str(summary['unique_properties']))
    table.add_row("Languages used", ", ".join(summary['languages_used']) if summary['languages_used'] else "No language tags")
    table.add_row("Avg fields per entry", f"{summary['total_metadata_fields']/summary['total_entries']:.1f}" if summary['total_entries'] > 0 else "0")
    
    console.print(table)
    
    # Step 3: Show detailed preview for first entry
    if preview_result['entries']:
        console.print("\n[bold yellow]Step 3: Preview of first entry JSON...[/bold yellow]")
        first_entry = preview_result['entries'][0]
        
        # Show original CSV data
        console.print("\n[bold cyan]Original CSV data:[/bold cyan]")
        csv_table = Table()
        csv_table.add_column("Field", style="cyan")
        csv_table.add_column("Value", style="white")
        
        for field, value in first_entry['original_data'].items():
            if value:  # Only show non-empty fields
                display_value = str(value)[:60] + "..." if len(str(value)) > 60 else str(value)
                csv_table.add_row(field, display_value)
                
        console.print(csv_table)
        
        # Show generated JSON
        console.print("\n[bold cyan]NAKALA metadata JSON preview:[/bold cyan]")
        json_output_data = {
            "status": "pending",
            "metas": first_entry['generated_metadata']
        }
        
        json_str = json.dumps(json_output_data, indent=2, ensure_ascii=False)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="NAKALA API Payload Preview"))
        
        # Save JSON if requested
        if json_output:
            with open(json_output, 'w', encoding='utf-8') as f:
                json.dump({'preview_data': preview_result}, f, indent=2, ensure_ascii=False)
            console.print(f"\n[green]✅ Preview saved to: {json_output}[/green]")
            
    # Interactive mode
    if interactive:
        console.print("\n[bold yellow]Interactive Assistant Mode[/bold yellow]")
        
        while True:
            console.print("\n[cyan]What would you like to do?[/cyan]")
            console.print("1. Get COAR resource type suggestions")
            console.print("2. Generate metadata template")
            console.print("3. Validate field values in detail")
            console.print("4. Exit")
            
            choice = Prompt.ask("Enter choice", choices=["1", "2", "3", "4"], default="4")
            
            if choice == "1":
                hint = Prompt.ask("Enter content description (optional)", default="")
                suggestions = assistant.suggest_coar_types(hint)
                
                table = Table(title="COAR Resource Type Suggestions")
                table.add_column("URI", style="cyan")
                table.add_column("Label", style="white")
                table.add_column("Description", style="green")
                
                for suggestion in suggestions:
                    table.add_row(suggestion['uri'], suggestion['label'], suggestion['description'])
                    
                console.print(table)
                
            elif choice == "2":
                template_type = Prompt.ask("Template type", choices=["research_paper", "dataset", "code"], default="dataset")
                template = assistant.generate_templates(template_type)
                
                console.print(f"\n[bold cyan]Template for {template_type}:[/bold cyan]")
                for field, value in template.items():
                    console.print(f"{field}: {value}")
                    
            elif choice == "3":
                console.print("\n[bold cyan]Detailed field validation:[/bold cyan]")
                for entry in preview_result['entries'][:1]:  # Just first entry
                    issues = validator.validate_field_values(entry['original_data'])
                    if issues:
                        for issue in issues:
                            severity_color = {'error': 'red', 'warning': 'yellow', 'info': 'blue'}[issue['severity']]
                            console.print(f"[{severity_color}]{issue['severity'].upper()}[/{severity_color}] {issue['field']}: {issue['message']}")
                            console.print(f"  💡 {issue['suggestion']}")
                    else:
                        console.print("[green]✅ No issues found[/green]")
                        
            elif choice == "4":
                break
                
    console.print("\n[bold green]🎉 Preview complete![/bold green]")
    console.print("Your metadata is ready for upload with o-nakala-upload")


def main():
    """Main entry point for CLI."""
    try:
        preview()
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]❌ Unexpected error: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()