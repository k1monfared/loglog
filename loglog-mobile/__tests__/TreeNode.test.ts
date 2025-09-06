import { TreeNode } from '../src/core/TreeNode';

describe('TreeNode', () => {
  describe('constructor', () => {
    it('should create a node with default values', () => {
      const node = new TreeNode('Test content');
      expect(node.content).toBe('Test content');
      expect(node.level).toBe(0);
      expect(node.type).toBe('item');
      expect(node.children).toEqual([]);
      expect(node.parent).toBeNull();
    });

    it('should create a node with custom values', () => {
      const node = new TreeNode('Todo item', 2, 'todo');
      expect(node.content).toBe('Todo item');
      expect(node.level).toBe(2);
      expect(node.type).toBe('todo');
    });
  });

  describe('addChild', () => {
    it('should add a child node', () => {
      const parent = new TreeNode('Parent');
      const child = new TreeNode('Child');
      
      parent.addChild(child);
      
      expect(parent.children).toContain(child);
      expect(child.parent).toBe(parent);
    });

    it('should add multiple children in order', () => {
      const parent = new TreeNode('Parent');
      const child1 = new TreeNode('Child 1');
      const child2 = new TreeNode('Child 2');
      
      parent.addChild(child1);
      parent.addChild(child2);
      
      expect(parent.children[0]).toBe(child1);
      expect(parent.children[1]).toBe(child2);
    });
  });

  describe('toMd', () => {
    it('should convert simple node to markdown', () => {
      const node = new TreeNode('Simple item');
      expect(node.toMd()).toBe('- Simple item');
    });

    it('should convert nested structure to markdown', () => {
      const root = new TreeNode('Root');
      const child1 = new TreeNode('Child 1', 1);
      const child2 = new TreeNode('Child 2', 1);
      const grandchild = new TreeNode('Grandchild', 2);
      
      root.addChild(child1);
      root.addChild(child2);
      child1.addChild(grandchild);
      
      const expected = `- Root
  - Child 1
    - Grandchild
  - Child 2`;
      
      expect(root.toMd()).toBe(expected);
    });

    it('should handle todo items correctly', () => {
      const todo = new TreeNode('[ ] Uncompleted task', 0, 'todo');
      expect(todo.toMd()).toBe('- [ ] Uncompleted task');
      
      const completed = new TreeNode('[x] Completed task', 0, 'todo');
      expect(completed.toMd()).toBe('- [x] Completed task');
    });
  });

  describe('toData and fromData', () => {
    it('should serialize and deserialize correctly', () => {
      const original = new TreeNode('Test content', 1, 'todo');
      const child = new TreeNode('Child content', 2);
      original.addChild(child);
      
      const data = original.toData();
      const restored = TreeNode.fromData(data);
      
      expect(restored.content).toBe(original.content);
      expect(restored.level).toBe(original.level);
      expect(restored.type).toBe(original.type);
      expect(restored.children.length).toBe(1);
      expect(restored.children[0].content).toBe('Child content');
    });

    it('should handle empty children array', () => {
      const node = new TreeNode('Single node');
      const data = node.toData();
      const restored = TreeNode.fromData(data);
      
      expect(restored.children).toEqual([]);
      expect(restored.parent).toBeNull();
    });
  });

  describe('findById', () => {
    it('should find node by id', () => {
      const root = new TreeNode('Root');
      const child = new TreeNode('Target');
      root.addChild(child);
      
      const found = root.findById(child.id);
      expect(found).toBe(child);
    });

    it('should return null for non-existent id', () => {
      const root = new TreeNode('Root');
      const found = root.findById('non-existent-id');
      expect(found).toBeNull();
    });

    it('should search in nested structure', () => {
      const root = new TreeNode('Root');
      const child = new TreeNode('Child');
      const grandchild = new TreeNode('Target');
      
      root.addChild(child);
      child.addChild(grandchild);
      
      const found = root.findById(grandchild.id);
      expect(found).toBe(grandchild);
    });
  });
});