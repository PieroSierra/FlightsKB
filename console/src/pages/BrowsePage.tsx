import { useState, useEffect, useCallback } from 'react';
import { FileTree } from '../components/FileTree';
import { MarkdownViewer } from '../components/MarkdownViewer';
import { api } from '../services/api';
import type { FileTreeNode, FileContentResponse } from '../types';

export function BrowsePage() {
  const [tree, setTree] = useState<FileTreeNode[]>([]);
  const [isLoadingTree, setIsLoadingTree] = useState(true);
  const [treeError, setTreeError] = useState<string>();

  const [selectedPath, setSelectedPath] = useState<string>();
  const [content, setContent] = useState<FileContentResponse>();
  const [isLoadingContent, setIsLoadingContent] = useState(false);
  const [contentError, setContentError] = useState<string>();

  useEffect(() => {
    const loadTree = async () => {
      try {
        setIsLoadingTree(true);
        setTreeError(undefined);
        const response = await api.getFileTree();
        setTree(response.tree);
      } catch (err) {
        const error = err as { message?: string };
        setTreeError(error.message || 'Failed to load file tree');
      } finally {
        setIsLoadingTree(false);
      }
    };

    loadTree();
  }, []);

  const handleSelect = useCallback(async (path: string) => {
    setSelectedPath(path);
    setContentError(undefined);

    try {
      setIsLoadingContent(true);
      const response = await api.getFileContent(path);
      setContent(response);
    } catch (err) {
      const error = err as { message?: string };
      setContentError(error.message || 'Failed to load file content');
      setContent(undefined);
    } finally {
      setIsLoadingContent(false);
    }
  }, []);

  return (
    <div className="browse-page">
      <header className="page-header">
        <h2 className="page-title">Browse Knowledge Base</h2>
        <p className="page-description">
          Explore the knowledge base files and view their contents.
        </p>
      </header>

      <div className="browse-layout">
        <div className="browse-sidebar">
          <FileTree
            tree={tree}
            selectedPath={selectedPath}
            onSelect={handleSelect}
            isLoading={isLoadingTree}
            error={treeError}
          />
        </div>
        <div className="browse-content">
          <MarkdownViewer
            content={content}
            isLoading={isLoadingContent}
            error={contentError}
          />
        </div>
      </div>
    </div>
  );
}
