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
