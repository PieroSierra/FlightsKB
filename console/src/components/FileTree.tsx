import { useState } from 'react';
import type { FileTreeNode } from '../types';

interface FileTreeItemProps {
  node: FileTreeNode;
  selectedPath?: string;
  onSelect: (path: string) => void;
  level?: number;
}

function FileTreeItem({ node, selectedPath, onSelect, level = 0 }: FileTreeItemProps) {
  const [isExpanded, setIsExpanded] = useState(level === 0);
  const isSelected = node.path === selectedPath;

  const handleClick = () => {
    if (node.type === 'directory') {
      setIsExpanded(!isExpanded);
    } else {
      onSelect(node.path);
    }
  };

  return (
    <div className="file-tree-item">
      <div
        className={`file-tree-row ${isSelected ? 'file-tree-row--selected' : ''}`}
        style={{ paddingLeft: `${level * 16 + 8}px` }}
        onClick={handleClick}
      >
        {node.type === 'directory' ? (
          <span className="file-tree-icon">
            {isExpanded ? '▼' : '▶'}
          </span>
        ) : (
          <span className="file-tree-icon file-tree-icon--file">📄</span>
        )}
        <span className="file-tree-name">
          {node.type === 'directory' ? node.name : (node.metadata?.title || node.name)}
        </span>
        {node.type === 'file' && node.metadata?.status && (
          <span className={`file-tree-status file-tree-status--${node.metadata.status}`}>
            {node.metadata.status}
          </span>
        )}
      </div>
      {node.type === 'directory' && isExpanded && node.children && (
        <div className="file-tree-children">
          {node.children.map((child) => (
            <FileTreeItem
              key={child.path}
              node={child}
              selectedPath={selectedPath}
              onSelect={onSelect}
              level={level + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}

interface FileTreeProps {
  tree: FileTreeNode[];
  selectedPath?: string;
  onSelect: (path: string) => void;
  isLoading?: boolean;
  error?: string;
}

export function FileTree({ tree, selectedPath, onSelect, isLoading, error }: FileTreeProps) {
  if (isLoading) {
    return (
      <div className="file-tree-loading">
        <div className="spinner"></div>
        <span>Loading files...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="file-tree-error">
        <span>{error}</span>
      </div>
    );
  }

  if (tree.length === 0) {
    return (
      <div className="file-tree-empty">
        No files found
      </div>
    );
  }

  return (
    <div className="file-tree">
      {tree.map((node) => (
        <FileTreeItem
          key={node.path}
          node={node}
          selectedPath={selectedPath}
          onSelect={onSelect}
        />
      ))}
    </div>
  );
}
