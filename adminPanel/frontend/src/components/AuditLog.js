import { useState, useEffect } from 'react';
import { getAuditLogs } from '../api/products';

function AuditLog({ isOpen, onClose, productId }) {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && productId) loadLogs();
  }, [isOpen, productId]);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const data = await getAuditLogs(productId, 50);
      setLogs(data);
    } catch (err) {
      console.error('Failed to load audit logs:', err);
    } finally {
      setLoading(false);
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
          <h2 className="text-xl font-bold">Audit Log</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700 text-2xl">&times;</button>
        </div>

        {loading ? (
          <p className="text-center py-4">Loading...</p>
        ) : logs.length === 0 ? (
          <p className="text-gray-500 text-center py-4">No audit logs yet</p>
        ) : (
          <div className="space-y-3">
            {logs.map((log) => (
              <div key={log.id} className="p-3 bg-gray-50 rounded border">
                <div className="flex justify-between items-start mb-1">
                  <span className={`px-2 py-1 text-xs rounded ${
                    log.action.includes('approved') ? 'bg-green-100 text-green-800' :
                    log.action.includes('suggestion') ? 'bg-yellow-100 text-yellow-800' :
                    'bg-blue-100 text-blue-800'
                  }`}>
                    {log.action}
                  </span>
                  <span className="text-xs text-gray-500">{formatDate(log.timestamp)}</span>
                </div>
                <p className="text-sm">{log.reason}</p>
                {log.old_value !== null && log.new_value !== null && (
                  <p className="text-xs text-gray-500 mt-1">
                    €{log.old_value?.toFixed(2)} → €{log.new_value?.toFixed(2)}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default AuditLog;
