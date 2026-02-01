import { useState } from 'react';

interface SearchFormProps {
  onSearch: (text: string, k: number) => void;
  isLoading: boolean;
}

export function SearchForm({ onSearch, isLoading }: SearchFormProps) {
  const [text, setText] = useState('');
  const [k, setK] = useState(5);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (text.trim()) {
      onSearch(text.trim(), k);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="card">
      <div className="form-group">
        <label className="form-label" htmlFor="search-text">
          Search Query
        </label>
        <input
          type="text"
          id="search-text"
          name="search-text"
          className="bpk-input"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="e.g., business class tips, lounge access..."
          disabled={isLoading}
        />
      </div>
      <div className="form-row">
        <div className="form-group" style={{ width: '120px' }}>
          <label className="form-label" htmlFor="k-value">
            Results (k)
          </label>
          <select
            id="k-value"
            name="k-value"
            className="bpk-select"
            value={String(k)}
            onChange={(e) => setK(Number(e.target.value))}
            disabled={isLoading}
          >
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
              <option key={n} value={n}>
                {n}
              </option>
            ))}
          </select>
        </div>
        <button type="submit" className="bpk-button" disabled={isLoading || !text.trim()}>
          {isLoading ? 'Searching...' : 'Search'}
        </button>
      </div>
    </form>
  );
}
