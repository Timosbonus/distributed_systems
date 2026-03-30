function ProductCard({ product, currentImageIndex, onPrevImage, onNextImage, onUpdatePrice, onViewHistory, onViewAudit, onEdit, onDelete, loadingPrice }) {
  const formatDate = (dateStr) => {
    if (!dateStr) return 'Never';
    const date = new Date(dateStr);
    return date.toLocaleString();
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      {product.image_data && product.image_data.length > 0 ? (
        <div className="relative h-36 bg-gray-100">
          <img 
            src={product.image_data[currentImageIndex || 0]} 
            alt={product.name} 
            className="w-full h-full object-contain"
          />
          {product.image_data.length > 1 && (
            <>
              <button
                onClick={() => onPrevImage(product.id, product.image_data)}
                className="absolute left-2 top-1/2 -translate-y-1/2 bg-black/50 text-white rounded-full w-8 h-8 flex items-center justify-center hover:bg-black/70"
              >
                ‹
              </button>
              <button
                onClick={() => onNextImage(product.id, product.image_data)}
                className="absolute right-2 top-1/2 -translate-y-1/2 bg-black/50 text-white rounded-full w-8 h-8 flex items-center justify-center hover:bg-black/70"
              >
                ›
              </button>
              <div className="absolute bottom-2 left-1/2 -translate-x-1/2 bg-black/50 text-white text-xs px-2 py-1 rounded">
                {((currentImageIndex || 0) + 1)} / {product.image_data.length}
              </div>
            </>
          )}
        </div>
      ) : (
        <div className="h-36 bg-gray-100 flex items-center justify-center">
          <span className="text-gray-400">No image</span>
        </div>
      )}
      <div className="p-4">
        <h3 className="text-lg font-bold text-gray-900">{product.name}</h3>
        <p className="text-sm text-gray-500 truncate mt-1">{product.idealo_link}</p>
        
        <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
          <div>
            <span className="text-gray-500">Quantity:</span>
            <span className="ml-1 font-medium">{product.quantity}</span>
          </div>
          <div>
            <span className="text-gray-500">Cost/Unit:</span>
            <span className="ml-1 font-medium">{product.cost_per_unit ? `€${product.cost_per_unit.toFixed(2)}` : '-'}</span>
          </div>
          <div className="col-span-2">
            <span className="text-gray-500">Lowest Price:</span>
            <span className="ml-1 font-medium text-green-600">
              {loadingPrice === product.id ? 'Updating...' : (product.lowest_price ? `€${product.lowest_price.toFixed(2)}` : '-')}
            </span>
            {product.lowest_seller && (
              <span className="ml-1 text-xs text-gray-500">({product.lowest_seller})</span>
            )}
          </div>
          <div>
            <span className="text-gray-500">Sell Price:</span>
            <span className="ml-1 font-medium text-blue-600">
              {product.sell_price ? `€${product.sell_price.toFixed(2)}` : '-'}
            </span>
            {product.manual_sell_price && (
              <span className="ml-1 text-xs text-green-600">(manual)</span>
            )}
          </div>
          <div>
            <span className="text-gray-500">Interval:</span>
            <span className="ml-1 font-medium">{product.update_interval_hours}h</span>
          </div>
          {product.minimum_margin !== null && product.minimum_margin !== undefined && (
            <div>
              <span className="text-gray-500">Min Margin:</span>
              <span className="ml-1 font-medium">{product.minimum_margin}%</span>
            </div>
          )}
          <div className="col-span-2">
            <span className="text-gray-500">Last Update:</span>
            <span className="ml-1 text-xs">{formatDate(product.last_price_update)}</span>
          </div>
        </div>

        {product.description && (
          <p className="mt-2 text-sm text-gray-600 line-clamp-2">{product.description}</p>
        )}

        <div className="mt-4 flex gap-1 justify-between">
          <button
            onClick={() => onUpdatePrice(product.id)}
            disabled={loadingPrice === product.id}
            className="bg-yellow-500 text-white py-2 px-2 rounded hover:bg-yellow-600 transition disabled:opacity-50 text-xs font-medium flex-1"
          >
            Update
          </button>
          <button
            onClick={() => onViewHistory(product)}
            className="bg-purple-500 text-white py-2 px-2 rounded hover:bg-purple-600 transition text-xs font-medium"
          >
            History
          </button>
          <button
            onClick={() => onViewAudit(product.id)}
            className="bg-gray-500 text-white py-2 px-2 rounded hover:bg-gray-600 transition text-xs font-medium"
          >
            Audit
          </button>
          <button
            onClick={() => onEdit(product)}
            className="bg-blue-500 text-white py-2 px-2 rounded hover:bg-blue-600 transition text-xs font-medium"
          >
            Edit
          </button>
          <button
            onClick={() => onDelete(product.id)}
            className="bg-red-500 text-white py-2 px-2 rounded hover:bg-red-600 transition text-xs font-medium"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}

export default ProductCard;
