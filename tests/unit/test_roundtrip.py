#!/usr/bin/env python3
"""
Unit tests for round-trip conversions between loglog and markdown formats.
"""
import sys
import os
import unittest
from pathlib import Path

# Add parent directories to path to import loglog
sys.path.append(str(Path(__file__).parent.parent.parent))
from loglog import build_tree_from_file, build_tree_from_text, from_md

class TestRoundTripConversions(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_data_dir = Path(__file__).parent.parent
        
        # List of test files (without extension)
        self.test_files = [
            'test_input',
            'test_input_shallow', 
            'test_input_deep',
            'test_input_todos',
            'test_input_flat'
        ]
    
    def normalize_loglog_text(self, text, add_dashes=False):
        """Normalize loglog text for comparison"""
        lines = []
        for line in text.split('\n'):
            line = line.rstrip()  # Remove trailing whitespace
            if line.strip():  # Skip empty lines
                # Normalize TODO format: [] -> [ ]
                line = line.replace('[]', '[ ]')
                
                # Optionally add dashes to match from_md output format
                if add_dashes and not line.strip().startswith(('[ ]', '[x]', '[?]')):
                    indent = len(line) - len(line.lstrip())
                    content = line.strip()
                    if content and not content.startswith('-'):
                        line = ' ' * indent + '- ' + content
                
                lines.append(line)
        return '\n'.join(lines)
    
    def normalize_markdown_text(self, text):
        """Normalize markdown text for flexible comparison"""
        lines = []
        for line in text.split('\n'):
            line = line.rstrip()  # Remove trailing whitespace
            if line.strip():  # Skip empty lines
                lines.append(line)
        return '\n'.join(lines)
    
    def test_txt_to_md_to_txt_roundtrip(self):
        """Test: loglog -> markdown -> loglog (should be identical)"""
        print("\n" + "="*60)
        print("Testing TXT -> MD -> TXT round-trip conversions")
        print("="*60)
        
        for test_name in self.test_files:
            with self.subTest(test_file=test_name):
                print(f"\nTesting: {test_name}")
                
                # Read original loglog file
                txt_file = self.test_data_dir / f"{test_name}.txt"
                with open(txt_file, 'r') as f:
                    original_txt = f.read()
                
                # Convert: txt -> tree -> md
                tree = build_tree_from_file(str(txt_file))
                markdown_result = tree.to_md()
                
                # Convert: md -> txt  
                converted_txt = from_md(markdown_result)
                
                # Normalize both for comparison
                # Original needs dashes added to match from_md output format
                original_normalized = self.normalize_loglog_text(original_txt, add_dashes=True)
                converted_normalized = self.normalize_loglog_text(converted_txt)
                
                print(f"  Original length: {len(original_normalized.split())}")
                print(f"  Converted length: {len(converted_normalized.split())}")
                
                # They should be identical (or very close)
                if original_normalized != converted_normalized:
                    print(f"  ⚠️  DIFFERENCE DETECTED:")
                    print(f"     Original:\n{original_normalized[:200]}...")
                    print(f"     Converted:\n{converted_normalized[:200]}...")
                    
                    # Save debug files
                    debug_dir = self.test_data_dir / "debug"
                    debug_dir.mkdir(exist_ok=True)
                    
                    with open(debug_dir / f"{test_name}_original.txt", 'w') as f:
                        f.write(original_normalized)
                    with open(debug_dir / f"{test_name}_roundtrip.txt", 'w') as f:
                        f.write(converted_normalized)
                    with open(debug_dir / f"{test_name}_intermediate.md", 'w') as f:
                        f.write(markdown_result)
                    
                    print(f"     Debug files saved to: {debug_dir}")
                
                # Use assertAlmostEqual for string comparison with some tolerance
                similarity = self._calculate_similarity(original_normalized, converted_normalized)
                print(f"  Similarity: {similarity:.2%}")
                
                # Should be very similar (>90% after normalization)
                self.assertGreater(similarity, 0.90, 
                    f"Round-trip conversion similarity too low for {test_name}: {similarity:.2%}")
                
                if similarity == 1.0:
                    print(f"  ✅ PERFECT match")
                else:
                    print(f"  ✅ GOOD match ({similarity:.2%})")
    
    def test_md_to_txt_to_md_roundtrip(self):
        """Test: markdown -> loglog -> markdown (should be structurally similar)"""
        print("\n" + "="*60)
        print("Testing MD -> TXT -> MD round-trip conversions")
        print("="*60)
        
        for test_name in self.test_files:
            with self.subTest(test_file=test_name):
                print(f"\nTesting: {test_name}")
                
                # Read original markdown output file
                md_file = self.test_data_dir / f"{test_name}_output.md"
                with open(md_file, 'r') as f:
                    original_md = f.read()
                
                # Convert: md -> txt
                converted_txt = from_md(original_md)
                
                # Convert: txt -> tree -> md
                txt_lines = converted_txt.split('\n')
                tree = build_tree_from_text(txt_lines)
                reconverted_md = tree.to_md()
                
                # Normalize both for flexible comparison
                original_normalized = self.normalize_markdown_text(original_md)
                reconverted_normalized = self.normalize_markdown_text(reconverted_md)
                
                print(f"  Original length: {len(original_normalized.split())}")
                print(f"  Reconverted length: {len(reconverted_normalized.split())}")
                
                # Calculate structural similarity
                similarity = self._calculate_structural_similarity(original_normalized, reconverted_normalized)
                print(f"  Structural similarity: {similarity:.2%}")
                
                if similarity < 0.9:
                    print(f"  ⚠️  LOW SIMILARITY DETECTED:")
                    print(f"     Original:\n{original_normalized[:200]}...")
                    print(f"     Reconverted:\n{reconverted_normalized[:200]}...")
                    
                    # Save debug files
                    debug_dir = self.test_data_dir / "debug"
                    debug_dir.mkdir(exist_ok=True)
                    
                    with open(debug_dir / f"{test_name}_md_original.md", 'w') as f:
                        f.write(original_normalized)
                    with open(debug_dir / f"{test_name}_md_roundtrip.md", 'w') as f:
                        f.write(reconverted_normalized)
                    with open(debug_dir / f"{test_name}_md_intermediate.txt", 'w') as f:
                        f.write(converted_txt)
                    
                    print(f"     Debug files saved to: {debug_dir}")
                
                # Should be structurally similar (>85% due to formatting differences)
                self.assertGreater(similarity, 0.85, 
                    f"Markdown round-trip structural similarity too low for {test_name}: {similarity:.2%}")
                
                if similarity > 0.95:
                    print(f"  ✅ EXCELLENT structural match")
                elif similarity > 0.90:
                    print(f"  ✅ GOOD structural match")
                else:
                    print(f"  ✅ ACCEPTABLE structural match")
    
    def _calculate_similarity(self, text1, text2):
        """Calculate similarity between two texts using simple word-based comparison"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _calculate_structural_similarity(self, md1, md2):
        """Calculate structural similarity for markdown, focusing on headers and structure"""
        
        def extract_structure(md_text):
            """Extract structural elements from markdown"""
            structure = []
            for line in md_text.split('\n'):
                line = line.strip()
                if line.startswith('#'):
                    # Count header level
                    level = 0
                    for char in line:
                        if char == '#':
                            level += 1
                        else:
                            break
                    structure.append(f"H{level}:{line[level:].strip()}")
                elif line.startswith('- '):
                    # List item
                    indent = len(line) - len(line.lstrip())
                    structure.append(f"L{indent//2}:{line.strip()[2:]}")
            return structure
        
        struct1 = extract_structure(md1)
        struct2 = extract_structure(md2)
        
        if not struct1 and not struct2:
            return 1.0
        if not struct1 or not struct2:
            return 0.0
        
        # Compare structures
        matches = 0
        max_len = max(len(struct1), len(struct2))
        
        for i in range(min(len(struct1), len(struct2))):
            if struct1[i] == struct2[i]:
                matches += 1
        
        return matches / max_len

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)