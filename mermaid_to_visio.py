#!/usr/bin/env python3
"""
Mermaid to Visio Converter
Extracts Mermaid diagrams from markdown files and converts them to Visio-compatible formats
"""

import re
import subprocess
import sys
import argparse
from pathlib import Path
from typing import List, Tuple
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MermaidConverter:
    """Extract and convert Mermaid diagrams to various formats"""
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("diagrams")
        self.output_dir.mkdir(exist_ok=True)
        
    def extract_mermaid_blocks(self, markdown_file: Path) -> List[Tuple[str, str]]:
        """Extract all Mermaid code blocks from a markdown file
        
        Returns:
            List of tuples: (diagram_type, mermaid_code)
        """
        logger.info(f"Reading {markdown_file}")
        content = markdown_file.read_text(encoding='utf-8')
        
        # Pattern to match ```mermaid ... ```
        pattern = r'```mermaid\s+(.*?)\s+```'
        matches = re.findall(pattern, content, re.DOTALL)
        
        diagrams = []
        for code in matches:
            # Detect diagram type from first line
            first_line = code.strip().split('\n')[0]
            diagram_type = first_line.strip()
            diagrams.append((diagram_type, code))
        
        logger.info(f"Found {len(diagrams)} Mermaid diagrams")
        return diagrams
    
    def save_mermaid_file(self, code: str, output_path: Path) -> Path:
        """Save Mermaid code to .mmd file"""
        output_path.write_text(code, encoding='utf-8')
        logger.info(f"Saved Mermaid file: {output_path}")
        return output_path
    
    def check_mermaid_cli(self) -> bool:
        """Check if Mermaid CLI is installed"""
        try:
            result = subprocess.run(
                ['mmdc', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def convert_to_svg(self, mermaid_file: Path) -> Path:
        """Convert Mermaid file to SVG using Mermaid CLI
        
        Requires: npm install -g @mermaid-js/mermaid-cli
        """
        svg_file = mermaid_file.with_suffix('.svg')
        
        try:
            logger.info(f"Converting {mermaid_file.name} to SVG...")
            result = subprocess.run(
                ['mmdc', '-i', str(mermaid_file), '-o', str(svg_file)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Created: {svg_file}")
                return svg_file
            else:
                logger.error(f"Conversion failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("Conversion timed out")
            return None
        except FileNotFoundError:
            logger.error("Mermaid CLI not found. Install with: npm install -g @mermaid-js/mermaid-cli")
            return None
    
    def convert_to_png(self, mermaid_file: Path, scale: int = 2) -> Path:
        """Convert Mermaid file to PNG"""
        png_file = mermaid_file.with_suffix('.png')
        
        try:
            logger.info(f"Converting {mermaid_file.name} to PNG...")
            result = subprocess.run(
                ['mmdc', '-i', str(mermaid_file), '-o', str(png_file), '-s', str(scale)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Created: {png_file}")
                return png_file
            else:
                logger.error(f"Conversion failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("Conversion timed out")
            return None
        except FileNotFoundError:
            logger.error("Mermaid CLI not found")
            return None
    
    def convert_to_pdf(self, mermaid_file: Path) -> Path:
        """Convert Mermaid file to PDF"""
        pdf_file = mermaid_file.with_suffix('.pdf')
        
        try:
            logger.info(f"Converting {mermaid_file.name} to PDF...")
            result = subprocess.run(
                ['mmdc', '-i', str(mermaid_file), '-o', str(pdf_file)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Created: {pdf_file}")
                return pdf_file
            else:
                logger.error(f"Conversion failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("Conversion timed out")
            return None
        except FileNotFoundError:
            logger.error("Mermaid CLI not found")
            return None
    
    def process_markdown_file(
        self, 
        markdown_file: Path, 
        formats: List[str] = ['svg'],
        prefix: str = None
    ) -> List[Path]:
        """Process a markdown file and convert all Mermaid diagrams
        
        Args:
            markdown_file: Path to markdown file
            formats: List of output formats ('svg', 'png', 'pdf')
            prefix: Optional prefix for output files
            
        Returns:
            List of created file paths
        """
        diagrams = self.extract_mermaid_blocks(markdown_file)
        
        if not diagrams:
            logger.warning(f"No Mermaid diagrams found in {markdown_file}")
            return []
        
        # Use markdown filename as prefix if not provided
        if prefix is None:
            prefix = markdown_file.stem
        
        created_files = []
        
        for i, (diagram_type, code) in enumerate(diagrams, 1):
            # Create descriptive filename
            base_name = f"{prefix}_diagram_{i}_{diagram_type.replace(' ', '_')}"
            mermaid_file = self.output_dir / f"{base_name}.mmd"
            
            # Save Mermaid source
            self.save_mermaid_file(code, mermaid_file)
            created_files.append(mermaid_file)
            
            # Convert to requested formats
            if 'svg' in formats:
                svg_file = self.convert_to_svg(mermaid_file)
                if svg_file:
                    created_files.append(svg_file)
            
            if 'png' in formats:
                png_file = self.convert_to_png(mermaid_file)
                if png_file:
                    created_files.append(png_file)
            
            if 'pdf' in formats:
                pdf_file = self.convert_to_pdf(mermaid_file)
                if pdf_file:
                    created_files.append(pdf_file)
        
        return created_files
    
    def process_directory(
        self, 
        directory: Path, 
        formats: List[str] = ['svg'],
        recursive: bool = False
    ) -> List[Path]:
        """Process all markdown files in a directory
        
        Args:
            directory: Directory to search
            formats: Output formats
            recursive: Search subdirectories
            
        Returns:
            List of all created files
        """
        pattern = '**/*.md' if recursive else '*.md'
        md_files = list(directory.glob(pattern))
        
        logger.info(f"Found {len(md_files)} markdown files")
        
        all_created_files = []
        for md_file in md_files:
            created = self.process_markdown_file(md_file, formats)
            all_created_files.extend(created)
        
        return all_created_files


def main():
    parser = argparse.ArgumentParser(
        description='Convert Mermaid diagrams from markdown to Visio-compatible formats',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert single file to SVG (default)
  python mermaid_to_visio.py docs/architecture.md
  
  # Convert to multiple formats
  python mermaid_to_visio.py docs/architecture.md --formats svg png pdf
  
  # Process all markdown files in a directory
  python mermaid_to_visio.py docs/ --recursive
  
  # Custom output directory
  python mermaid_to_visio.py README.md --output exports/
  
  # Check if Mermaid CLI is installed
  python mermaid_to_visio.py --check

Prerequisites:
  Install Mermaid CLI: npm install -g @mermaid-js/mermaid-cli
  
Visio Import:
  1. Open Visio
  2. Insert → Pictures → From File
  3. Select the .svg file
  4. SVG will be imported as editable vector graphics
        """
    )
    
    parser.add_argument(
        'input',
        nargs='?',
        type=Path,
        help='Markdown file or directory to process'
    )
    
    parser.add_argument(
        '--formats',
        nargs='+',
        choices=['svg', 'png', 'pdf'],
        default=['svg'],
        help='Output formats (default: svg)'
    )
    
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('diagrams'),
        help='Output directory (default: diagrams/)'
    )
    
    parser.add_argument(
        '--recursive',
        action='store_true',
        help='Process subdirectories recursively'
    )
    
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check if Mermaid CLI is installed'
    )
    
    args = parser.parse_args()
    
    converter = MermaidConverter(output_dir=args.output)
    
    # Check installation
    if args.check:
        if converter.check_mermaid_cli():
            logger.info("✅ Mermaid CLI is installed")
            result = subprocess.run(['mmdc', '--version'], capture_output=True, text=True)
            logger.info(f"Version: {result.stdout.strip()}")
            sys.exit(0)
        else:
            logger.error("❌ Mermaid CLI is not installed")
            logger.error("Install with: npm install -g @mermaid-js/mermaid-cli")
            sys.exit(1)
    
    # Require input if not checking
    if not args.input:
        parser.print_help()
        sys.exit(1)
    
    # Check if Mermaid CLI is available
    if not converter.check_mermaid_cli():
        logger.error("❌ Mermaid CLI is not installed")
        logger.error("Install with: npm install -g @mermaid-js/mermaid-cli")
        logger.error("Or run: python mermaid_to_visio.py --check")
        sys.exit(1)
    
    # Process input
    if args.input.is_file():
        created_files = converter.process_markdown_file(args.input, args.formats)
    elif args.input.is_dir():
        created_files = converter.process_directory(args.input, args.formats, args.recursive)
    else:
        logger.error(f"Input not found: {args.input}")
        sys.exit(1)
    
    # Summary
    logger.info("")
    logger.info("=" * 80)
    logger.info(f"CONVERSION COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Created {len(created_files)} files in {args.output}/")
    logger.info("")
    logger.info("To import into Visio:")
    logger.info("  1. Open Visio")
    logger.info("  2. Insert → Pictures → From File")
    logger.info(f"  3. Select files from {args.output.absolute()}/")
    logger.info("  4. SVG files import as editable vector graphics")
    logger.info("")


if __name__ == "__main__":
    main()
