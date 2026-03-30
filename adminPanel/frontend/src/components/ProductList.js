import { useState, useEffect } from 'react';
import { getProducts, addProduct, updateProduct, updateProductPrice, deleteProduct, runScheduler, getSchedulerStatus, getPriceHistory, getPendingSuggestions } from '../api/products';
import ProductCard from './ProductCard';
import ProductFormModal from './ProductFormModal';
import PriceHistory from './PriceHistory';
import ExcludedSellers from './ExcludedSellers';
import AuditLog from './AuditLog';
import Suggestions from './Suggestions';

const initialFormData = {
  name: '',
  idealo_link: '',
  quantity: 0,
  cost_per_unit: '',
  description: '',
  image_data: [],
  update_interval_hours: 24,
  minimum_margin: '',
  manual_sell_price: ''
};

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
  const [showExcludedSellers, setShowExcludedSellers] = useState(false);
  const [selectedAuditProduct, setSelectedAuditProduct] = useState(null);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [suggestionCount, setSuggestionCount] = useState(0);
  
  const [formData, setFormData] = useState(initialFormData);

  useEffect(() => {
    loadProducts();
    loadSchedulerStatus();
    loadSuggestionCount();
    const interval = setInterval(loadSchedulerStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadSuggestionCount = async () => {
    try {
      const suggestions = await getPendingSuggestions();
      setSuggestionCount(suggestions.length);
    } catch (err) {
      console.error('Failed to load suggestion count');
    }
  };

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
      
      setFormData(initialFormData);
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
    setFormData(initialFormData);
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

  const handleViewAudit = (productId) => {
    setSelectedAuditProduct(productId);
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

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">Products</h1>
          <div className="flex gap-2">
            <button
              onClick={() => setShowSuggestions(true)}
              className="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600 transition relative"
            >
              Suggestions
              {suggestionCount > 0 && (
                <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                  {suggestionCount}
                </span>
              )}
            </button>
            <button
              onClick={() => setShowExcludedSellers(true)}
              className="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600 transition"
            >
              Excluded Sellers
            </button>
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

        <ProductFormModal
          isOpen={showForm}
          onClose={handleCancel}
          onSubmit={handleSubmit}
          editingProduct={editingId}
          formData={formData}
          setFormData={setFormData}
          error={error}
        />

        <PriceHistory
          isOpen={!!selectedHistory}
          onClose={closeHistory}
          productName={historyProductName}
          priceHistory={priceHistory}
        />

        <ExcludedSellers
          isOpen={showExcludedSellers}
          onClose={() => setShowExcludedSellers(false)}
        />

        <AuditLog
          isOpen={!!selectedAuditProduct}
          onClose={() => setSelectedAuditProduct(null)}
          productId={selectedAuditProduct}
        />

        <Suggestions
          isOpen={showSuggestions}
          onClose={() => { setShowSuggestions(false); loadProducts(); }}
          onRefresh={loadProducts}
        />

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              currentImageIndex={currentImageIndex[product.id]}
              onPrevImage={prevImage}
              onNextImage={nextImage}
              onUpdatePrice={handleUpdatePrice}
              onViewHistory={handleViewHistory}
              onViewAudit={handleViewAudit}
              onEdit={handleEdit}
              onDelete={handleDelete}
              loadingPrice={loadingPrice}
            />
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
