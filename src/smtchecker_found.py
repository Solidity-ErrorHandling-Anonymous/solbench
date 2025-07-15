#!/usr/bin/env python3
"""
Script to detect 'pragma experimental SMTChecker' in Solidity smart contracts.
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import csv

class SMTCheckerDetector:
    """Detects pragma experimental SMTChecker in Solidity files."""
    
    def __init__(self):
        # Regex patterns to match SMTChecker pragma
        self.patterns = [
            r'pragma\s+experimental\s+SMTChecker\s*;',
            r'pragma\s+experimental\s+"SMTChecker"\s*;',
            r'pragma\s+experimental\s+\'SMTChecker\'\s*;',
        ]
        
        # Compile regex patterns for efficiency
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE | re.MULTILINE) 
            for pattern in self.patterns
        ]
        
        self.results = []
    
    def detect_in_content(self, content: str) -> List[Dict]:
        """
        Detect SMTChecker pragma in file content.
        
        Args:
            content: File content as string
            
        Returns:
            List of dictionaries containing match information
        """
        matches = []
        lines = content.split('\n')
        
        for pattern_idx, pattern in enumerate(self.compiled_patterns):
            for match in pattern.finditer(content):
                # Find line number
                line_num = content[:match.start()].count('\n') + 1
                line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                
                matches.append({
                    'pattern_used': self.patterns[pattern_idx],
                    'match_text': match.group(0),
                    'line_number': line_num,
                    'line_content': line_content,
                    'start_pos': match.start(),
                    'end_pos': match.end()
                })
        
        return matches
    
    def detect_in_file(self, file_path: Path) -> Dict:
        """
        Detect SMTChecker pragma in a single file.
        
        Args:
            file_path: Path to the Solidity file
            
        Returns:
            Dictionary with detection results
        """
        result = {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'has_smt_checker': False,
            'matches': [],
            'error': None
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            matches = self.detect_in_content(content)
            
            if matches:
                result['has_smt_checker'] = True
                result['matches'] = matches
                
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def scan_directory(self, directory: Path, recursive: bool = True) -> List[Dict]:
        """
        Scan directory for Solidity files and detect SMTChecker pragma.
        
        Args:
            directory: Directory path to scan
            recursive: Whether to scan subdirectories
            
        Returns:
            List of detection results
        """
        solidity_extensions = {'.sol', '.solidity'}
        results = []
        
        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"
            
        for file_path in directory.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in solidity_extensions:
                result = self.detect_in_file(file_path)
                results.append(result)
                
                # Print progress for large scans
                if len(results) % 100 == 0:
                    print(f"Processed {len(results)} files...")
        
        return results
    
    def detect_in_string(self, solidity_code: str, identifier: str = "inline_code") -> Dict:
        """
        Detect SMTChecker pragma in a Solidity code string.
        
        Args:
            solidity_code: Solidity source code as string
            identifier: Identifier for this code snippet
            
        Returns:
            Dictionary with detection results
        """
        result = {
            'identifier': identifier,
            'has_smt_checker': False,
            'matches': [],
            'error': None
        }
        
        try:
            matches = self.detect_in_content(solidity_code)
            
            if matches:
                result['has_smt_checker'] = True
                result['matches'] = matches
                
        except Exception as e:
            result['error'] = str(e)
        
        return result

def save_results_csv(results: List[Dict], output_file: Path):
    """Save results to CSV file."""
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'file_path', 'file_name', 'has_smt_checker', 
            'match_count', 'line_numbers', 'match_texts', 'error'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            row = {
                'file_path': result['file_path'],
                'file_name': result['file_name'],
                'has_smt_checker': result['has_smt_checker'],
                'match_count': len(result['matches']),
                'line_numbers': ';'.join(str(m['line_number']) for m in result['matches']),
                'match_texts': ';'.join(m['match_text'] for m in result['matches']),
                'error': result['error'] or ''
            }
            writer.writerow(row)

def save_results_json(results: List[Dict], output_file: Path):
    """Save results to JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

def print_summary(results: List[Dict]):
    """Print summary statistics."""
    total_files = len(results)
    files_with_smt = sum(1 for r in results if r['has_smt_checker'])
    files_with_errors = sum(1 for r in results if r['error'])
    total_matches = sum(len(r['matches']) for r in results)
    
    print("\n" + "="*50)
    print("DETECTION SUMMARY")
    print("="*50)
    print(f"Total files scanned: {total_files}")
    print(f"Files with SMTChecker pragma: {files_with_smt}")
    print(f"Files with errors: {files_with_errors}")
    print(f"Total pragma matches found: {total_matches}")
    print(f"Adoption rate: {files_with_smt/total_files*100:.2f}%" if total_files > 0 else "Adoption rate: 0%")
    
    if files_with_smt > 0:
        print("\nFiles with SMTChecker pragma:")
        for result in results:
            if result['has_smt_checker']:
                print(f"  - {result['file_name']} (matches: {len(result['matches'])})")
                for match in result['matches']:
                    print(f"    Line {match['line_number']}: {match['line_content']}")

def main():
    parser = argparse.ArgumentParser(
        description="Detect 'pragma experimental SMTChecker' in Solidity smart contracts"
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--file', '-f', 
        type=Path,
        help='Single Solidity file to analyze'
    )
    group.add_argument(
        '--directory', '-d',
        type=Path, 
        help='Directory containing Solidity files'
    )
    group.add_argument(
        '--code', '-c',
        type=str,
        help='Solidity code string to analyze'
    )
    
    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        help='Recursively scan subdirectories (only with --directory)'
    )
    
    parser.add_argument(
        '--output-csv',
        type=Path,
        help='Save results to CSV file'
    )
    
    parser.add_argument(
        '--output-json', 
        type=Path,
        help='Save results to JSON file'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress detailed output'
    )
    
    args = parser.parse_args()
    
    detector = SMTCheckerDetector()
    results = []
    
    try:
        if args.file:
            if not args.file.exists():
                print(f"Error: File {args.file} not found")
                return 1
            
            result = detector.detect_in_file(args.file)
            results = [result]
            
        elif args.directory:
            if not args.directory.exists():
                print(f"Error: Directory {args.directory} not found")
                return 1
            
            print(f"Scanning directory: {args.directory}")
            if args.recursive:
                print("Recursive mode enabled")
            
            results = detector.scan_directory(args.directory, args.recursive)
            
        elif args.code:
            result = detector.detect_in_string(args.code)
            results = [result]
        
        # Save results
        if args.output_csv:
            save_results_csv(results, args.output_csv)
            print(f"Results saved to CSV: {args.output_csv}")
            
        if args.output_json:
            save_results_json(results, args.output_json)
            print(f"Results saved to JSON: {args.output_json}")
        
        # Print summary
        if not args.quiet:
            print_summary(results)
            
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
