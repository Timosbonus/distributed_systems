import { useState, useEffect } from 'react';
import { getProducts, addProduct, updateProduct, updateProductPrice, deleteProduct, runScheduler, getSchedulerStatus, getPriceHistory } from '../api/products';

const MAX_IMAGES = 5;

function ProductList() {
  const [products, setProducts] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState('');
  const [loadingPrice, setLoadingPrice] = useState(null);
  const [currentImageIndex, setCurrentImageIndex] = useState({});
  const [schedulerRunning, setSchedulerRunning] = useState(false);
  const [schedulerStatus, setSchedulerStatus] = useState(null);
  const [selectedHistory, setSelectedHistory] = useState(null);
  const [priceHistory, setPriceHistory] = useState([]);
  const [historyProductName, setHistoryProductName] = useState('');
  
  const [formData, setFormData] = useState({
    name: '',
    idealo_link: '',
    quantity: 0,
    cost_per_unit: '',
    description: '',
    image_data: [],
    update_interval_hours: 24,
    minimum_margin: '',
    manual_sell_price: ''
  });

  useEffect(() => {
    loadProducts();
    loadSchedulerStatus();
    const interval = setInterval(loadSchedulerStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadProducts = async () => {
    try {
      const data = await getProducts();
      setProducts(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const loadSchedulerStatus = async () => {
    try {
      const status = await getSchedulerStatus();
      setSchedulerStatus(status);
    } catch (err) {
      console.error('Failed to load scheduler status');
    }
  };

  const handleRunScheduler = async () => {
    setSchedulerRunning(true);
    setError('');
    try {
      const result = await runScheduler();
      loadProducts();
      loadSchedulerStatus();
      alert(`Updated ${result.updated.length} products${result.failed.length > 0 ? `, ${result.failed.length} failed` : ''}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setSchedulerRunning(false);
    }
  };

  const handleImageUpload = (e) => {
    const files = Array.from(e.target.files);
    if (formData.image_data.length + files.length > MAX_IMAGES) {
      setError(`Maximum ${MAX_IMAGES} images allowed`);
      return;
    }

    const newImages = [];
    let loadedCount = 0;

    files.forEach((file) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        newImages.push(reader.result);
        loadedCount++;
        if (loadedCount === files.length) {
          setFormData({ ...formData, image_data: [...formData.image_data, ...newImages] });
        }
      };
      reader.readAsDataURL(file);
    });
  };

  const removeImage = (index) => {
    const newImages = formData.image_data.filter((_, i) => i !== index);
    setFormData({ ...formData, image_data: newImages });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const productData = {
        name: formData.name,
        idealo_link: formData.idealo_link,
        quantity: formData.quantity || 0,
        description: formData.description || null,
        image_data: formData.image_data || null,
        update_interval_hours: formData.update_interval_hours || 24,
        cost_per_unit: formData.cost_per_unit ? parseFloat(formData.cost_per_unit) : null,
        minimum_margin: formData.minimum_margin ? parseFloat(formData.minimum_margin) : null,
        manual_sell_price: formData.manual_sell_price ? parseFloat(formData.manual_sell_price) : null
      };
      
      if (editingId) {
        await updateProduct(editingId, productData);
        setEditingId(null);
      } else {
        await addProduct(productData);
      }
      
      setFormData({ name: '', idealo_link: '', quantity: 0, cost_per_unit: '', description: '', image_data: [], update_interval_hours: 24, minimum_margin: '', manual_sell_price: '' });
      setShowForm(false);
      loadProducts();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleEdit = (product) => {
    setEditingId(product.id);
    setFormData({
      name: product.name,
      idealo_link: product.idealo_link,
      quantity: product.quantity,
      cost_per_unit: product.cost_per_unit || '',
      description: product.description || '',
      image_data: product.image_data || [],
      update_interval_hours: product.update_interval_hours || 24,
      minimum_margin: product.minimum_margin || '',
      manual_sell_price: product.manual_sell_price || ''
    });
    setShowForm(true);
  };

  const handleCancel = () => {
    setEditingId(null);
    setFormData({ name: '', idealo_link: '', quantity: 0, cost_per_unit: '', description: '', image_data: [], update_interval_hours: 24, minimum_margin: '', manual_sell_price: '' });
    setShowForm(false);
  };

  const handleUpdatePrice = async (productId) => {
    setLoadingPrice(productId);
    setError('');
    try {
      await updateProductPrice(productId);
      loadProducts();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingPrice(null);
    }
  };

  const handleDelete = async (productId) => {
    if (!window.confirm('Are you sure you want to delete this product?')) {
      return;
    }
    setError('');
    try {
      await deleteProduct(productId);
      loadProducts();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleViewHistory = async (product) => {
    try {
      const history = await getPriceHistory(product.id, 10);
      setPriceHistory(history);
      setSelectedHistory(product.id);
      setHistoryProductName(product.name);
    } catch (err) {
      setError(err.message);
    }
  };

  const closeHistory = () => {
    setSelectedHistory(null);
    setPriceHistory([]);
    setHistoryProductName('');
  };

  const nextImage = (productId, images) => {
    setCurrentImageIndex(prev => ({
      ...prev,
      [productId]: ((prev[productId] || 0) + 1) % images.length
    }));
  };

  const prevImage = (productId, images) => {
    setCurrentImageIndex(prev => ({
      ...prev,
      [productId]: ((prev[productId] || 0) - 1 + images.length) % images.length
    }));
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Never';
    const date = new Date(dateStr);
    return date.toLocaleString();
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">Products</h1>
          <div className="flex gap-2">
            <button
              onClick={handleRunScheduler}
              disabled={schedulerRunning}
              className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 transition disabled:opacity-50"
            >
              {schedulerRunning ? 'Updating...' : 'Run Scheduler'}
            </button>
            <button
              onClick={() => setShowForm(!showForm)}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition"
            >
              {showForm ? 'Cancel' : (editingId ? 'Cancel Edit' : 'Add Product')}
            </button>
          </div>
        </div>

        {schedulerStatus && schedulerStatus.products_needing_update > 0 && (
          <div className="mb-4 p-3 rounded bg-yellow-100 text-yellow-700">
            {schedulerStatus.products_needing_update} product(s) need price updates
          </div>
        )}

        {error && (
          <div className="mb-4 p-3 rounded bg-red-100 text-red-700">
            {error}
          </div>
        )}

        {showForm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-hidden">
              <div className="flex justify-between items-center p-4 border-b">
                <h2 className="text-xl font-bold">{editingId ? 'Edit Product' : 'Add New Product'}</h2>
                <button onClick={handleCancel} className="text-gray-500 hover:text-gray-700 text-2xl">&times;</button>
              </div>
              <div className="p-6 overflow-y-auto max-h-[calc(90vh-80px)]">
                <form onSubmit={handleSubmit}>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="mb-4">
                      <label className="block text-gray-700 text-sm font-bold mb-2">
                        Product Name
                      </label>
                      <input
                        type="text"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      />
                    </div>
                    
                    <div className="mb-4">
                      <label className="block text-gray-700 text-sm font-bold mb-2">
                        Idealo Link
                      </label>
                      <input
                        type="url"
                        value={formData.idealo_link}
                        onChange={(e) => setFormData({ ...formData, idealo_link: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      />
                    </div>

                    <div className="mb-4">
                      <label className="block text-gray-700 text-sm font-bold mb-2">
                        Quantity
                      </label>
                      <input
                        type="number"
                        value={formData.quantity}
                        onChange={(e) => setFormData({ ...formData, quantity: parseInt(e.target.value) || 0 })}
                        className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>

                    <div className="mb-4">
                      <label className="block text-gray-700 text-sm font-bold mb-2">
                        Cost per Unit
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        value={formData.cost_per_unit}
                        onChange={(e) => setFormData({ ...formData, cost_per_unit: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>

                    <div className="mb-4">
                      <label className="block text-gray-700 text-sm font-bold mb-2">
                        Update Interval (hours)
                      </label>
                      <input
                        type="number"
                        min="1"
                        value={formData.update_interval_hours}
                        onChange={(e) => setFormData({ ...formData, update_interval_hours: parseInt(e.target.value) || 24 })}
                        className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>

                    <div className="mb-4">
                      <label className="block text-gray-700 text-sm font-bold mb-2">
                        Minimum Margin (%)
                      </label>
                      <input
                        type="number"
                        min="0"
                        step="0.1"
                        value={formData.minimum_margin || ''}
                        onChange={(e) => setFormData({ ...formData, minimum_margin: e.target.value ? parseFloat(e.target.value) : null })}
                        className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="e.g. 10"
                      />
                    </div>

                    <div className="mb-4 col-span-2">
                      <label className="block text-gray-700 text-sm font-bold mb-2">
                        Manual Sell Price (overrides auto-calculated)
                      </label>
                      <div className="flex gap-2">
                        <input
                          type="number"
                          step="0.01"
                          value={formData.manual_sell_price || ''}
                          onChange={(e) => setFormData({ ...formData, manual_sell_price: e.target.value ? parseFloat(e.target.value) : null })}
                          className="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="Leave empty for auto-calculated"
                        />
                        {formData.manual_sell_price && (
                          <button
                            type="button"
                            onClick={() => setFormData({ ...formData, manual_sell_price: null })}
                            className="px-3 py-2 bg-red-500 text-white rounded hover:bg-red-600"
                          >
                            Clear
                          </button>
                        )}
                      </div>
                    </div>

                    <div className="mb-4 col-span-2">
                      <label className="block text-gray-700 text-sm font-bold mb-2">
                        Description
                      </label>
                      <textarea
                        value={formData.description}
                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        rows="2"
                      />
                    </div>

                    <div className="mb-4 col-span-2">
                      <label className="block text-gray-700 text-sm font-bold mb-2">
                        Product Images (max {MAX_IMAGES})
                      </label>
                      <input
                        type="file"
                        accept="image/*"
                        multiple
                        onChange={handleImageUpload}
                        className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        disabled={formData.image_data.length >= MAX_IMAGES}
                      />
                      {formData.image_data.length > 0 && (
                        <div className="mt-2 flex flex-wrap gap-2">
                          {formData.image_data.map((img, idx) => (
                            <div key={idx} className="relative">
                              <img src={img} alt={`Preview ${idx + 1}`} className="h-24 w-24 object-contain rounded border border-gray-200" />
                              <button
                                type="button"
                                onClick={() => removeImage(idx)}
                                className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 text-xs flex items-center justify-center"
                              >
                                ×
                              </button>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex gap-2 mt-4">
                    <button
                      type="submit"
                      className="flex-1 bg-green-500 text-white py-2 px-4 rounded hover:bg-green-600 transition"
                    >
                      {editingId ? 'Update Product' : 'Add Product'}
                    </button>
                    <button
                      type="button"
                      onClick={handleCancel}
                      className="bg-gray-500 text-white py-2 px-4 rounded hover:bg-gray-600 transition"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}

        {selectedHistory && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white p-6 rounded-lg shadow-lg max-w-md w-full mx-4">
              <div className="flex justify-between items-center mb-4">
                <div>
                  <h2 className="text-xl font-bold">Price History</h2>
                  <p className="text-sm text-gray-500">{historyProductName}</p>
                </div>
                <button onClick={closeHistory} className="text-gray-500 hover:text-gray-700 text-2xl">&times;</button>
              </div>
              <div className="max-h-80 overflow-y-auto">
                {priceHistory.length === 0 ? (
                  <p className="text-gray-500">No price history available</p>
                ) : (
                  <table className="min-w-full">
                    <thead>
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
                )}
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map((product) => (
            <div key={product.id} className="bg-white rounded-lg shadow-md overflow-hidden">
              {product.image_data && product.image_data.length > 0 ? (
                <div className="relative h-36 bg-gray-100">
                  <img 
                    src={product.image_data[currentImageIndex[product.id] || 0]} 
                    alt={product.name} 
                    className="w-full h-full object-contain"
                  />
                  {product.image_data.length > 1 && (
                    <>
                      <button
                        onClick={() => prevImage(product.id, product.image_data)}
                        className="absolute left-2 top-1/2 -translate-y-1/2 bg-black/50 text-white rounded-full w-8 h-8 flex items-center justify-center hover:bg-black/70"
                      >
                        ‹
                      </button>
                      <button
                        onClick={() => nextImage(product.id, product.image_data)}
                        className="absolute right-2 top-1/2 -translate-y-1/2 bg-black/50 text-white rounded-full w-8 h-8 flex items-center justify-center hover:bg-black/70"
                      >
                        ›
                      </button>
                      <div className="absolute bottom-2 left-1/2 -translate-x-1/2 bg-black/50 text-white text-xs px-2 py-1 rounded">
                        {((currentImageIndex[product.id] || 0) + 1)} / {product.image_data.length}
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

                <div className="mt-4 flex gap-2 flex-wrap">
                  <button
                    onClick={() => handleUpdatePrice(product.id)}
                    disabled={loadingPrice === product.id}
                    className="flex-1 bg-yellow-500 text-white py-2 px-3 rounded hover:bg-yellow-600 transition disabled:opacity-50 text-sm"
                  >
                    Update Price
                  </button>
                  <button
                    onClick={() => handleViewHistory(product)}
                    className="bg-purple-500 text-white py-2 px-3 rounded hover:bg-purple-600 transition text-sm"
                  >
                    History
                  </button>
                  <button
                    onClick={() => handleEdit(product)}
                    className="bg-blue-500 text-white py-2 px-3 rounded hover:bg-blue-600 transition text-sm"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(product.id)}
                    className="bg-red-500 text-white py-2 px-3 rounded hover:bg-red-600 transition text-sm"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
          {products.length === 0 && (
            <div className="col-span-full text-center py-12 text-gray-500">
              No products yet. Click "Add Product" to get started.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ProductList;
