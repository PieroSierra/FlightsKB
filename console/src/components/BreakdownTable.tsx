interface BreakdownTableProps {
  title: string;
  data: Record<string, number>;
}

export function BreakdownTable({ title, data }: BreakdownTableProps) {
  const entries = Object.entries(data);

  if (entries.length === 0) {
    return null;
  }

  const total = entries.reduce((sum, [, count]) => sum + count, 0);

  return (
    <div className="card">
      <h4 style={{ margin: '0 0 16px 0', fontWeight: 600 }}>{title}</h4>
      <table className="breakdown-table">
        <thead>
          <tr>
            <th>Category</th>
            <th>Count</th>
            <th>Percentage</th>
          </tr>
        </thead>
        <tbody>
          {entries.map(([key, count]) => (
            <tr key={key}>
              <td style={{ textTransform: 'capitalize' }}>{key || 'Unknown'}</td>
              <td>{count}</td>
              <td>{total > 0 ? `${Math.round((count / total) * 100)}%` : '0%'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
