import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

function PriceHistory({ isOpen, onClose, productName, priceHistory }) {
  if (!isOpen) return null;

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Never';
    const date = new Date(dateStr);
    return date.toLocaleString();
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-lg max-w-4xl w-full mx-4 max-h-[85vh] overflow-y-auto flex flex-col">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="text-xl font-bold">Price History</h2>
            <p className="text-sm text-gray-500">{productName}</p>
          </div>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700 text-2xl">&times;</button>
        </div>
        {priceHistory.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No price history available</p>
        ) : (
          <>
            <div className="mb-4">
              <LineChart width={750} height={256} data={[...priceHistory].reverse()} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis 
                  dataKey="timestamp" 
                  tickFormatter={(str) => {
                    const date = new Date(str);
                    return `${date.getDate()}.${date.getMonth() + 1}. ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
                  }}
                  stroke="#6b7280"
                  fontSize={12}
                />
                <YAxis 
                  domain={['auto', 'auto']}
                  tickFormatter={(value) => `€${value}`}
                  stroke="#6b7280"
                  fontSize={12}
                />
                <Tooltip 
                  formatter={(value) => [`€${value.toFixed(2)}`, 'Price']}
                  labelFormatter={(label) => formatDate(label)}
                />
                <Line 
                  type="monotone" 
                  dataKey="price" 
                  stroke="#3b82f6" 
                  strokeWidth={2}
                  dot={{ fill: '#3b82f6', strokeWidth: 2 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </div>
            <div className="h-48 overflow-y-auto border-t pt-4">
              <table className="min-w-full">
                <thead className="sticky top-0 bg-white">
                  <tr className="text-left text-sm text-gray-500">
                    <th className="pb-2">Price</th>
                    <th className="pb-2">Seller</th>
                    <th className="pb-2">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {priceHistory.map((entry) => (
                    <tr key={entry.id} className="border-t">
                      <td className="py-2">€{entry.price.toFixed(2)}</td>
                      <td className="py-2 text-sm">{entry.seller || '-'}</td>
                      <td className="py-2 text-sm">{formatDate(entry.timestamp)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default PriceHistory;
