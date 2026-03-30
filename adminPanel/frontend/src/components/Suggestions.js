import { useState, useEffect } from 'react';
import { getPendingSuggestions, approveSuggestion, rejectSuggestion } from '../api/products';

function Suggestions({ isOpen, onClose, onRefresh }) {
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) loadSuggestions();
  }, [isOpen]);

  const loadSuggestions = async () => {
    setLoading(true);
    try {
      const data = await getPendingSuggestions();
      setSuggestions(data);
    } catch (err) {
      console.error('Failed to load suggestions:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id) => {
    try {
      await approveSuggestion(id);
      loadSuggestions();
      if (onRefresh) onRefresh();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleReject = async (id) => {
    try {
      await rejectSuggestion(id);
      loadSuggestions();
    } catch (err) {
      alert(err.message);
    }
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleString();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-lg max-w-2xl w-full mx-4 max-h-[85vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Price Change Suggestions</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700 text-2xl">&times;</button>
        </div>

        {loading ? (
          <p className="text-center py-4">Loading...</p>
        ) : suggestions.length === 0 ? (
          <p className="text-gray-500 text-center py-4">No pending suggestions</p>
        ) : (
          <div className="space-y-3">
            {suggestions.map((s) => (
              <div key={s.id} className="p-4 bg-yellow-50 rounded border border-yellow-200">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <span className="font-medium">{s.product_name}</span>
                    <p className="text-sm text-gray-600">
                      {s.competitor_name} lowered to €{s.competitor_price?.toFixed(2)}
                    </p>
                  </div>
                  <span className="text-sm text-yellow-700 font-medium">
                    {s.percentage_change?.toFixed(1)}% change
                  </span>
                </div>
                <div className="flex items-center gap-2 text-sm mb-3">
                  <span className="line-through text-gray-500">€{s.current_price?.toFixed(2)}</span>
                  <span className="text-lg font-bold text-green-600">€{s.suggested_price?.toFixed(2)}</span>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleApprove(s.id)}
                    className="flex-1 bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
                  >
                    Approve
                  </button>
                  <button
                    onClick={() => handleReject(s.id)}
                    className="flex-1 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
                  >
                    Reject
                  </button>
                </div>
                <p className="text-xs text-gray-500 mt-2">{formatDate(s.created_at)}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Suggestions;
