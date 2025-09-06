import { parseLine, buildTreeFromString, treeToText, getNode } from '../src/core/parser';
import { TreeNode } from '../src/core/TreeNode';

describe('parser', () => {
  describe('parseLine', () => {
    it('should parse line with no indentation', () => {
      const result = parseLine('Simple item');
      expect(result.level).toBe(0);
      expect(result.content).toBe('Simple item');
      expect(result.type).toBe('item');
    });

    it('should parse line with indentation', () => {
      const result = parseLine('    Indented item');
      expect(result.level).toBe(1);
      expect(result.content).toBe('Indented item');
      expect(result.type).toBe('item');
    });

    it('should parse todo items', () => {
      const uncompleted = parseLine('[ ] Todo item');
      expect(uncompleted.type).toBe('todo');
      expect(uncompleted.content).toBe('[ ] Todo item');
      
      const completed = parseLine('[x] Completed item');
      expect(completed.type).toBe('todo');
      expect(completed.content).toBe('[x] Completed item');
    });

    it('should handle empty lines', () => {
      const result = parseLine('');
      expect(result.level).toBe(0);
      expect(result.content).toBe('');
      expect(result.type).toBe('item');
    });

    it('should handle lines with only spaces', () => {
      const result = parseLine('        ');
      expect(result.level).toBe(2);
      expect(result.content).toBe('');
      expect(result.type).toBe('item');
    });
  });

  describe('buildTreeFromString', () => {
    it('should build tree from simple text', () => {
      const text = `Root item
    Child item
        Grandchild item
    Another child`;
      
      const tree = buildTreeFromString(text);
      
      expect(tree.content).toBe('Root item');
      expect(tree.children.length).toBe(2);
      expect(tree.children[0].content).toBe('Child item');
      expect(tree.children[0].children.length).toBe(1);
      expect(tree.children[0].children[0].content).toBe('Grandchild item');
      expect(tree.children[1].content).toBe('Another child');
    });

    it('should handle empty string', () => {
      const tree = buildTreeFromString('');
      expect(tree.content).toBe('');
      expect(tree.children).toEqual([]);
    });

    it('should handle mixed todo and regular items', () => {
      const text = `Project
    [ ] Task 1
    [x] Task 2
    Regular note`;
      
      const tree = buildTreeFromString(text);
      
      expect(tree.children[0].type).toBe('todo');
      expect(tree.children[1].type).toBe('todo');
      expect(tree.children[2].type).toBe('item');
    });

    it('should handle inconsistent indentation', () => {
      const text = `Root
  Two spaces
      Six spaces
    Four spaces`;
      
      const tree = buildTreeFromString(text);
      
      expect(tree.children[0].level).toBe(1);
      expect(tree.children[0].children[0].level).toBe(2);
      expect(tree.children[1].level).toBe(1);
    });
  });

  describe('treeToText', () => {
    it('should convert tree back to text', () => {
      const root = new TreeNode('Root');
      const child = new TreeNode('Child', 1);
      const grandchild = new TreeNode('Grandchild', 2);
      
      root.addChild(child);
      child.addChild(grandchild);
      
      const text = treeToText(root);
      const expected = `Root
    Child
        Grandchild`;
      
      expect(text).toBe(expected);
    });

    it('should handle single node', () => {
      const node = new TreeNode('Single item');
      const text = treeToText(node);
      expect(text).toBe('Single item');
    });

    it('should preserve todo formatting', () => {
      const root = new TreeNode('Project');
      const todo = new TreeNode('[ ] Task', 1, 'todo');
      root.addChild(todo);
      
      const text = treeToText(root);
      expect(text).toBe(`Project
    [ ] Task`);
    });
  });

  describe('getNode', () => {
    let tree: TreeNode;
    
    beforeEach(() => {
      const text = `Root
    Child 1
        Grandchild 1
        Grandchild 2
    Child 2`;
      tree = buildTreeFromString(text);
    });

    it('should get root node with empty address', () => {
      const node = getNode(tree, []);
      expect(node).toBe(tree);
    });

    it('should get child node with address', () => {
      const node = getNode(tree, [0]);
      expect(node?.content).toBe('Child 1');
    });

    it('should get grandchild node with nested address', () => {
      const node = getNode(tree, [0, 1]);
      expect(node?.content).toBe('Grandchild 2');
    });

    it('should return null for invalid address', () => {
      const node = getNode(tree, [5]);
      expect(node).toBeNull();
    });

    it('should return null for deeply invalid address', () => {
      const node = getNode(tree, [0, 5, 3]);
      expect(node).toBeNull();
    });
  });

  describe('round-trip conversion', () => {
    it('should maintain structure through text->tree->text conversion', () => {
      const originalText = `Project Planning
    Phase 1: Research
        [ ] Market analysis
        [x] Competitor research
        Technical requirements
    Phase 2: Development
        Frontend work
        Backend implementation
    [ ] Final review`;
      
      const tree = buildTreeFromString(originalText);
      const convertedText = treeToText(tree);
      
      expect(convertedText).toBe(originalText);
    });

    it('should handle edge cases in round-trip', () => {
      const originalText = `Single line`;
      
      const tree = buildTreeFromString(originalText);
      const convertedText = treeToText(tree);
      
      expect(convertedText).toBe(originalText);
    });
  });
});