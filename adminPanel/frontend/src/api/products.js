const API_URL = 'http://localhost:8000';

export const getProducts = async () => {
  const response = await fetch(`${API_URL}/products`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch products');
  }
  
  return response.json();
};

export const addProduct = async (productData) => {
  const response = await fetch(`${API_URL}/products`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(productData),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Failed to add product');
  }

  return data;
};

export const updateProduct = async (productId, productData) => {
  const response = await fetch(`${API_URL}/products/${productId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(productData),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Failed to update product');
  }

  return data;
};

export const updateProductPrice = async (productId) => {
  const response = await fetch(`${API_URL}/products/${productId}/update-price`, {
    method: 'POST',
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Failed to update price');
  }

  return data;
};

export const deleteProduct = async (productId) => {
  const response = await fetch(`${API_URL}/products/${productId}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.detail || 'Failed to delete product');
  }

  return true;
};

export const getPriceHistory = async (productId, limit = 10) => {
  const response = await fetch(`${API_URL}/products/${productId}/history?limit=${limit}`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch price history');
  }
  
  return response.json();
};

export const runScheduler = async () => {
  const response = await fetch(`${API_URL}/scheduler/run`, {
    method: 'POST',
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Failed to run scheduler');
  }

  return data;
};

export const getSchedulerStatus = async () => {
  const response = await fetch(`${API_URL}/scheduler/status`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch scheduler status');
  }
  
  return response.json();
};

export const getExcludedSellers = async () => {
  const response = await fetch(`${API_URL}/sellers/excluded`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch excluded sellers');
  }
  
  return response.json();
};

export const addExcludedSeller = async (sellerName, reason = null) => {
  const response = await fetch(`${API_URL}/sellers/excluded`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ seller_name: sellerName, reason }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Failed to add excluded seller');
  }

  return data;
};

export const removeExcludedSeller = async (sellerName) => {
  const response = await fetch(`${API_URL}/sellers/excluded/${sellerName}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.detail || 'Failed to remove excluded seller');
  }

  return true;
};

export const getAuditLogs = async (productId, limit = 50) => {
  const response = await fetch(`${API_URL}/audit/products/${productId}?limit=${limit}`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch audit logs');
  }
  
  return response.json();
};

export const getPendingSuggestions = async () => {
  const response = await fetch(`${API_URL}/pricing/suggestions`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch suggestions');
  }
  
  return response.json();
};

export const approveSuggestion = async (suggestionId) => {
  const response = await fetch(`${API_URL}/pricing/suggestions/${suggestionId}/approve`, {
    method: 'POST',
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Failed to approve suggestion');
  }

  return data;
};

export const rejectSuggestion = async (suggestionId) => {
  const response = await fetch(`${API_URL}/pricing/suggestions/${suggestionId}/reject`, {
    method: 'POST',
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Failed to reject suggestion');
  }

  return data;
};
