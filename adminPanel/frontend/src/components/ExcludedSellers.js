import { useState, useEffect } from 'react';
import { getExcludedSellers, addExcludedSeller, removeExcludedSeller, runScheduler } from '../api/products';

function ExcludedSellers({ isOpen, onClose, onRefresh }) {
  const [sellers, setSellers] = useState([]);
  const [newSeller, setNewSeller] = useState('');
  const [reason, setReason] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) loadSellers();
  }, [isOpen]);

  const loadSellers = async () => {
    try {
      const data = await getExcludedSellers();
      setSellers(data);
    } catch (err) {
      console.error('Failed to load sellers:', err);
    }
  };

  const handleAdd = async (e) => {
    e.preventDefault();
    if (!newSeller.trim()) return;
    setLoading(true);
    try {
      await addExcludedSeller(newSeller.trim(), reason || null);
      await runScheduler();
      setNewSeller('');
      setReason('');
      loadSellers();
      if (onRefresh) onRefresh();
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = async (sellerName) => {
    try {
      await removeExcludedSeller(sellerName);
      await runScheduler();
      loadSellers();
      if (onRefresh) onRefresh();
    } catch (err) {
      alert(err.message);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-lg max-w-md w-full mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Excluded Sellers</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700 text-2xl">&times;</button>
        </div>

        <form onSubmit={handleAdd} className="mb-4 p-3 bg-gray-50 rounded">
          <input
            type="text"
            placeholder="Seller name"
            value={newSeller}
            onChange={(e) => setNewSeller(e.target.value)}
            className="w-full px-3 py-2 border rounded mb-2"
          />
          <input
            type="text"
            placeholder="Reason (optional)"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            className="w-full px-3 py-2 border rounded mb-2"
          />
          <button
            type="submit"
            disabled={loading || !newSeller.trim()}
            className="w-full bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 disabled:opacity-50"
          >
            {loading ? 'Adding...' : 'Exclude Seller'}
          </button>
        </form>

        <div className="max-h-64 overflow-y-auto">
          {sellers.length === 0 ? (
            <p className="text-gray-500 text-center py-4">No excluded sellers</p>
          ) : (
            <ul className="divide-y">
              {sellers.map((seller) => (
                <li key={seller.id} className="py-2 flex justify-between items-center">
                  <div>
                    <span className="font-medium">{seller.seller_name}</span>
                    {seller.reason && (
                      <p className="text-sm text-gray-500">{seller.reason}</p>
                    )}
                  </div>
                  <button
                    onClick={() => handleRemove(seller.seller_name)}
                    className="text-sm text-red-500 hover:text-red-700"
                  >
                    Remove
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}

export default ExcludedSellers;
