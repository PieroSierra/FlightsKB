interface RebuildButtonProps {
  onClick: () => void;
  isLoading: boolean;
}

export function RebuildButton({ onClick, isLoading }: RebuildButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={isLoading}
      className="bpk-button bpk-button--destructive"
      style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
    >
      {isLoading && <span className="spinner" />}
      {isLoading ? 'Rebuilding Index...' : 'Rebuild Index'}
    </button>
  );
}
