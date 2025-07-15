#!/usr/bin/env python3
"""
Script to detect and analyze error messages in Solidity error handling statements.
Supports require, revert, assert, try-catch, and custom errors.
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Union
import csv
from dataclasses import dataclass
from enum import Enum

class ErrorHandlingType(Enum):
    """Types of error handling constructs."""
    REQUIRE = "require"
    REVERT = "revert"
    ASSERT = "assert"
    TRY_CATCH = "try_catch"
    CUSTOM_ERROR = "custom_error"

@dataclass
class ErrorMessage:
    """Represents an error message found in code."""
    eh_type: ErrorHandlingType
    message: str
    message_type: str  # 'string', 'empty', 'none', 'custom_error'
    line_number: int
    line_content: str
    start_pos: int
    end_pos: int
    function_name: Optional[str] = None
    contract_name: Optional[str] = None

class SolidityErrorMessageDetector:
    """Detects error messages in Solidity error handling statements."""
    
    def __init__(self):
        self.results = []
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for different error handling constructs."""
        
        # Require patterns
        self.require_patterns = [
            # require(condition, "message")
            re.compile(r'require\s*\(\s*([^,]+),\s*"([^"]*)"\s*\)', re.IGNORECASE | re.MULTILINE),
            # require(condition, 'message')
            re.compile(r"require\s*\(\s*([^,]+),\s*'([^']*)'\s*\)", re.IGNORECASE | re.MULTILINE),
            # require(condition, variable)
            re.compile(r'require\s*\(\s*([^,]+),\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\)', re.IGNORECASE | re.MULTILINE),
            # require(condition) - no message
            re.compile(r'require\s*\(\s*([^,)]+)\s*\)', re.IGNORECASE | re.MULTILINE),
        ]
        
        # Revert patterns
        self.revert_patterns = [
            # revert("message")
            re.compile(r'revert\s*\(\s*"([^"]*)"\s*\)', re.IGNORECASE | re.MULTILINE),
            # revert('message')
            re.compile(r"revert\s*\(\s*'([^']*)'\s*\)", re.IGNORECASE | re.MULTILINE),
            # revert CustomError(args)
            re.compile(r'revert\s+([A-Z][a-zA-Z0-9_]*)\s*\([^)]*\)', re.IGNORECASE | re.MULTILINE),
            # revert() - no message
            re.compile(r'revert\s*\(\s*\)', re.IGNORECASE | re.MULTILINE),
            # revert; - no parentheses
            re.compile(r'revert\s*;', re.IGNORECASE | re.MULTILINE),
        ]
        
        # Assert patterns
        self.assert_patterns = [
            # assert(condition, "message") - rare but possible in some versions
            re.compile(r'assert\s*\(\s*([^,]+),\s*"([^"]*)"\s*\)', re.IGNORECASE | re.MULTILINE),
            # assert(condition) - standard
            re.compile(r'assert\s*\(\s*([^)]+)\s*\)', re.IGNORECASE | re.MULTILINE),
        ]
        
        # Custom error definitions
        self.custom_error_patterns = [
            # error ErrorName(type param, ...)
            re.compile(r'error\s+([A-Z][a-zA-Z0-9_]*)\s*\([^)]*\)\s*;', re.IGNORECASE | re.MULTILINE),
        ]
        
        # Try-catch patterns
        self.try_catch_patterns = [
            # Basic try-catch structure
            re.compile(r'try\s+([^{]+)\s*{[^}]*}\s*catch\s*(?:\([^)]*\))?\s*{([^}]*)}', 
                      re.IGNORECASE | re.MULTILINE | re.DOTALL),
        ]
    
    def _extract_context(self, content: str, start_pos: int, end_pos: int) -> Dict[str, Optional[str]]:
        """Extract function and contract context for the match."""
        # Find the function containing this match
        before_match = content[:start_pos]
        
        # Look for function definition
        function_match = re.search(r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)', before_match[::-1])
        function_name = function_match.group(1) if function_match else None
        
        # Look for contract definition
        contract_match = re.search(r'contract\s+([a-zA-Z_][a-zA-Z0-9_]*)', before_match[::-1])
        contract_name = contract_match.group(1) if contract_match else None
        
        return {
            'function_name': function_name,
            'contract_name': contract_name
        }
    
    def _analyze_require_statements(self, content: str) -> List[ErrorMessage]:
        """Analyze require statements for error messages."""
        messages = []
        lines = content.split('\n')
        
        for pattern_idx, pattern in enumerate(self.require_patterns):
            for match in pattern.finditer(content):
                line_num = content[:match.start()].count('\n') + 1
                line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                
                context = self._extract_context(content, match.start(), match.end())
                
                if pattern_idx in [0, 1]:  # String message patterns
                    message_text = match.group(2)
                    message_type = 'empty' if message_text == '' else 'string'
                elif pattern_idx == 2:  # Variable pattern
                    message_text = match.group(2)
                    message_type = 'variable'
                else:  # No message pattern
                    message_text = ''
                    message_type = 'none'
                
                messages.append(ErrorMessage(
                    eh_type=ErrorHandlingType.REQUIRE,
                    message=message_text,
                    message_type=message_type,
                    line_number=line_num,
                    line_content=line_content,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    function_name=context['function_name'],
                    contract_name=context['contract_name']
                ))
        
        return messages
    
    def _analyze_revert_statements(self, content: str) -> List[ErrorMessage]:
        """Analyze revert statements for error messages."""
        messages = []
        lines = content.split('\n')
        
        for pattern_idx, pattern in enumerate(self.revert_patterns):
            for match in pattern.finditer(content):
                line_num = content[:match.start()].count('\n') + 1
                line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                
                context = self._extract_context(content, match.start(), match.end())
                
                if pattern_idx in [0, 1]:  # String message patterns
                    message_text = match.group(1)
                    message_type = 'empty' if message_text == '' else 'string'
                elif pattern_idx == 2:  # Custom error pattern
                    message_text = match.group(1)
                    message_type = 'custom_error'
                else:  # No message patterns
                    message_text = ''
                    message_type = 'none'
                
                messages.append(ErrorMessage(
                    eh_type=ErrorHandlingType.REVERT,
                    message=message_text,
                    message_type=message_type,
                    line_number=line_num,
                    line_content=line_content,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    function_name=context['function_name'],
                    contract_name=context['contract_name']
                ))
        
        return messages
    
    def _analyze_assert_statements(self, content: str) -> List[ErrorMessage]:
        """Analyze assert statements for error messages."""
        messages = []
        lines = content.split('\n')
        
        for pattern_idx, pattern in enumerate(self.assert_patterns):
            for match in pattern.finditer(content):
                line_num = content[:match.start()].count('\n') + 1
                line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                
                context = self._extract_context(content, match.start(), match.end())
                
                if pattern_idx == 0:  # Assert with message (rare)
                    message_text = match.group(2)
                    message_type = 'empty' if message_text == '' else 'string'
                else:  # Standard assert (no message)
                    message_text = ''
                    message_type = 'none'
                
                messages.append(ErrorMessage(
                    eh_type=ErrorHandlingType.ASSERT,
                    message=message_text,
                    message_type=message_type,
                    line_number=line_num,
                    line_content=line_content,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    function_name=context['function_name'],
                    contract_name=context['contract_name']
                ))
        
        return messages
    
    def _analyze_custom_errors(self, content: str) -> List[ErrorMessage]:
        """Analyze custom error definitions."""
        messages = []
        lines = content.split('\n')
        
        for pattern in self.custom_error_patterns:
            for match in pattern.finditer(content):
                line_num = content[:match.start()].count('\n') + 1
                line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                
                context = self._extract_context(content, match.start(), match.end())
                
                error_name = match.group(1)
                
                messages.append(ErrorMessage(
                    eh_type=ErrorHandlingType.CUSTOM_ERROR,
                    message=error_name,
                    message_type='custom_error_definition',
                    line_number=line_num,
                    line_content=line_content,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    function_name=context['function_name'],
                    contract_name=context['contract_name']
                ))
        
        return messages
    
    def _analyze_try_catch_blocks(self, content: str) -> List[ErrorMessage]:
        """Analyze try-catch blocks for error handling."""
        messages = []
        lines = content.split('\n')
        
        for pattern in self.try_catch_patterns:
            for match in pattern.finditer(content):
                line_num = content[:match.start()].count('\n') + 1
                line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                
                context = self._extract_context(content, match.start(), match.end())
                
                try_part = match.group(1).strip()
                catch_part = match.group(2).strip()
                
                # Check if catch block contains revert with custom error
                has_custom_error = bool(re.search(r'revert\s+[A-Z][a-zA-Z0-9_]*', catch_part))
                has_revert_message = bool(re.search(r'revert\s*\(\s*["\']', catch_part))
                
                if has_custom_error:
                    message_type = 'custom_error'
                    message_text = 'custom_error_in_catch'
                elif has_revert_message:
                    message_type = 'string'
                    message_text = 'string_message_in_catch'
                else:
                    message_type = 'none'
                    message_text = ''
                
                messages.append(ErrorMessage(
                    eh_type=ErrorHandlingType.TRY_CATCH,
                    message=message_text,
                    message_type=message_type,
                    line_number=line_num,
                    line_content=line_content,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    function_name=context['function_name'],
                    contract_name=context['contract_name']
                ))
        
        return messages
    
    def analyze_content(self, content: str) -> List[ErrorMessage]:
        """Analyze Solidity content for all error handling messages."""
        all_messages = []
        
        # Analyze different types of error handling
        all_messages.extend(self._analyze_require_statements(content))
        all_messages.extend(self._analyze_revert_statements(content))
        all_messages.extend(self._analyze_assert_statements(content))
        all_messages.extend(self._analyze_custom_errors(content))
        all_messages.extend(self._analyze_try_catch_blocks(content))
        
        # Sort by line number
        all_messages.sort(key=lambda x: x.line_number)
        
        return all_messages
    
    def analyze_file(self, file_path: Path) -> Dict:
        """Analyze a single Solidity file."""
        result = {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'total_messages': 0,
            'messages_by_type': {},
            'messages': [],
            'error': None
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            messages = self.analyze_content(content)
            
            # Convert ErrorMessage objects to dictionaries
            message_dicts = []
            for msg in messages:
                message_dicts.append({
                    'eh_type': msg.eh_type.value,
                    'message': msg.message,
                    'message_type': msg.message_type,
                    'line_number': msg.line_number,
                    'line_content': msg.line_content,
                    'function_name': msg.function_name,
                    'contract_name': msg.contract_name
                })
            
            # Count messages by type
            type_counts = {}
            for msg in messages:
                eh_type = msg.eh_type.value
                msg_type = msg.message_type
                key = f"{eh_type}_{msg_type}"
                type_counts[key] = type_counts.get(key, 0) + 1
            
            result.update({
                'total_messages': len(messages),
                'messages_by_type': type_counts,
                'messages': message_dicts
            })
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def scan_directory(self, directory: Path, recursive: bool = True) -> List[Dict]:
        """Scan directory for Solidity files and analyze error messages."""
        solidity_extensions = {'.sol', '.solidity'}
        results = []
        
        pattern = "**/*" if recursive else "*"
        
        for file_path in directory.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in solidity_extensions:
                result = self.analyze_file(file_path)
                results.append(result)
                
                if len(results) % 50 == 0:
                    print(f"Processed {len(results)} files...")
        
        return results

def save_results_csv(results: List[Dict], output_file: Path):
    """Save results to CSV file."""
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'file_path', 'file_name', 'total_messages', 
            'require_string', 'require_empty', 'require_none',
            'revert_string', 'revert_empty', 'revert_none', 'revert_custom_error',
            'assert_string', 'assert_none',
            'custom_errors_defined', 'try_catch_blocks',
            'error'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            row = {
                'file_path': result['file_path'],
                'file_name': result['file_name'],
                'total_messages': result['total_messages'],
                'error': result['error'] or ''
            }
            
            # Add type-specific counts
            msg_types = result['messages_by_type']
            row.update({
                'require_string': msg_types.get('require_string', 0),
                'require_empty': msg_types.get('require_empty', 0),
                'require_none': msg_types.get('require_none', 0),
                'revert_string': msg_types.get('revert_string', 0),
                'revert_empty': msg_types.get('revert_empty', 0),
                'revert_none': msg_types.get('revert_none', 0),
                'revert_custom_error': msg_types.get('revert_custom_error', 0),
                'assert_string': msg_types.get('assert_string', 0),
                'assert_none': msg_types.get('assert_none', 0),
                'custom_errors_defined': msg_types.get('custom_error_custom_error_definition', 0),
                'try_catch_blocks': msg_types.get('try_catch_custom_error', 0) + 
                                  msg_types.get('try_catch_string', 0) + 
                                  msg_types.get('try_catch_none', 0),
            })
            
            writer.writerow(row)

def save_detailed_csv(results: List[Dict], output_file: Path):
    """Save detailed message-level results to CSV."""
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'file_path', 'file_name', 'eh_type', 'message_type', 
            'message', 'line_number', 'line_content', 
            'function_name', 'contract_name'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            for message in result['messages']:
                row = {
                    'file_path': result['file_path'],
                    'file_name': result['file_name'],
                    **message
                }
                writer.writerow(row)

def print_summary(results: List[Dict]):
    """Print comprehensive summary statistics."""
    total_files = len(results)
    files_with_messages = sum(1 for r in results if r['total_messages'] > 0)
    total_messages = sum(r['total_messages'] for r in results)
    
    # Aggregate type counts
    aggregate_types = {}
    for result in results:
        for msg_type, count in result['messages_by_type'].items():
            aggregate_types[msg_type] = aggregate_types.get(msg_type, 0) + count
    
    print("\n" + "="*60)
    print("ERROR MESSAGE ANALYSIS SUMMARY")
    print("="*60)
    print(f"Total files analyzed: {total_files}")
    print(f"Files with error messages: {files_with_messages}")
    print(f"Total error handling statements: {total_messages}")
    print(f"Coverage: {files_with_messages/total_files*100:.2f}%" if total_files > 0 else "Coverage: 0%")
    
    print("\nError Handling Types Found:")
    for msg_type, count in sorted(aggregate_types.items()):
        print(f"  {msg_type}: {count}")
    
    # Calculate percentages for main categories
    require_total = sum(count for key, count in aggregate_types.items() if key.startswith('require_'))
    revert_total = sum(count for key, count in aggregate_types.items() if key.startswith('revert_'))
    assert_total = sum(count for key, count in aggregate_types.items() if key.startswith('assert_'))
    
    print(f"\nMain Categories:")
    print(f"  require statements: {require_total} ({require_total/total_messages*100:.1f}%)" if total_messages > 0 else "  require statements: 0")
    print(f"  revert statements: {revert_total} ({revert_total/total_messages*100:.1f}%)" if total_messages > 0 else "  revert statements: 0")
    print(f"  assert statements: {assert_total} ({assert_total/total_messages*100:.1f}%)" if total_messages > 0 else "  assert statements: 0")

def main():
    parser = argparse.ArgumentParser(
        description="Detect and analyze error messages in Solidity error handling statements"
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--file', '-f', type=Path, help='Single Solidity file to analyze')
    group.add_argument('--directory', '-d', type=Path, help='Directory containing Solidity files')
    group.add_argument('--code', '-c', type=str, help='Solidity code string to analyze')
    
    parser.add_argument('--recursive', '-r', action='store_true', 
                       help='Recursively scan subdirectories')
    parser.add_argument('--output-csv', type=Path, help='Save summary results to CSV')
    parser.add_argument('--output-detailed-csv', type=Path, help='Save detailed results to CSV')
    parser.add_argument('--output-json', type=Path, help='Save results to JSON')
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress detailed output')
    
    args = parser.parse_args()
    
    detector = SolidityErrorMessageDetector()
    results = []
    
    try:
        if args.file:
            if not args.file.exists():
                print(f"Error: File {args.file} not found")
                return 1
            result = detector.analyze_file(args.file)
            results = [result]
            
        elif args.directory:
            if not args.directory.exists():
                print(f"Error: Directory {args.directory} not found")
                return 1
            print(f"Scanning directory: {args.directory}")
            results = detector.scan_directory(args.directory, args.recursive)
            
        elif args.code:
            messages = detector.analyze_content(args.code)
            result = {
                'file_path': 'inline_code',
                'file_name': 'inline_code',
                'total_messages': len(messages),
                'messages_by_type': {},
                'messages': [msg.__dict__ for msg in messages],
                'error': None
            }
            results = [result]
        
        # Save results
        if args.output_csv:
            save_results_csv(results, args.output_csv)
            print(f"Summary results saved to: {args.output_csv}")
            
        if args.output_detailed_csv:
            save_detailed_csv(results, args.output_detailed_csv)
            print(f"Detailed results saved to: {args.output_detailed_csv}")
            
        if args.output_json:
            with open(args.output_json, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"JSON results saved to: {args.output_json}")
        
        if not args.quiet:
            print_summary(results)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
